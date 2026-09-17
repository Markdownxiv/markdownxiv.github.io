"""Trusted Actions entry points. There is deliberately NO development-profile switch."""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .archive import (atomic_json, capture, evaluate, mark_deployed, process, public_receipt,
                      receipt_path, snapshot_key)
from .codec import canonical, decimal, fields, loads, read_json, sha, timestamp, utcnow, write_json
from .epochs import rotate
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
                    self.git(worktree, "add", "--all", "--", "papers", "receipts", "challenges", "state")
                    staged = self.git(worktree, "diff", "--cached", "--name-only", "-z").stdout.split("\0")
                    allowed = re.compile(r"(?:papers/[0-9a-f]{64}/(?:paper\.md|metadata\.json|proof\.json)|"
                                         r"receipts/[0-9]+-[0-9]+\.json|challenges/(?:latest\.json|registry\.json|"
                                         r"epochs/\d{4}-\d{2}-\d{2}\.json)|state/(?:scan|published)\.json)\Z")
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


def opened_snapshot(event, repository, repository_id):
    require(event.get("action") == "opened" and event.get("repository", {}).get("full_name") == repository
            and str(event["repository"]["id"]) == repository_id,
            "event_mismatch", "Event does not match the trusted GitHub repository context.")
    return capture(event["issue"], repository_id, "opened")


def validate_snapshot(root, snapshot, github):
    record_path = receipt_path(root, snapshot)
    if record_path.exists():
        record = read_json(record_path)
        if record["status"] != "retryable":
            return {"snapshot": snapshot, "body_base64": None, "result": public_receipt(record)}
        snapshot = record["snapshot"]
    try:
        result = evaluate(snapshot, root, production=True, fetch_body=github.fetch_paper)
        return {"snapshot": snapshot, "body_base64": base64.b64encode(result["body"]).decode("ascii"),
                "result": {"valid": True, "paper_id": result["paper_id"]}}
    except Rejection as exc:
        return {"snapshot": snapshot, "body_base64": None, "result": exc.as_dict()}


def collect(root, github, repository, repository_id, now=None, batch=20):
    """Bounded cyclic pagination, with a persisted cursor and retry backoff.

    Full pages skipped by a deletion are revisited in the next sweep. The current page
    is retained when the candidate budget is full. All recovery snapshots use NOW.
    """
    root, now = Path(root), now or utcnow()
    selected = []
    for path in sorted((root / "receipts").glob("*.json")):
        record = read_json(path)
        attempts = int(record["attempts"])
        if record["status"] != "retryable" or attempts >= 8:
            continue
        elapsed = (timestamp(now) - timestamp(record["last_attempt_at"] or now)).total_seconds()
        if elapsed >= min(86400, 60 * 2**attempts):
            selected.append(record["snapshot"])
        if len(selected) == 5:
            break
    cursor_path = root / "state" / "scan.json"
    page = int(read_json(cursor_path)["page"]) if cursor_path.exists() else 1
    for _ in range(2):
        issues = github.issues_page(repository, page)
        require(isinstance(issues, list) and len(issues) <= 100, "github_response", "Invalid Issue listing.")
        for issue in issues:
            if "pull_request" in issue or not str(issue.get("title", "")).startswith("[preprint] "):
                continue
            key = repository_id + "-" + str(issue["id"])
            decimal(str(issue["id"]), 1)
            if (root / "receipts" / (key + ".json")).exists():
                continue
            if len(selected) >= batch:
                return {"snapshots": selected, "next_page": str(page), "observed_at": now}
            selected.append(capture(issue, repository_id, "observed", now))
        if len(issues) < 100:
            page = 1
            break
        page += 1
    return {"snapshots": selected, "next_page": str(page), "observed_at": now}


def ingest(root, validated, github, repository_id):
    records = []
    for item in validated:
        fields(item, ["snapshot", "body_base64", "result"])
        snapshot = item["snapshot"]
        require(snapshot["repository_id"] == repository_id, "event_mismatch", "Artifact repository mismatch.")
        body = None
        if item["body_base64"] is not None:
            require(isinstance(item["body_base64"], str) and len(item["body_base64"]) <= 350_000,
                    "artifact_limit", "Invalid paper cache.")
            try:
                body = base64.b64decode(item["body_base64"], validate=True)
            except ValueError as exc:
                raise Rejection("artifact_limit", "Malformed paper cache.") from exc
        # No acceptance bit from the read-only artifact is trusted. Re-validate after
        # obtaining fresh state, including on every non-fast-forward retry.
        records.append(process(root, snapshot, True, github.fetch_paper, body))
    return records


