"""Short IDs, immutable versions and a recoverable local archive transaction.

Call mutations only while holding archive.lock. Production visibility is the atomic
Git commit; the local write-ahead journal also survives interruption between renames.
"""
import copy
import os
import re
import shutil
from pathlib import Path

from . import PROTOCOL, PROTOCOL_V2, assets
from .codec import canonical, read_json, sha, timestamp, utcnow
from .errors import require
from .protocol_v2 import document_hash, work_id


def path(root, wid):
    return Path(root) / "works" / (work_id(wid)[3:] + ".json")


def all_works(root):
    return [read_json(p) for p in sorted((Path(root) / "works").glob("*.json"))]


def allocate(root, received_at):
    month = timestamp(received_at).strftime("%y%m")
    numbers = [int(w["work_id"].split(".")[1]) for w in all_works(root) if w["work_id"].startswith("mx:" + month + ".")]
    return "mx:" + month + "." + str(max(numbers, default=0) + 1).zfill(5)


def version(record, package, number="1", summary="Initial submission"):
    return {"version": number, "content_hash": record["paper_id"], "received_at": record["received_at"],
            "source_issue_id": record["source_issue_id"], "source_issue_number": record["source_issue_number"],
            "protocol": package["protocol"], "document_hash": document_hash(record["paper_sha256"], package.get("assets", [])),
            "change_summary": summary}


def new_work(wid, record, package):
    return {"work_id": wid, "repository_id": record["repository_id"], "owner_id": record["submitter_id"],
            "created_at": record["received_at"], "root_issue_id": record["source_issue_id"],
            "root_issue_number": record["source_issue_number"], "versions": [version(record, package)]}


def migrate(root):
    """Add deterministic legacy aliases without modifying old papers, proofs or receipts."""
    from .archive import atomic_json
    root = Path(root)
    known = {v["content_hash"] for w in all_works(root) for v in w["versions"]}
    records = [read_json(p) for p in (root / "papers").glob("*/metadata.json")]
    for record in sorted(records, key=lambda r: (r["received_at"], r["paper_id"])):
        if record["paper_id"] in known:
            continue
        proof = read_json(root / "papers" / record["paper_id"] / "proof.json")
        require(proof["protocol"] == PROTOCOL, "archive_conflict", "Unregistered v2 version; recover its journal first.")
        wid = allocate(root, record["received_at"])
        atomic_json(path(root, wid), new_work(wid, record, proof["package"]))
    return all_works(root)


def locate(root, pid):
    for work in all_works(root):
        for entry in work["versions"]:
            if entry["content_hash"] == pid:
                return work, entry
    return None, None


def annotate(record, work, entry, root):
    config = read_json(Path(root) / "config" / "production.json")
    base = config["site_url"].rstrip("/") + "/"
    record.update({"work_id": work["work_id"], "version": entry["version"],
                   "work_url": base + "p/" + work["work_id"][3:] + "/",
                   "discussion_url": "https://github.com/" + config["repository"] + "/issues/" + work["root_issue_number"]})
    if record["published"]:
        record["url"] = record["work_url"] + "v" + record["version"] + "/"


SAFE = re.compile(r"(?:papers/[0-9a-f]{64}/(?:paper\.md|metadata\.json|proof\.json)|assets/[0-9a-f]{64}\.(?:png|jpg|webp)|works/[0-9]{4}\.[0-9]{5,10}\.json|receipts/[0-9]+-[0-9]+\.json)\Z")


