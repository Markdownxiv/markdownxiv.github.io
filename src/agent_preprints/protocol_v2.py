"""Versioned content commitments, metadata, revisions and image verification."""
import re
from pathlib import PurePosixPath

from . import PROTOCOL_V2, VERIFIER_V2, assets, poa, pow, taxonomy
from .codec import (MAX_PACKAGE, canonical, decimal, fields, hexhash, metadata as metadata_v1,
                    paper_bytes, sha, text)
from .errors import require
from .github import validate_source

PACKAGE_FIELDS = ["protocol", "repository_id", "submitter_id", "epoch_id", "epoch_hash", "metadata",
                  "paper_sha256", "content_hash", "body", "nonce", "answers", "assets", "asset_source", "intent"]
META_V1 = ("title", "abstract", "authors", "license", "tags")


def work_id(value):
    require(isinstance(value, str) and re.fullmatch(r"mx:[0-9]{4}\.[0-9]{5,10}", value),
            "invalid_work_id", "Expected a short work ID such as mx:2609.00001.")
    return value


def metadata(meta):
    fields(meta, ["title", "abstract", "authors", "license", "language", "primary_category",
                  "secondary_categories", "taxonomy_hash", "ai_disclosure", "agents"], ["tags"])
    metadata_v1({k: meta[k] for k in META_V1 if k in meta})
    require(isinstance(meta["language"], str) and re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", meta["language"]),
            "invalid_language", "Declare a language code; English (en) is the writing default.")
    hexhash(meta["taxonomy_hash"])
    require(meta["ai_disclosure"] in ("declared", "none", "unknown"), "invalid_ai_disclosure", "Explicitly declare AI use, none, or unknown.")
    require(isinstance(meta["agents"], list) and len(meta["agents"]) <= 8, "invalid_ai_disclosure", "At most eight agent declarations.")
    require((meta["ai_disclosure"] != "declared" or len(meta["agents"]) > 0)
            and (meta["ai_disclosure"] != "none" or not meta["agents"]),
            "invalid_ai_disclosure", "Declared AI requires details; none requires an empty agent list.")
    for agent in meta["agents"]:
        fields(agent, ["provider", "model", "client"], ["model_version", "role"])
        for value in agent.values():
            text(value, 1, 160)
    require(isinstance(meta["primary_category"], str) and isinstance(meta["secondary_categories"], list)
            and len(meta["secondary_categories"]) <= 2 and all(isinstance(c, str) for c in meta["secondary_categories"]),
            "invalid_category", "Choose one primary and at most two secondary categories.")


def intent(value):
    fields(value, ["kind", "work_id", "parent_hash", "change_summary"])
    require(value["kind"] in ("new", "revision"), "invalid_intent", "Unknown submission intent.")
    if value["kind"] == "new":
        require(value["work_id"] is None and value["parent_hash"] is None and value["change_summary"] == "",
                "invalid_intent", "A new work has no parent or revision summary.")
    else:
        work_id(value["work_id"])
        hexhash(value["parent_hash"])
        text(value["change_summary"], 1, 2000)


def content_hash(meta, paper_hash, entries, submission_intent):
    return sha(b"agent-preprints-content-v2\0" + canonical({"metadata": meta, "paper_sha256": paper_hash,
                                                         "assets": entries, "intent": submission_intent}))


def document_hash(paper_hash, entries):
    return sha(b"markdownxiv-document-v1\0" + canonical({"paper_sha256": paper_hash, "assets": entries}))


def validate_package(package):
    require(len(canonical(package)) <= MAX_PACKAGE, "input_limit", "Submission package exceeds 60000 bytes.")
    fields(package, PACKAGE_FIELDS)
    require(package["protocol"] == PROTOCOL_V2, "protocol_version", "Unsupported protocol.")
    decimal(package["repository_id"], 1)
    decimal(package["submitter_id"], 1)
    for key in ("epoch_hash", "paper_sha256", "content_hash"):
        hexhash(package[key])
    metadata(package["metadata"])
    intent(package["intent"])
    assets.validate_manifest(package["assets"])
    body = package["body"]
    require(isinstance(body, dict), "invalid_source", "Missing body source.")
    if body.get("kind") == "inline":
        fields(body, ["kind", "text"])
        require(isinstance(body["text"], str), "invalid_source", "Inline body must be text.")
    else:
        validate_source(body)
    source = package["asset_source"]
    if package["assets"]:
        fields(source, ["repository", "commit", "directory"])
        directory = source["directory"]
        require(isinstance(directory, str) and (directory == "" or not directory.endswith("/")), "unsafe_path", "Invalid asset directory.")
        validate_source({"kind": "github", "repository": source["repository"], "commit": source["commit"],
                         "path": (directory + "/" if directory else "") + "paper.md"})
        for entry in package["assets"]:
            validate_source({"kind": "github", "repository": source["repository"], "commit": source["commit"],
                             "path": (directory + "/" if directory else "") + entry["path"]}, image=True)
        if body["kind"] == "github":
            require(source == source_for_body(body), "source_mismatch", "Images and manuscript must share a pinned repository, commit and directory.")
    else:
        require(source is None, "invalid_source", "Empty image manifests require a null source.")
    require(content_hash(package["metadata"], package["paper_sha256"], package["assets"], package["intent"]) == package["content_hash"],
            "content_hash_mismatch", "Metadata, image manifest or revision intent differs from the PoW commitment.")
    pow.nonce_bytes(package["nonce"])