COMMENT_RE = re.compile(r"<!-- agent-preprints:[0-9]+:[0-9]+ -->\n```json\n(.*)\n```\Z", re.S)


def parse_comment(comment):
    user = comment.get("user", {})
    if user.get("login") != "github-actions[bot]" or user.get("type") != "Bot":
        return None
    match = COMMENT_RE.fullmatch(comment.get("body", ""))
    if not match:
        return None
    try:
        value = loads(match.group(1))
        if value.get("receipt_version") == "agent-preprints-receipt-v1":
            return value
    except Rejection:
        pass
    return None


def upsert_comment(github, repository, record):
    snapshot = record["snapshot"]
    marker = "<!-- agent-preprints:" + snapshot["repository_id"] + ":" + snapshot["issue_id"] + " -->"
    body = marker + "\n```json\n" + canonical(public_receipt(record)).decode() + "\n```"
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
    for path in sorted((Path(root) / "receipts").glob("*.json")):
        record = read_json(path)
        digest = sha(canonical(public_receipt(record)))
        if digest == record["comment_digest"]:
            continue
        if count >= limit:
            break
        count += 1
        try:
            record["comment_id"] = upsert_comment(github, repository, record)
            record["comment_digest"] = digest
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
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate-event", "collect", "ingest-event", "maintain", "finalize"))
    parser.add_argument("--root", default=".")
    parser.add_argument("--artifact", default=".work/validated.json")
    parser.add_argument("--manifest", default=".work/manifest.json")
    args = parser.parse_args()
    try:
        github, repository, repository_id, branch = _workflow_context()
        if args.command in ("validate-event", "ingest-event"):
            require(os.environ.get("GITHUB_EVENT_NAME") == "issues", "event_mismatch", "Expected issues.opened event.")
            event_path = Path(os.environ["GITHUB_EVENT_PATH"])
            require(event_path.stat().st_size < 2_000_000, "input_limit", "Event payload too large.")
            event = json.loads(event_path.read_bytes())
            snapshot = opened_snapshot(event, repository, repository_id)
        else:
            require(os.environ.get("GITHUB_REF") == "refs/heads/" + branch or args.command == "finalize",
                    "event_mismatch", "Maintenance must run on the default branch.")
        if args.command == "validate-event":
            write_json(args.artifact, {"validated": [validate_snapshot(args.root, snapshot, github)]})
            return 0
        if args.command == "collect":
            plan = collect(args.root, github, repository, repository_id)
            write_json(args.artifact, {"validated": [validate_snapshot(args.root, s, github) for s in plan["snapshots"]],
                                       "next_page": plan["next_page"]})
            return 0
        data = read_json(args.artifact, 12_000_000) if args.command in ("ingest-event", "maintain") else None
        if args.command == "ingest-event":
            fields(data, ["validated"])
            require(len(data["validated"]) == 1, "artifact_limit", "Expected one event snapshot.")
            # A previously sealed snapshot may differ from the current edited event, but
            # only trusted repository state may authorize using it (process enforces this).
            candidate = data["validated"][0]["snapshot"]
            require(snapshot_key(candidate) == snapshot_key(snapshot), "event_mismatch", "Artifact Issue mismatch.")
            if candidate != snapshot:
                sealed = read_json(receipt_path(args.root, snapshot))
                require(candidate == sealed["snapshot"], "event_mismatch", "Artifact snapshot differs from event and sealed record.")
        if args.command == "maintain":
            fields(data, ["validated", "next_page"])
            require(isinstance(data["validated"], list) and len(data["validated"]) <= 20, "artifact_limit", "Maintenance batch limit exceeded.")
            decimal(data["next_page"], 1, 1_000_000)
        def mutate(root):
            if args.command == "maintain":
                rotate(root)
            if data is not None:
                records = ingest(root, data["validated"], github, repository_id)
                if args.command == "maintain":
                    atomic_json(root / "state" / "scan.json", {"page": data["next_page"]})
                return [public_receipt(r) for r in records]
            if os.environ.get("DEPLOYMENT_RESULT") == "success":
                config = read_json(root / "config" / "production.json")
                mark_deployed(root, read_json(args.manifest), config["site_url"])
            sync_receipts(root, github, repository)
            return []
        transaction = GitTransaction(args.root, branch)
        commit, results = transaction.run(mutate)
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                output.write("sha=" + commit + "\n")
                needs_deploy = args.command == "maintain" or any(r["archived"] and not r["published"] for r in results)
                output.write("needs_deploy=" + ("true" if needs_deploy else "false") + "\n")
        print(canonical({"commit": commit, "receipts": results}).decode())
        return 0
    except Rejection as exc:
        print(canonical({"status": "error", **exc.as_dict()}).decode())
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
