"""Read sealed PR commits as bounded data, never as executable checkout contents."""
import re
from contextlib import nullcontext
from pathlib import Path

from . import PR_PROTOCOLS, PROTOCOL_V5, PROTOCOL_V6
from .codec import canonical, decimal, fields, loads, read_json, sha, utcnow
from .errors import require
from .github import repository_name, wall_timeout
from .protocol import Context, load_package, pr_protocol, verify, verify_pow
from .protocol_v3 import metadata_file

DIRECTORY = re.compile(r"submissions/[0-9a-f]{32}\Z")
SOURCE_FIELDS = ["repository", "head_repository", "head_repository_id", "head_sha", "base_sha"]


def source(snapshot):
    value = loads(snapshot["body"])
    fields(value, SOURCE_FIELDS)
    repository_name(value["repository"])
    repository_name(value["head_repository"])
    decimal(value["head_repository_id"], 1)
    for key in ("head_sha", "base_sha"):
        require(isinstance(value[key], str) and re.fullmatch(r"[0-9a-f]{40}", value[key]), "invalid_snapshot", "Expected an immutable Git commit SHA.")
    return value


def capture(pr, repository, repository_id, now=None):
    require(pr.get("draft") is False and pr.get("state") == "open"
            and str(pr.get("title", "")).startswith("[preprint] "), "not_submission", "Expected a ready preprint PR.")
    require(str(pr["base"]["repo"]["id"]) == repository_id and pr["base"]["repo"]["full_name"] == repository,
            "event_mismatch", "PR targets another repository.")
    head = pr["head"]
    require(head.get("repo") is not None and head["repo"].get("private") is False,
            "private_source", "PR source must be an available public fork.")
    raw = canonical({"repository": repository, "head_repository": head["repo"]["full_name"],
                     "head_repository_id": str(head["repo"]["id"]), "head_sha": head["sha"], "base_sha": pr["base"]["sha"]})
    snapshot = {"repository_id": repository_id, "issue_id": str(pr["id"]), "issue_number": str(pr["number"]),
                "submitter_id": str(pr["user"]["id"]), "submitter_login": pr["user"].get("login"),
                "received_at": now or utcnow(), "mode": "pull_request",
                "request_sha256": sha(raw), "body": raw.decode()}
    from .archive import snapshot_key
    snapshot_key(snapshot)
    source(snapshot)
    return snapshot


def event_snapshot(event, repository, repository_id, now=None):
    require(event.get("action") in ("opened", "ready_for_review")
            and event.get("repository", {}).get("full_name") == repository
            and str(event["repository"]["id"]) == repository_id,
            "event_mismatch", "Expected an original ready PR event in this repository.")
    return capture(event["pull_request"], repository, repository_id, now)


def read_package(snapshot, github):
    origin = source(snapshot)
    # Resolve the stable identity without following redirects or rewriting the sealed source.
    repo = github.repository_by_id(origin["head_repository_id"])
    require(isinstance(repo, dict) and str(repo.get("id")) == origin["head_repository_id"] and repo.get("private") is False,
            "source_mismatch", "PR source repository identity changed.")
    current_repository = repository_name(repo.get("full_name"))
    # Compare exact objects, never the PR's potentially edited branch.
    compare = github.request("GET", "/repos/" + current_repository + "/compare/"
                             + origin["base_sha"] + "..." + origin["head_sha"], limit=24_000_000)
    require(compare.get("base_commit", {}).get("sha") == origin["base_sha"], "source_mismatch", "PR base commit mismatch.")
    files = compare.get("files")
    require(isinstance(files, list) and 3 <= len(files) <= 23,
            "submission_files", "A PR must add one manuscript directory with at most 20 images.")
    names = []
    for item in files:
        name = item.get("filename")
        require(item.get("status") == "added" and isinstance(name, str), "submission_files", "Submission PRs may only add files.")
        names.append(name)
    directories = {"/".join(name.split("/")[:2]) for name in names}
    require(len(directories) == 1, "submission_files", "Submit exactly one manuscript directory per PR.")
    directory = next(iter(directories))
    require(DIRECTORY.fullmatch(directory), "unsafe_path", "Use submissions/<32 lowercase hex characters>/.")
    def get(relative, cap, data=False, image=False):
        return github.fetch_file({"kind": "github", "repository": current_repository,
                                  "commit": origin["head_sha"], "path": directory + "/" + relative},
                                 cap, image=image, data=data)
    package = load_package(get("submission.json", 1_000_000, data=True))
    require(isinstance(package, dict), "invalid_fields", "Submission package must be an object.")
    pr_protocol(package.get("protocol")).validate_package(package)
    expected = {directory + "/" + name for name in ("paper.md", "metadata.json", "submission.json")}
    expected.update(directory + "/" + e["path"] for e in package["assets"])
    require(len(names) == len(set(names)) and set(names) == expected,
            "submission_files", "The PR must contain exactly its declared manuscript, metadata, proof and images.")
    return package, get


def evaluate(snapshot, root, production=True, github=None, bundle=None):
    source(snapshot)
    context = Context(snapshot["repository_id"], snapshot["submitter_id"], snapshot["received_at"])
    with wall_timeout(120) if github is not None else nullcontext():
        if github is not None:
            package, get = read_package(snapshot, github)
        else:
            require(not production and isinstance(bundle, dict), "trusted_context_required", "Production PR validation requires sealed Git objects.")
            fields(bundle, ["package", "paper", "metadata", "assets"])
            package = bundle["package"]
        require(package["protocol"] in PR_PROTOCOLS, "protocol_version", "New submissions require a versioned PR package.")
        if production:
            current = read_json(Path(root) / "config/production.json").get("protocol")
            if current in (PROTOCOL_V5, PROTOCOL_V6):
                require(package["protocol"] == current, "protocol_version", "New PR submissions must use the current published WitnessBench protocol.")
        verify_pow(package, root, context, production)
        if github is not None:
            meta = get("metadata.json", 60_000, data=True)
            body = get("paper.md", pr_protocol(package["protocol"]).MAX_MATERIAL)
            images = {e["path"]: get(e["path"], int(e["size"]), image=True) for e in package["assets"]}
        else:
            meta, body, images = bundle["metadata"], bundle["paper"], bundle["assets"]
        require(meta == canonical(metadata_file(package)) + b"\n", "metadata_mismatch", "metadata.json must exactly match canonical submission metadata and homepage display fields.")
        return verify(package, root, context, production, supplied_body=body, supplied_assets=images)
