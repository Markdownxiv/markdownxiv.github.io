"""Sealed requests and local durable archive; a Git transaction publishes them atomically."""
import base64
import contextlib
import fcntl
import os
import tempfile
from pathlib import Path

from .codec import MAX_PACKAGE, canonical, decimal, fields, loads, read_json, sha, timestamp, utcnow, write_json
from .errors import Rejection, require
from .protocol import Context, verify


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = stream.name
        stream.write(canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextlib.contextmanager
def lock(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".archive.lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def capture(issue, repository_id, mode="observed", observed_at=None):
    """Call opened ONLY on the actual GITHUB_EVENT_PATH issues.opened payload."""
    require(mode in ("opened", "observed"), "invalid_snapshot", "Invalid observation mode.")
    require("pull_request" not in issue and str(issue.get("title", "")).startswith("[preprint] "),
            "not_submission", "Not a preprint submission Issue.")
    for value in (repository_id, str(issue["id"]), str(issue["number"]), str(issue["user"]["id"])):
        decimal(value, 1)
    body = issue.get("body") or ""
    raw = body.encode("utf-8")
    received_at = issue["created_at"] if mode == "opened" else (observed_at or utcnow())
    timestamp(received_at)
    return {"repository_id": repository_id, "issue_id": str(issue["id"]), "issue_number": str(issue["number"]),
            "submitter_id": str(issue["user"]["id"]), "received_at": received_at, "mode": mode,
            "request_sha256": sha(raw), "body": body if len(raw) <= MAX_PACKAGE else None}


def snapshot_key(snapshot):
    fields(snapshot, ["repository_id", "issue_id", "issue_number", "submitter_id", "received_at", "mode",
                      "request_sha256", "body"])
    from .codec import hexhash
    for key in ("repository_id", "issue_id", "issue_number", "submitter_id"):
        decimal(snapshot[key], 1)
    timestamp(snapshot["received_at"])
    hexhash(snapshot["request_sha256"])
    require(snapshot["mode"] in ("opened", "observed", "pull_request"), "invalid_snapshot", "Invalid snapshot mode.")
    if snapshot["body"] is not None:
        require(isinstance(snapshot["body"], str) and len(snapshot["body"].encode("utf-8")) <= MAX_PACKAGE
                and sha(snapshot["body"].encode("utf-8")) == snapshot["request_sha256"],
                "invalid_snapshot", "Snapshot digest mismatch.")
    return snapshot["repository_id"] + ("-pr-" if snapshot["mode"] == "pull_request" else "-") + snapshot["issue_id"]


def receipt_path(root, snapshot):
    return Path(root) / "receipts" / (snapshot_key(snapshot) + ".json")


def evaluate(snapshot, root, production=True, fetch_body=None, supplied_body=None, fetch_asset=None, supplied_assets=None):
    snapshot_key(snapshot)
    if snapshot["mode"] == "pull_request":
        from .pull_requests import evaluate as evaluate_pr
        return evaluate_pr(snapshot, root, production, fetch_body, supplied_body)
    require(snapshot["body"] is not None, "input_limit", "Issue package exceeded 60000 bytes at first observation.")
    from .envelope import parse_submission
    package = parse_submission(snapshot["body"])
    context = Context(snapshot["repository_id"], snapshot["submitter_id"], snapshot["received_at"])
    try:
        return verify(package, root, context, production, fetch_body, supplied_body, fetch_asset, supplied_assets)
    except Rejection as exc:
        if snapshot["mode"] == "observed" and exc.code in ("epoch_expired", "epoch_not_yet_valid", "epoch_unpublished_at_submission"):
            raise Rejection("original_snapshot_unavailable", "Original opened snapshot is unavailable; this complete body was checked at first observation. Create a new Issue with a current proof.") from exc
        raise


def process(root, snapshot, production=True, fetch_body=None, supplied_body=None, fetch_asset=None, supplied_assets=None):
    with lock(root):
        from .works import recover
        recover(root)
        return _process(Path(root), snapshot, production, fetch_body, supplied_body, fetch_asset, supplied_assets)


def _process(root, snapshot, production, fetch_body, supplied_body, fetch_asset, supplied_assets):
    path = receipt_path(root, snapshot)
    if path.exists():
        record = read_json(path)
        if record["status"] != "retryable":
            return record
        if snapshot != record["snapshot"]:
            supplied_body, supplied_assets = None, None
        snapshot = record["snapshot"]  # Never replace the sealed body or observation time.
    else:
        record = {"snapshot": snapshot, "status": "retryable", "error_code": "processing",
                  "message": "Request sealed; processing pending.", "paper_id": None, "content_hash": None,
                  "archived": False, "published": False, "url": None, "comment_id": None,
                  "comment_digest": None, "attempts": "0", "last_attempt_at": None}
        atomic_json(path, record)
    record["attempts"] = str(int(record["attempts"]) + 1)
    record["last_attempt_at"] = utcnow()
    try:
        result = evaluate(snapshot, root, production, fetch_body, supplied_body, fetch_asset, supplied_assets)
        package = result["proof"]["package"]
        record["content_hash"] = package["content_hash"]
        from . import PROTOCOL_V2, PR_PROTOCOLS
        if package["protocol"] in (PROTOCOL_V2, *PR_PROTOCOLS):
            from .works import admit
            record = admit(root, snapshot, result, record)
            published = root / "state" / "published.json"
            if published.exists() and record["paper_id"] in read_json(published)["paper_ids"]:
                record.update({"published": True, "url": record["work_url"] + "v" + record["version"] + "/"})
                if package["protocol"] in PR_PROTOCOLS:
                    from .works import all_works, annotate
                    work = next(w for w in all_works(root) if w["work_id"] == record["work_id"])
                    entry = next(v for v in work["versions"] if v["content_hash"] == record["paper_id"])
                    annotate(record, work, entry, root)
            atomic_json(path, record)
            return record
        existing = None
        for meta_path in sorted((root / "papers").glob("*/metadata.json")):
            meta = read_json(meta_path)
            if meta["paper_sha256"] == package["paper_sha256"]:
                existing = meta
                break
        paper_id = existing["paper_id"] if existing else result["paper_id"]
        if not existing:
            parent = root / "papers"
            parent.mkdir(parents=True, exist_ok=True)
            destination = parent / paper_id
            require(not destination.exists(), "archive_conflict", "Paper ID already exists with different content.")
            with tempfile.TemporaryDirectory(prefix=".pending-", dir=parent) as pending:
                staged = Path(pending) / "paper"
                staged.mkdir()
                (staged / "paper.md").write_bytes(result["body"])
                write_json(staged / "metadata.json", {"paper_id": paper_id, "paper_sha256": package["paper_sha256"],
                    "metadata": package["metadata"], "received_at": snapshot["received_at"],
                    "archived_at": utcnow(), "source_issue_id": snapshot["issue_id"],
                    "source_issue_number": snapshot["issue_number"], "repository_id": snapshot["repository_id"],
                    "submitter_id": snapshot["submitter_id"]})
                write_json(staged / "proof.json", result["proof"])
                os.rename(staged, destination)
        record.update({"status": "duplicate" if existing else "accepted", "error_code": None,
                       "message": "Body already archived." if existing else "Proofs verified; archived. Pages publication pending.",
                       "paper_id": paper_id, "archived": True})
        from .works import migrate
        migrate(root)
        # Reconcile a previously published duplicate without claiming a new deployment.
        published_path = root / "state" / "published.json"
        if published_path.exists() and paper_id in read_json(published_path)["paper_ids"]:
            config = read_json(root / "config" / "production.json")
            record.update({"published": True, "url": config["site_url"].rstrip("/") + "/papers/" + paper_id + "/"})
    except Rejection as exc:
        record.update({"status": "retryable" if exc.retryable else "rejected", "error_code": exc.code, "message": exc.message})
    atomic_json(path, record)
    return record


def public_receipt(record):
    result = {key: record[key] for key in ("status", "paper_id", "content_hash", "error_code", "message", "archived", "published", "url")}
    result.update({"receipt_version": "agent-preprints-receipt-v1", "request_sha256": record["snapshot"]["request_sha256"],
                   "repository_id": record["snapshot"]["repository_id"], "issue_id": record["snapshot"]["issue_id"],
                   "publication_status": "published" if record["published"] else ("pending" if record["archived"] else "not_archived")})
    if record.get("work_id"):
        result["receipt_version"] = "agent-preprints-receipt-v2"
        result.update({key: record[key] for key in ("work_id", "version", "work_url", "discussion_url")})
    if record["snapshot"]["mode"] == "pull_request":
        from .pull_requests import source
        result.update({"receipt_version": "markdownxiv-receipt-v3", "pull_request_id": result.pop("issue_id"),
                       "pull_request_number": record["snapshot"]["issue_number"],
                       "head_sha": source(record["snapshot"])["head_sha"]})
    return result


def mark_deployed(root, manifest, site_url):
    """Called only by a trusted job after deploy-pages reports success."""
    from .codec import hexhash
    fields(manifest, ["built_at", "paper_ids", "epochs", "source_digest"])
    hexhash(manifest["source_digest"])
    timestamp(manifest["built_at"])
    root = Path(root)
    published_state = root / "state" / "published.json"
    if published_state.exists():
        previous = read_json(published_state).get("built_at")
        require(previous is None or timestamp(previous) <= timestamp(manifest["built_at"]),
                "stale_deployment", "An older deployment cannot replace newer publication state.")
    for pid in manifest["paper_ids"]:
        hexhash(pid)
        require((root / "papers" / pid / "proof.json").is_file(), "manifest_mismatch", "Deployed manifest names an unknown paper.")
    registry_path = root / "challenges" / "registry.json"
    registry = read_json(registry_path)
    for published in manifest["epochs"]:
        fields(published, ["epoch_id", "epoch_hash"])
        entries = [e for e in registry["epochs"] if e["epoch_id"] == published["epoch_id"] and e["epoch_hash"] == published["epoch_hash"]]
        require(len(entries) == 1, "manifest_mismatch", "Deployed manifest names an unknown epoch.")
        if entries[0]["published_at"] is None:
            entries[0]["published_at"] = manifest["built_at"]
    atomic_json(registry_path, registry)
    atomic_json(root / "state" / "published.json", {"paper_ids": manifest["paper_ids"], "built_at": manifest["built_at"], "deployed_at": utcnow()})
    for path in (root / "receipts").glob("*.json"):
        record = read_json(path)
        if record["archived"] and record["paper_id"] in manifest["paper_ids"]:
            record.update({"published": True, "url": site_url.rstrip("/") + "/papers/" + record["paper_id"] + "/",
                           "message": "Proofs verified; archived and published. Not peer reviewed."})
            if record.get("work_id"):
                record["url"] = record["work_url"] + "v" + record["version"] + "/"
                if record["snapshot"]["mode"] == "pull_request":
                    record["url"] = site_url.rstrip("/") + "/abs/" + record["work_id"][3:] + "v" + record["version"] + "/"
            atomic_json(path, record)
