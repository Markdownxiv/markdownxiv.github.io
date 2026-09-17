"""Small bounded GitHub REST client. No arbitrary hosts, redirects, or shell."""
import base64
import contextlib
import hashlib
import json
import re
import signal
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from .codec import MAX_PAPER, decimal, fields
from .errors import Rejection, require


def repository_name(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]{1,100}", value),
            "invalid_repository", "Expected a GitHub owner/repository name.")
    require(value.split("/")[1] not in (".", ".."), "invalid_repository", "Invalid repository name.")
    return value


def validate_source(source, image=False):
    fields(source, ["kind", "repository", "commit", "path"])
    require(source["kind"] == "github", "invalid_source", "Expected a GitHub source.")
    repository_name(source["repository"])
    require(isinstance(source["commit"], str) and re.fullmatch(r"[0-9a-f]{40}", source["commit"]),
            "mutable_ref", "Source must use a full lowercase 40-hex commit SHA.")
    path = source["path"]
    require(isinstance(path, str) and 1 <= len(path) <= 240 and
            re.fullmatch(r"[A-Za-z0-9_./-]+", path) and
            all(p not in ("", ".", "..") for p in path.split("/")) and
            len(path.split("/")) <= 12 and path.lower().endswith((".png", ".jpg", ".jpeg", ".webp") if image else (".md", ".markdown")),
            "unsafe_path", "Source path must name one bounded Markdown file without traversal.")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Rejection("redirect_forbidden", "Redirects are not followed.")


@contextlib.contextmanager
def wall_timeout(seconds):
    """An absolute main-thread timer also interrupts a slowly dripping socket read."""
    require(threading.current_thread() is threading.main_thread(), "network_context",
            "The bounded GitHub client must run in the main thread on Linux/WSL.")
    def expired(*_):
        raise Rejection("network_timeout", "GitHub request exceeded its absolute wall deadline.", True)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    previous_handler = signal.signal(signal.SIGALRM, expired)
    # Nested source/request deadlines must never extend the outer bundle budget.
    effective = min(seconds, previous_timer[0]) if previous_timer[0] > 0 else seconds
    signal.setitimer(signal.ITIMER_REAL, max(0.001, effective))
    start = time.monotonic()
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, max(0.001, previous_timer[0] - (time.monotonic() - start)), previous_timer[1])


def bounded_read(response, limit, deadline):
    length = response.headers.get("Content-Length")
    if length:
        require(length.isdigit() and int(length) <= limit, "download_limit", "Remote object exceeds byte limit.")
    parts, size = [], 0
    while True:
        if time.monotonic() > deadline:
            raise Rejection("network_timeout", "Remote read exceeded time limit.", True)
        chunk = response.read(min(16384, limit + 1 - size))
        if not chunk:
            return b"".join(parts)
        parts.append(chunk)
        size += len(chunk)
        require(size <= limit, "download_limit", "Remote object exceeds byte limit.")


