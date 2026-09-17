"""Historical Issue automation fixtures, never imported by production entry points."""
import base64
import re
import sys
from pathlib import Path

from agent_preprints.archive import atomic_json, capture, evaluate, process, public_receipt, receipt_path
from agent_preprints.automation import upsert_comment
from agent_preprints.codec import canonical, decimal, fields, read_json, sha, timestamp, utcnow
from agent_preprints.errors import Rejection, require


def opened_snapshot(event, repository, repository_id):
    require(event.get("action") == "opened" and event.get("repository", {}).get("full_name") == repository
            and str(event["repository"]["id"]) == repository_id,
            "event_mismatch", "Event does not match the trusted GitHub repository context.")
    return capture(event["issue"], repository_id, "opened")


def validate_snapshot(root, snapshot, github, cache=None):
    record_path = receipt_path(root, snapshot)
    if record_path.exists():
        record = read_json(record_path)
        if record["status"] != "retryable":
            return {"snapshot": snapshot, "body_base64": None, "result": public_receipt(record)}
        snapshot = record["snapshot"]
    try:
        from agent_preprints.github import wall_timeout
        with wall_timeout(120):
            result = evaluate(snapshot, root, production=True,
                              fetch_body=getattr(github, "fetch_paper_v2", github.fetch_paper),
                              fetch_asset=getattr(github, "fetch_asset", None))
        if cache is not None:
            from agent_preprints.assets import filename
            cache = Path(cache)
            cache.mkdir(parents=True, exist_ok=True)
            body_name = sha(result["body"]) + ".md"
            (cache / body_name).write_bytes(result["body"])
            asset_files = []
            for entry in result["proof"]["package"].get("assets", []):
                name = filename(entry)
                (cache / name).write_bytes(result["assets"][entry["path"]])
                asset_files.append({"path": entry["path"], "file": name})
            return {"snapshot": snapshot, "body_file": body_name, "asset_files": asset_files,
                    "result": {"valid": True, "paper_id": result["paper_id"]}}
        return {"snapshot": snapshot, "body_base64": base64.b64encode(result["body"]).decode("ascii"),
                "result": {"valid": True, "paper_id": result["paper_id"]}}
    except Rejection as exc:
        return {"snapshot": snapshot, "body_base64": None, "result": exc.as_dict()}


def collect(root, github, repository, repository_id, now=None, batch=5):
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


def ingest(root, validated, github, repository_id, cache=None):
    records = []
    total = 0
    for item in validated:
        binary = "body_file" in item
        fields(item, ["snapshot", "result"] + (["body_file", "asset_files"] if binary else ["body_base64"]))
        snapshot = item["snapshot"]
        require(snapshot["repository_id"] == repository_id, "event_mismatch", "Artifact repository mismatch.")
        body, image_data = None, None
        if binary:
            from agent_preprints.assets import MAX_PAPER, MAX_IMAGE, logical_path
            require(cache is not None and isinstance(item["asset_files"], list) and len(item["asset_files"]) <= 20,
                    "artifact_limit", "Invalid binary artifact cache.")
            def read_cache(name, cap):
                nonlocal total
                require(isinstance(name, str) and re.fullmatch(r"[0-9a-f]{64}\.(?:md|png|jpg|webp)", name),
                        "artifact_limit", "Unsafe cache filename.")
                path = Path(cache) / name
                require(path.is_file() and not path.is_symlink() and path.stat().st_size <= cap, "artifact_limit", "Missing or oversized cache file.")
                raw = path.read_bytes()
                total += len(raw)
                require(total <= 64 * 1024 * 1024 and sha(raw) == name.split(".")[0], "artifact_limit", "Cache digest or batch budget mismatch.")
                return raw
            body = read_cache(item["body_file"], MAX_PAPER)
            image_data = {}
            for asset in item["asset_files"]:
                fields(asset, ["path", "file"])
                logical_path(asset["path"])
                require(asset["path"] not in image_data, "artifact_limit", "Duplicate cached image path.")
                image_data[asset["path"]] = read_cache(asset["file"], MAX_IMAGE)
        elif item["body_base64"] is not None:
            require(isinstance(item["body_base64"], str) and len(item["body_base64"]) <= 350_000,
                    "artifact_limit", "Invalid paper cache.")
            try:
                body = base64.b64decode(item["body_base64"], validate=True)
            except ValueError as exc:
                raise Rejection("artifact_limit", "Malformed paper cache.") from exc
        # No acceptance bit from the read-only artifact is trusted. Re-validate after
        # obtaining fresh state, including on every non-fast-forward retry.
        from agent_preprints.github import wall_timeout
        with wall_timeout(120):
            records.append(process(root, snapshot, True, getattr(github, "fetch_paper_v2", github.fetch_paper), body,
                                   getattr(github, "fetch_asset", None), image_data))
    return records


def sync_receipts(root, github, repository, limit=20):
    count = 0
    for path in sorted((Path(root) / "receipts").glob("*.json")):
        record = read_json(path)
        if record["archived"] and not record.get("work_id"):
            from agent_preprints.works import locate
            work, version = locate(root, record["paper_id"])
            if work:
                config = read_json(Path(root) / "config/production.json")
                # Human-facing aliases only: preserve the original v1 receipt JSON.
                record.update({"display_work_id": work["work_id"], "display_version": version["version"],
                               "display_work_url": config["site_url"].rstrip("/") + "/p/" + work["work_id"][3:] + "/",
                               "display_discussion_url": "https://github.com/" + repository + "/issues/" + work["root_issue_number"]})
        from agent_preprints.envelope import receipt_body
        digest = sha(receipt_body(record).encode())
        needs_close = record["snapshot"]["mode"] == "pull_request" and record["published"] and not record.get("pr_closed")
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