def source_for_body(body):
    directory = str(PurePosixPath(body["path"]).parent)
    return {"repository": body["repository"], "commit": body["commit"], "directory": "" if directory == "." else directory}


def verify_after_pow(package, epoch, proof_hash, fetch_body, supplied_body, fetch_asset, supplied_assets):
    if supplied_body is not None:
        body = supplied_body
        if package["body"]["kind"] == "inline":
            require(body == package["body"]["text"].encode(), "body_hash_mismatch", "Cached inline body differs.")
    elif package["body"]["kind"] == "inline":
        body = package["body"]["text"].encode()
    else:
        require(fetch_body is not None, "body_unavailable", "Supply local paper bytes or a GitHub downloader.")
        body = fetch_body(package["body"])
    paper_bytes(body, assets.MAX_PAPER)
    require(sha(body) == package["paper_sha256"], "body_hash_mismatch", "Paper bytes differ from the commitment.")
    def obtain(entry):
        if supplied_assets is not None and entry["path"] in supplied_assets:
            return supplied_assets[entry["path"]]
        require(fetch_asset is not None, "asset_unavailable", "Supply local images or a GitHub downloader.")
        source = package["asset_source"]
        path = (source["directory"] + "/" if source["directory"] else "") + entry["path"]
        return fetch_asset({"kind": "github", "repository": source["repository"], "commit": source["commit"], "path": path})
    data = assets.verify(body, package["assets"], obtain)
    problems = poa.sample(pow.seed(proof_hash), epoch["poa_policy"])
    results = poa.verify_all(problems, package["answers"])
    return {"paper_id": package["content_hash"], "body": body, "assets": data,
            "proof": {"protocol": PROTOCOL_V2, "verifier": VERIFIER_V2, "epoch_hash": package["epoch_hash"],
                      "pow_hash": proof_hash.hex(), "poa_seed": pow.seed(proof_hash).hex(), "problems": problems,
                      "results": results, "experimental": True, "package": package}}


def prepare(paper, meta, repository_id, submitter_id, epoch, epoch_hash, source=None,
            entries=None, asset_source=None, submission_intent=None, catalog=None):
    paper_bytes(paper, assets.MAX_PAPER)
    meta = dict(meta)
    meta.setdefault("language", "en")
    meta.setdefault("secondary_categories", [])
    meta["taxonomy_hash"] = epoch["taxonomy_hash"]
    if catalog is not None:
        meta["primary_category"] = taxonomy.normalize(meta["primary_category"], catalog)
        meta["secondary_categories"] = sorted({taxonomy.normalize(c, catalog) for c in meta["secondary_categories"]} - {meta["primary_category"]})
        taxonomy.validate_categories(meta, catalog)
    entries = entries or []
    submission_intent = submission_intent or {"kind": "new", "work_id": None, "parent_hash": None, "change_summary": ""}
    if entries and source and asset_source is None:
        asset_source = source_for_body(source)
    result = {"protocol": PROTOCOL_V2, "repository_id": repository_id, "submitter_id": submitter_id,
              "epoch_id": epoch["epoch_id"], "epoch_hash": epoch_hash, "metadata": meta, "assets": entries,
              "asset_source": asset_source, "intent": submission_intent, "paper_sha256": sha(paper),
              "content_hash": content_hash(meta, sha(paper), entries, submission_intent),
              "body": source or {"kind": "inline", "text": paper.decode()}, "nonce": "0000000000000000", "answers": []}
    validate_package(result)
    return result