class GitHub:
    def __init__(self, token=None, opener=None):
        self.token = token
        self.opener = opener or urllib.request.build_opener(NoRedirect())
        self.source_cache = {}

    def request(self, method, path, data=None, limit=4_000_000, deadline=None):
        require(path.startswith("/") and not path.startswith("//") and "\r" not in path and "\n" not in path,
                "invalid_api_path", "Invalid GitHub API path.")
        deadline = deadline or time.monotonic() + 25
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise Rejection("network_timeout", "Remote read exceeded time limit.", True)
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "agent-preprints-v1"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        payload = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
        if payload is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request("https://api.github.com" + path, data=payload, headers=headers, method=method)
        try:
            with wall_timeout(remaining):
                with self.opener.open(request, timeout=min(10, remaining)) as response:
                    raw = bounded_read(response, limit, deadline)
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise Rejection("github_not_found", "GitHub resource is unavailable.") from exc
            if exc.code in (403, 408, 409, 429) or exc.code >= 500:
                raise Rejection("github_temporary", "GitHub refused or deferred the request; retry later.", True) from exc
            raise Rejection("github_request_failed", "GitHub API rejected the request.") from exc
        except (OSError, ValueError, TimeoutError) as exc:
            raise Rejection("network_error", "GitHub response could not be read safely.", True) from exc

    def repository(self, name):
        return self.request("GET", "/repos/" + repository_name(name))

    def fetch_paper(self, source):
        return self.fetch_file(source, MAX_PAPER)

    def fetch_paper_v2(self, source):
        from .assets import MAX_PAPER as cap
        return self.fetch_file(source, cap)

    def fetch_asset(self, source):
        from .assets import MAX_IMAGE
        return self.fetch_file(source, MAX_IMAGE, image=True)

    def fetch_file(self, source, cap, image=False):
        validate_source(source, image)
        deadline = time.monotonic() + 30
        prefix = "/repos/" + source["repository"]
        def cached(path):
            if path not in self.source_cache:
                # Keep memory bounded; this cache is only an API optimization.
                if len(self.source_cache) >= 32:
                    self.source_cache.clear()
                self.source_cache[path] = self.request("GET", path, deadline=deadline)
            return self.source_cache[path]
        repo = cached(prefix)
        require(repo.get("private") is False and repo.get("visibility", "public") == "public",
                "private_source", "Body source must be a public repository.")
        commit = cached(prefix + "/git/commits/" + source["commit"])
        require(commit.get("sha") == source["commit"], "source_mismatch", "Commit response mismatch.")
        tree_sha = commit["tree"]["sha"]
        components = source["path"].split("/")
        for index, component in enumerate(components):
            require(re.fullmatch(r"[0-9a-f]{40}", tree_sha), "source_mismatch", "Invalid tree object.")
            tree = cached(prefix + "/git/trees/" + tree_sha)
            require(not tree.get("truncated"), "download_limit", "Truncated trees are unsupported.")
            matches = [e for e in tree["tree"] if e["path"] == component]
            require(len(matches) == 1, "source_missing", "Markdown file was not found at this commit.")
            entry = matches[0]
            if index + 1 < len(components):
                require(entry["type"] == "tree" and entry["mode"] == "040000",
                        "unsafe_source", "Path traverses a symlink, submodule, or non-directory.")
                tree_sha = entry["sha"]
            else:
                require(entry["type"] == "blob" and entry["mode"] in ("100644", "100755"),
                        "unsafe_source", "Only ordinary files are accepted, never symlinks or submodules.")
                require(type(entry.get("size")) is int and 0 < entry["size"] <= cap,
                        "paper_limit", "Source file exceeds paper limit.")
        require(re.fullmatch(r"[0-9a-f]{40}", entry["sha"]), "source_mismatch", "Invalid blob object.")
        blob = self.request("GET", prefix + "/git/blobs/" + entry["sha"], limit=cap * 2, deadline=deadline)
        require(blob.get("encoding") == "base64" and blob.get("size") == entry["size"],
                "source_mismatch", "Blob size or encoding mismatch.")
        try:
            body = base64.b64decode(blob["content"].replace("\n", ""), validate=True)
        except (ValueError, TypeError) as exc:
            raise Rejection("source_mismatch", "Invalid blob encoding.") from exc
        require(len(body) == entry["size"] and len(body) <= cap,
                "paper_limit", "Decoded blob size mismatch.")
        git_hash = hashlib.sha1(b"blob " + str(len(body)).encode("ascii") + b"\0" + body).hexdigest()
        require(git_hash == entry["sha"], "source_mismatch", "Git blob hash mismatch.")
        return body

    def issue(self, repository, number):
        decimal(str(number), 1)
        return self.request("GET", "/repos/" + repository_name(repository) + "/issues/" + str(number))

    def issues_page(self, repository, page):
        return self.request("GET", "/repos/" + repository_name(repository) +
                            "/issues?state=all&sort=created&direction=asc&per_page=100&page=" + str(page))

    def create_issue(self, repository, package_text, content_hash, title=None):
        return self.request("POST", "/repos/" + repository_name(repository) + "/issues",
                            {"title": "[preprint] " + (title[:230] if title else content_hash), "body": package_text})

    def comments(self, repository, number, page=1):
        return self.request("GET", "/repos/" + repository_name(repository) + "/issues/" + str(number) +
                            "/comments?per_page=100&page=" + str(page))
