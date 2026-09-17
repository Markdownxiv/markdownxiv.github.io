from dataclasses import dataclass
from pathlib import Path

from . import PROTOCOL, VERIFIER
from .codec import (MAX_PACKAGE, canonical, content_hash, decimal, fields, hexhash,
                    loads, metadata, paper_bytes, sha, timestamp)
from .epochs import load_epoch
from .errors import Rejection, require
from . import poa, pow

PACKAGE_FIELDS = ["protocol", "repository_id", "submitter_id", "epoch_id", "epoch_hash", "metadata",
                  "paper_sha256", "content_hash", "body", "nonce", "answers"]


@dataclass(frozen=True)
class Context:
    repository_id: str
    submitter_id: str
    received_at: str


def validate_package(package):
    require(len(canonical(package)) <= MAX_PACKAGE, "input_limit", "Submission package exceeds 60000 bytes.")
    fields(package, PACKAGE_FIELDS)
    require(package["protocol"] == PROTOCOL, "protocol_version", "Unsupported submission protocol.")
    decimal(package["repository_id"], 1)
    decimal(package["submitter_id"], 1)
    for key in ("epoch_hash", "paper_sha256", "content_hash"):
        hexhash(package[key])
    metadata(package["metadata"])
    body = package["body"]
    require(isinstance(body, dict), "invalid_source", "Missing body source.")
    if body.get("kind") == "inline":
        fields(body, ["kind", "text"])
        require(isinstance(body["text"], str), "invalid_source", "Inline body must be text.")
    elif body.get("kind") == "github":
        from .github import validate_source
        validate_source(body)
    else:
        raise Rejection("invalid_source", "Only inline and immutable GitHub file sources are accepted.")
    pow.nonce_bytes(package["nonce"])


def verify_pow(package, root, context, production=True):
    validate_package(package)
    decimal(context.repository_id, 1)
    decimal(context.submitter_id, 1)
    timestamp(context.received_at)
    require(package["repository_id"] == context.repository_id,
            "repository_mismatch", "Submission targets another repository ID.")
    require(package["submitter_id"] == context.submitter_id,
            "identity_mismatch", "Submission is bound to another GitHub user ID.")
    epoch = load_epoch(root, package["epoch_id"], package["epoch_hash"], context.received_at,
                       context.repository_id, production)
    head = pow.header(context.repository_id, package["epoch_hash"], context.submitter_id, package["content_hash"])
    proof_hash = pow.verify(head, package["nonce"], epoch["target"])
    return epoch, proof_hash


def verify(package, root, context, production=True, fetch_body=None, supplied_body=None):
    """Order matters: validate trusted epoch and cheap PoW BEFORE fetching any paper."""
    epoch, proof_hash = verify_pow(package, root, context, production)
    if supplied_body is not None:
        body = supplied_body
        if package["body"]["kind"] == "inline":
            require(body == package["body"]["text"].encode("utf-8"), "body_hash_mismatch", "Cached inline body differs.")
    elif package["body"]["kind"] == "inline":
        body = package["body"]["text"].encode("utf-8")
    else:
        require(fetch_body is not None, "body_unavailable", "Offline verification needs --paper for a GitHub source.")
        body = fetch_body(package["body"])
    paper_bytes(body)
    require(sha(body) == package["paper_sha256"], "body_hash_mismatch", "Paper bytes do not match their declared SHA-256.")
    require(content_hash(package["metadata"], sha(body)) == package["content_hash"],
            "content_hash_mismatch", "Metadata or paper differs from the PoW commitment.")
    problems = poa.sample(pow.seed(proof_hash), epoch["poa_policy"])
    results = poa.verify_all(problems, package["answers"])
    return {"paper_id": package["content_hash"], "body": body,
            "proof": {"protocol": PROTOCOL, "verifier": VERIFIER, "epoch_hash": package["epoch_hash"],
                      "pow_hash": proof_hash.hex(), "poa_seed": pow.seed(proof_hash).hex(),
                      "problems": problems, "results": results, "experimental": True,
                      "package": package}}


def prepare(paper, meta, repository_id, submitter_id, epoch, epoch_hash, source=None):
    paper_bytes(paper)
    metadata(meta)
    result = {"protocol": PROTOCOL, "repository_id": repository_id, "submitter_id": submitter_id,
              "epoch_id": epoch["epoch_id"], "epoch_hash": epoch_hash, "metadata": meta,
              "paper_sha256": sha(paper), "content_hash": content_hash(meta, sha(paper)),
              "body": source or {"kind": "inline", "text": paper.decode("utf-8")},
              "nonce": "0000000000000000", "answers": []}
    validate_package(result)
    return result