def _write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _apply(root, journal):
    manifest = read_json(journal / "ready.json")
    for item in manifest["files"]:
        name = item["path"]
        require(SAFE.fullmatch(name), "unsafe_write", "Unsafe journal destination.")
        source, destination = journal / "data" / name, root / name
        raw = source.read_bytes()
        require(sha(raw) == item["sha256"], "archive_conflict", "Journal bytes changed.")
        current = sha(destination.read_bytes()) if destination.exists() else None
        if current == item["sha256"]:
            continue
        require(current == item["previous"], "archive_conflict", "Journal compare-and-swap failed.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(".pending-" + destination.name)
        _write(temporary, raw)
        os.replace(temporary, destination)
        descriptor = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    shutil.rmtree(journal)


def recover(root):
    root = Path(root)
    for journal in sorted((root / ".transactions").glob("*")):
        if (journal / "ready.json").exists():
            _apply(root, journal)
        elif journal.is_dir():
            shutil.rmtree(journal)  # No published files exist before the ready marker.


def commit(root, key, files):
    """Ordered immutable blobs, then registry and receipt; ready is written last."""
    from .archive import atomic_json
    require(re.fullmatch(r"[0-9]+-[0-9]+", key), "unsafe_write", "Invalid transaction key.")
    journal = root / ".transactions" / key
    journal.mkdir(parents=True, exist_ok=False)
    manifest = []
    for name, raw in files:
        require(SAFE.fullmatch(name), "unsafe_write", "Unsafe archive destination.")
        destination = root / name
        previous = sha(destination.read_bytes()) if destination.exists() else None
        if name.startswith(("papers/", "assets/")):
            require(previous in (None, sha(raw)), "archive_conflict", "An immutable object already exists with other bytes.")
        _write(journal / "data" / name, raw)
        manifest.append({"path": name, "sha256": sha(raw), "previous": previous})
    atomic_json(journal / "ready.json", {"files": manifest})
    _apply(root, journal)


def admit(root, snapshot, result, receipt):
    from .archive import atomic_json, receipt_path, snapshot_key
    migrate(root)
    package, pid = result["proof"]["package"], result["paper_id"]
    intention = package["intent"]
    works = all_works(root)
    fingerprint = document_hash(package["paper_sha256"], package["assets"])
    target = next((w for w in works if w["work_id"] == intention["work_id"]), None)
    if intention["kind"] == "revision":
        require(target is not None, "unknown_work", "No such revision target.")
        require(target["owner_id"] == snapshot["submitter_id"] and target["repository_id"] == snapshot["repository_id"],
                "revision_unauthorized", "Only the original GitHub numerical user ID may revise this work.")
        # Exact replay through a new Issue is idempotent, even after a later revision.
        replay = next((v for v in target["versions"] if v["content_hash"] == pid), None)
        if replay:
            receipt.update({"status": "duplicate", "error_code": None, "message": "This exact version is already archived.",
                            "paper_id": pid, "content_hash": pid, "archived": True})
            annotate(receipt, target, replay, root)
            atomic_json(receipt_path(root, snapshot), receipt)
            return receipt
        require(target["versions"][-1]["content_hash"] == intention["parent_hash"],
                "revision_conflict", "The parent is no longer current. Prepare and prove a new revision against the latest version.")
        parent = read_json(root / "papers" / intention["parent_hash"] / "proof.json")["package"]
        require(any(package[k] != parent.get(k, []) for k in ("metadata", "paper_sha256", "assets")),
                "revision_unchanged", "No manuscript, metadata or image changes; no new version created.")
    for work in works:
        if target and work["work_id"] == target["work_id"]:
            continue
        duplicate = next((v for v in work["versions"] if v["document_hash"] == fingerprint), None)
        if duplicate:
            require(intention["kind"] == "new", "duplicate_other_work", "This manuscript and images belong to another work.")
            receipt.update({"status": "duplicate", "error_code": None, "message": "Manuscript and images already archived.",
                            "paper_id": duplicate["content_hash"], "content_hash": pid, "archived": True})
            annotate(receipt, work, duplicate, root)
            atomic_json(receipt_path(root, snapshot), receipt)
            return receipt
    metadata = {"paper_id": pid, "paper_sha256": package["paper_sha256"], "metadata": package["metadata"],
                "received_at": snapshot["received_at"], "archived_at": utcnow(), "source_issue_id": snapshot["issue_id"],
                "source_issue_number": snapshot["issue_number"], "repository_id": snapshot["repository_id"],
                "submitter_id": snapshot["submitter_id"], "assets": package["assets"]}
    if target:
        work = copy.deepcopy(target)
        work["versions"].append(version(metadata, package, str(len(work["versions"]) + 1), intention["change_summary"]))
    else:
        work = new_work(allocate(root, snapshot["received_at"]), metadata, package)
    receipt.update({"status": "accepted", "error_code": None, "message": "Proofs verified; archived. Pages publication pending.",
                    "paper_id": pid, "content_hash": pid, "archived": True})
    annotate(receipt, work, work["versions"][-1], root)
    encode = lambda value: canonical(value) + b"\n"
    prefix = "papers/" + pid + "/"
    files = [(prefix + "paper.md", result["body"]), (prefix + "metadata.json", encode(metadata)),
             (prefix + "proof.json", encode(result["proof"]))]
    unique = {assets.filename(e): result["assets"][e["path"]] for e in package["assets"]}
    files += [("assets/" + name, raw) for name, raw in unique.items()]
    files += [("works/" + work["work_id"][3:] + ".json", encode(work)),
              ("receipts/" + snapshot_key(snapshot) + ".json", encode(receipt))]
    commit(root, snapshot_key(snapshot), files)
    return receipt
