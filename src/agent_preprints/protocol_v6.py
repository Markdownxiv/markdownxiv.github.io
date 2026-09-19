"""Isotropic-only admission with explicit v6 commitments and unchanged material limits."""
from . import PROTOCOL_V6, VERIFIER_V6, assets, poi, poi_v6, pow, taxonomy
from .codec import canonical, decimal, fields, hexhash, paper_bytes, sha
from .errors import require
from . import protocol_v2 as v2
from .protocol_v3 import PACKAGE_FIELDS, homepages, material_size, metadata_file

MAX_MATERIAL = 8_000_000
MAX_PACKAGE = 1_000_000
MAX_PROOF = 2_000_000
POLICY = {**assets.POLICY, "paper_bytes": str(MAX_MATERIAL), "image_bytes": str(MAX_MATERIAL),
          "image_total_bytes": str(MAX_MATERIAL), "version_bytes": str(MAX_MATERIAL),
          "metadata_included": True, "proof_bytes": str(MAX_PROOF), "submission_bytes": str(MAX_PACKAGE),
          "certificate_bytes": str(poi.MAX_CERTIFICATE),
          "verification_cpu_seconds": str(poi.CPU_SECONDS), "verification_wall_seconds": str(poi.WALL_SECONDS),
          "verification_memory_bytes": str(poi.MEMORY_BYTES)}


def content_hash(meta, paper_hash, entries, intention):
    return sha(b"agent-preprints-content-v6\0" + canonical({"metadata": meta, "paper_sha256": paper_hash,
                                                          "assets": entries, "intent": intention}))


def validate_package(package):
    require(len(canonical(package)) + 1 <= MAX_PACKAGE, "input_limit", "V6 proof package exceeds 1000000 bytes.")
    fields(package, PACKAGE_FIELDS)
    require(package["protocol"] == PROTOCOL_V6, "protocol_version", "Expected a v6 PR submission.")
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
    require(len(canonical(metadata_file(package))) + 1 <= 60_000, "input_limit", "Author metadata exceeds 60000 bytes.")
    require(content_hash(package["metadata"], package["paper_sha256"], package["assets"], package["intent"]) == package["content_hash"],
            "content_hash_mismatch", "Manuscript, metadata, images or intent differs from the proof commitment.")
    require(isinstance(package["answers"], list) and len(package["answers"]) in (0, 1),
            "answer_count", "Use an empty draft or exactly one common isotropic certificate.")
    pow.nonce_bytes(package["nonce"])


def prepare(paper, meta, repository_id, submitter_id, epoch, epoch_hash, source=None,
            entries=None, submission_intent=None, catalog=None, **kwargs):
    require(source is None, "invalid_source", "PR submissions use the sealed PR commit.")
    paper_bytes(paper, MAX_MATERIAL)
    require(isinstance(meta, dict) and isinstance(meta.get("authors"), list), "invalid_metadata", "Declare author metadata.")
    meta = dict(meta)
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
    package = {"protocol": PROTOCOL_V6, "repository_id": repository_id, "submitter_id": submitter_id,
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
    seed = pow.seed(proof_hash, PROTOCOL_V6)
    problems = poi_v6.sample(seed, epoch["poa_policy"])
    proof = {"protocol": PROTOCOL_V6, "verifier": VERIFIER_V6, "epoch_hash": package["epoch_hash"],
             "pow_hash": proof_hash.hex(), "poa_seed": seed.hex(), "problems": problems,
             "results": poi_v6.verify_all(problems, package["answers"]), "experimental": True, "package": package}
    require(len(canonical(proof)) + 1 <= MAX_PROOF, "proof_limit", "Archive proof exceeds 2000000 bytes.")
    return {"paper_id": package["content_hash"], "body": body, "assets": data, "proof": proof}
