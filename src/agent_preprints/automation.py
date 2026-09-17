"""Trusted Git transactions and PR receipts. Issues are for project feedback only."""
import base64
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from .archive import atomic_json
from .codec import canonical, decimal, loads, read_json, sha
from .errors import Rejection, require
from .github import GitHub, repository_name


class GitTransaction:
    """Fresh detached worktree per attempt; one ordinary fast-forward push per transaction.

    The workflow-level lock spans archive, build, deploy and receipt reconciliation.
    Non-fast-forward conflicts with human commits are handled by re-running the entire
    callback against the new tip, never by force pushing or merging stale data.
    """
    def __init__(self, checkout, branch, attempts=3):
        self.checkout = Path(checkout).resolve()
        self.branch = branch
        self.attempts = attempts
        self.git(self.checkout, "check-ref-format", "refs/heads/" + branch)

    def git(self, directory, *args, check=True):
        environment = os.environ.copy()
        token = environment.get("GITHUB_TOKEN")
        if token:
            # Ephemeral auth also works in detached worktrees. No credential files,
            # token-bearing command arguments, or checkout credential persistence.
            index = int(environment.get("GIT_CONFIG_COUNT", "0"))
            environment["GIT_CONFIG_COUNT"] = str(index + 1)
            environment[f"GIT_CONFIG_KEY_{index}"] = "http.https://github.com/.extraheader"
            environment[f"GIT_CONFIG_VALUE_{index}"] = "AUTHORIZATION: basic " + base64.b64encode(("x-access-token:" + token).encode()).decode()
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-C", str(directory), *args],
                                capture_output=True, text=True, timeout=60, env=environment)
        if check and result.returncode:
            raise Rejection("git_operation_failed", "Trusted Git operation failed; no forced update was attempted.", True)
        return result

    def run(self, mutation, before_push=None):
        for attempt in range(self.attempts):
            self.git(self.checkout, "fetch", "--no-tags", "origin", "refs/heads/" + self.branch)
            head = self.git(self.checkout, "rev-parse", "FETCH_HEAD").stdout.strip()
            with tempfile.TemporaryDirectory(prefix="preprints-transaction-") as temp:
                worktree = Path(temp) / "snapshot"
                self.git(self.checkout, "worktree", "add", "--detach", str(worktree), head)
                try:
                    result = mutation(worktree)
                    paths = [p for p in ("papers", "receipts", "challenges", "state", "works", "assets") if (worktree / p).exists()]
                    self.git(worktree, "add", "--all", "--", *paths)
                    staged = self.git(worktree, "diff", "--cached", "--name-only", "-z").stdout.split("\0")
                    allowed = re.compile(r"(?:papers/[0-9a-f]{64}/(?:paper\.md|metadata\.json|proof\.json)|"
                                         r"receipts/[0-9]+-(?:pr-)?[0-9]+\.json|challenges/(?:latest\.json|registry\.json|"
                                         r"epochs/(?:v[234]-)?\d{4}-\d{2}-\d{2}\.json)|state/(?:scan|published)\.json|"
                                         r"works/[0-9]{4}\.[0-9]{5,10}\.json|assets/[0-9a-f]{64}\.(?:png|jpg|webp))\Z")
                    require(all(not name or allowed.fullmatch(name) for name in staged),
                            "unsafe_write", "Transaction attempted to modify a non-data path.")
                    if any(staged):
                        self.git(worktree, "-c", "user.name=github-actions[bot]", "-c",
                                 "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                                 "-c", "commit.gpgsign=false", "commit", "-m", "Archive admission state and publication records")
                        if before_push:
                            before_push(attempt)
                        pushed = self.git(worktree, "push", "origin", "HEAD:refs/heads/" + self.branch, check=False)
                        if pushed.returncode:
                            # Retry even an ambiguous transport outcome: the next callback sees
                            # the sealed receipt if the previous push actually reached GitHub.
                            continue
                    committed = self.git(worktree, "rev-parse", "HEAD").stdout.strip()
                    return committed, result
                finally:
                    self.git(self.checkout, "worktree", "remove", "--force", str(worktree), check=False)
        raise Rejection("git_push_failed", "Archive push failed after three fresh-state attempts; maintenance can recover.", True)


COMMENT_RE = re.compile(r"<!-- agent-preprints:[0-9]+:[0-9]+ -->\n```json\n(.*)\n```\Z", re.S)
CARD_RE = re.compile(r"<!-- agent-preprints:[0-9]+:[0-9]+ -->\n.*\n<details>\n<summary>Machine-readable receipt</summary>\n\n```json\n([^\n]+)\n```\n</details>\Z", re.S)


def parse_comment(comment):
    user = comment.get("user", {})
    if user.get("login") != "github-actions[bot]" or user.get("type") != "Bot":
        return None
    match = COMMENT_RE.fullmatch(comment.get("body", "")) or CARD_RE.fullmatch(comment.get("body", ""))
    if not match:
        return None
    try:
        value = loads(match.group(1))
        if isinstance(value, dict) and value.get("receipt_version") in ("agent-preprints-receipt-v1", "agent-preprints-receipt-v2", "markdownxiv-receipt-v3"):
            return value
    except Rejection:
        pass
    return None


def upsert_comment(github, repository, record):
    snapshot = record["snapshot"]
    marker = "<!-- agent-preprints:" + snapshot["repository_id"] + ":" + snapshot["issue_id"] + " -->"
    from .envelope import receipt_body
    body = receipt_body(record)
    prefix = "/repos/" + repository_name(repository) + "/issues"
    comment_id = record["comment_id"]
    if comment_id is not None:
        decimal(comment_id, 1)
        try:
            existing = github.request("GET", prefix + "/comments/" + comment_id)
            require(parse_comment(existing) is not None and existing["body"].startswith(marker),
                    "comment_mismatch", "Saved comment does not belong to this receipt.")
        except Rejection as exc:
            if exc.code != "github_not_found":
                raise
            comment_id = None
    if comment_id is None:
        for page in range(1, 11):
            comments = github.comments(repository, snapshot["issue_number"], page)
            for comment in comments:
                if parse_comment(comment) is not None and comment["body"].startswith(marker):
                    comment_id = str(comment["id"])
                    break
            if comment_id or len(comments) < 100:
                break
    if comment_id:
        result = github.request("PATCH", prefix + "/comments/" + comment_id, {"body": body})
    else:
        result = github.request("POST", prefix + "/" + snapshot["issue_number"] + "/comments", {"body": body})
    return str(result["id"])


def sync_receipts(root, github, repository, limit=20):
    count = 0
    for path in sorted((Path(root) / "receipts").glob("*-pr-*.json")):
        record = read_json(path)
        require(record["snapshot"]["mode"] == "pull_request", "invalid_snapshot", "PR receipts require a PR snapshot.")
        from .envelope import receipt_body
        digest = sha(receipt_body(record).encode())
        needs_close = record["published"] and not record.get("pr_closed")
        if digest == record["comment_digest"] and not needs_close:
            continue
        if count >= limit:
            break
        count += 1
        try:
            record["comment_id"] = upsert_comment(github, repository, record)
            record["comment_digest"] = digest
            if needs_close:
                github.request("PATCH", "/repos/" + repository_name(repository) + "/pulls/" + record["snapshot"]["issue_number"], {"state": "closed"})
                record["pr_closed"] = True
            atomic_json(path, record)
        except Rejection as exc:
            print(canonical({"receipt_sync": "pending", "error_code": exc.code}).decode(), file=sys.stderr)


def _workflow_context():
    require(os.environ.get("GITHUB_ACTIONS") == "true", "trusted_context_required", "Automation entry points require GitHub Actions context.")
    repository = repository_name(os.environ["GITHUB_REPOSITORY"])
    repository_id = os.environ["GITHUB_REPOSITORY_ID"]
    decimal(repository_id, 1)
    github = GitHub(os.environ.get("GITHUB_TOKEN"))
    actual = github.repository(repository)
    require(str(actual["id"]) == repository_id and actual.get("private") is False,
            "event_mismatch", "Automation requires the matching public GitHub repository.")
    return github, repository, repository_id, actual["default_branch"]


def main():
    from .pr_automation import main as pr_main
    return pr_main()


if __name__ == "__main__":
    raise SystemExit(main())
