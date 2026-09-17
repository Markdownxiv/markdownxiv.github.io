"""V4 PR commitments and an 8 MB material budget; mathematical families stay unchanged."""
from . import PROTOCOL_V4, VERIFIER_V4, assets, poa, pow, taxonomy
from .codec import MAX_PACKAGE, canonical, decimal, fields, hexhash, paper_bytes, sha
from .errors import require
from . import protocol_v2 as v2
from .protocol_v3 import PACKAGE_FIELDS, MAX_PROOF, homepages, material_size, metadata_file

MAX_MATERIAL = 8_000_000
POLICY = {**assets.POLICY, "paper_bytes": str(MAX_MATERIAL), "image_bytes": str(MAX_MATERIAL),
          "image_total_bytes": str(MAX_MATERIAL), "version_bytes": str(MAX_MATERIAL),
          "metadata_included": True, "proof_bytes": str(MAX_PROOF)}


def content_hash(meta, paper_hash, entries, intention):
    return sha(b"agent-preprints-content-v4\0" + canonical({"metadata": meta, "paper_sha256": paper_hash,
                                                          "assets": entries, "intent": intention}))


def validate_package(package):
    require(len(canonical(package)) + 1 <= MAX_PACKAGE, "input_limit", "Submission proof package exceeds 60000 bytes.")
    fields(package, PACKAGE_FIELDS)
    require(package["protocol"] == PROTOCOL_V4, "protocol_version", "Expected a v4 PR submission.")
    decimal(package["repository_id"], 1)
    decimal(package["submitter_id"], 1)
    for key in ("epoch_hash", "paper_sha256", "content_hash"):
        hexhash(package[key])
    decimal(package["paper_size"], 1, MAX_MATERIAL)
    v2.metadata(package["metadata"])
    homepages(package["author_homepages"], package["metadata"])
    v2.intent(package["intent"])
    assets.validate_manifest(package["assets"], MAX_MATERIAL, MAX_MATERIAL)
    require(material_size(package) <= MAX_MATERIAL, "material_limit", "Manuscript, images and metadata exceed 8000000 bytes.")
    require(content_hash(package["metadata"], package["paper_sha256"], package["assets"], package["intent"]) == package["content_hash"],
            "content_hash_mismatch", "Manuscript, metadata, images or revision intent differs from the proof commitment.")
    pow.nonce_bytes(package["nonce"])


def prepare(paper, meta, repository_id, submitter_id, epoch, epoch_hash, source=None,
            entries=None, submission_intent=None, catalog=None, **kwargs):
    require(source is None, "invalid_source", "PR submissions read files from the sealed PR commit.")
    paper_bytes(paper, MAX_MATERIAL)
    require(isinstance(meta, dict), "invalid_metadata", "Metadata must be an object.")
    meta = dict(meta)
    require(isinstance(meta.get("authors"), list), "invalid_metadata", "Metadata must declare authors.")
    links = meta.pop("author_homepages", [None] * len(meta["authors"]))
    meta.setdefault("language", "en")
    meta.setdefault("secondary_categories", [])
    meta["taxonomy_hash"] = epoch["taxonomy_hash"]
    v2.metadata(meta)
    if catalog is not None:
        meta["primary_category"] = taxonomy.normalize(meta["primary_category"], catalog)
        meta["secondary_categories"] = sorted({taxonomy.normalize(c, catalog) for c in meta["secondary_categories"]} - {meta["primary_category"]})
        taxonomy.validate_categories(meta, catalog)
    entries = entries or []
    intention = submission_intent or {"kind": "new", "work_id": None, "parent_hash": None, "change_summary": ""}
    package = {"protocol": PROTOCOL_V4, "repository_id": repository_id, "submitter_id": submitter_id,
               "epoch_id": epoch["epoch_id"], "epoch_hash": epoch_hash, "metadata": meta,
               "paper_sha256": sha(paper), "paper_size": str(len(paper)), "assets": entries,
               "intent": intention, "nonce": "0000000000000000", "answers": [], "author_homepages": links,
               "content_hash": content_hash(meta, sha(paper), entries, intention)}
    validate_package(package)
    return package


def verify_after_pow(package, epoch, proof_hash, fetch_body=None, supplied_body=None, fetch_asset=None, supplied_assets=None):
    body = supplied_body
    require(body is not None, "body_unavailable", "Supply the manuscript from the sealed PR commit.")
    paper_bytes(body, MAX_MATERIAL)
    require(len(body) == int(package["paper_size"]) and sha(body) == package["paper_sha256"],
            "body_hash_mismatch", "Manuscript bytes differ from the proof commitment.")
    def obtain(entry):
        require(supplied_assets is not None and entry["path"] in supplied_assets, "asset_unavailable", "A sealed image is missing.")
        return supplied_assets[entry["path"]]
    data = assets.verify(body, package["assets"], obtain, MAX_MATERIAL, MAX_MATERIAL)
    problems = poa.sample(pow.seed(proof_hash), epoch["poa_policy"])
    proof = {"protocol": PROTOCOL_V4, "verifier": VERIFIER_V4, "epoch_hash": package["epoch_hash"],
             "pow_hash": proof_hash.hex(), "poa_seed": pow.seed(proof_hash).hex(), "problems": problems,
             "results": poa.verify_all(problems, package["answers"]), "experimental": True, "package": package}
    require(len(canonical(proof) + b"\n") <= MAX_PROOF, "proof_limit", "Archive proof exceeds 512 KiB.")
    return {"paper_id": package["content_hash"], "body": body, "assets": data, "proof": proof}
