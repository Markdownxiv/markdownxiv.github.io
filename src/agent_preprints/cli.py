import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from . import poa, poi, pow, PROTOCOL_V2, PROTOCOL_V3, PROTOCOL_V4, PROTOCOL_V5, PR_PROTOCOLS
from .archive import capture, process, public_receipt
from .codec import MAX_PAPER, canonical, loads, read_json, sha, utcnow, write_json
from .epochs import epoch_path, initialize, load_epoch, rotate, validate_epoch
from .errors import Rejection, require
from .github import GitHub, NoRedirect, bounded_read, repository_name, wall_timeout
from .protocol import Context, pr_protocol, prepare, read_package, verify, verify_pow
from .site import build, site_address


def _emit(value):
    print(canonical(value).decode("utf-8"))


def _client_context(package, at=None):
    return Context(package["repository_id"], package["submitter_id"], at or utcnow())


def _local_assets(args, package):
    from .assets import read_local, MAX_IMAGE
    directory = getattr(args, "assets_dir", None)
    if directory is None and getattr(args, "paper", None):
        directory = Path(args.paper).parent
    cap = pr_protocol(package["protocol"]).MAX_MATERIAL if package["protocol"] in (PROTOCOL_V4, PROTOCOL_V5) else MAX_IMAGE
    return ({e["path"]: read_local(directory, e["path"], cap) for e in package.get("assets", [])}
            if directory is not None else None)


def participant_token(required=False):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
        token = result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        token = None
    require(token or not required, "auth_required", "Sign in with gh auth login, or provide a participant GH_TOKEN locally.")
    return token


def download_challenge(site, output):
    address = site_address(site)
    require(address.hostname.endswith(".github.io"), "invalid_site_url", "Challenge downloads require an official github.io Pages origin.")
    base = site.rstrip("/") + "/"
    output = Path(output)
    opener = urllib.request.build_opener(NoRedirect())
    def get(relative):
        try:
            with wall_timeout(20):
                with opener.open(base + relative, timeout=10) as response:
                    return bounded_read(response, 1_000_000, time.monotonic() + 20)
        except OSError as exc:
            raise Rejection("network_error", "Could not download the Pages challenge.", True) from exc
    latest = loads(get("challenges/latest.json"), 1_000_000)
    require(latest.get("status") == "active", "calibration_required", "Site has no active production challenge.")
    path = epoch_path(output, latest["epoch_id"])
    require(latest["path"] == "epochs/" + latest["epoch_id"] + ".json", "unknown_epoch", "Unsafe epoch location.")
    raw = get("challenges/" + latest["path"])
    require(sha(raw) == latest["epoch_hash"], "epoch_hash_mismatch", "Downloaded epoch hash mismatch.")
    epoch = loads(raw)
    validate_epoch(epoch)
    if epoch["protocol"] in (PROTOCOL_V2, *PR_PROTOCOLS):
        from .codec import hexhash
        digest = hexhash(epoch["taxonomy_hash"])
        catalog = get("taxonomy/" + digest + ".json")
        require(sha(catalog) == digest, "taxonomy_mismatch", "Downloaded taxonomy hash mismatch.")
        target = output / "taxonomy" / (digest + ".json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(catalog)
        write_json(target.parent / "latest.json", {"taxonomy_hash": digest})
    calibration = get("challenges/calibrations/" + epoch["calibration_id"] + ".json")
    require(sha(calibration) == epoch["calibration_id"], "calibration_required", "Downloaded calibration hash mismatch.")
    config = loads(get("config/production.json"))
    registry = loads(get("challenges/registry.json"), 1_000_000)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == raw, "immutable_conflict", "Cached epoch bytes differ.")
    path.write_bytes(raw)
    calpath = output / "challenges" / "calibrations" / (epoch["calibration_id"] + ".json")
    calpath.parent.mkdir(parents=True, exist_ok=True)
    calpath.write_bytes(calibration)
    write_json(output / "challenges" / "latest.json", latest)
    write_json(output / "challenges" / "registry.json", registry)
    write_json(output / "config" / "production.json", config)
    load_epoch(output, epoch["epoch_id"], latest["epoch_hash"], utcnow(), epoch["repository_id"])
    return epoch


def parser():
    p = argparse.ArgumentParser(prog="preprints", description="Agent-native Markdown preprint admission")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("calibrate", "benchmark"):
        cmd = sub.add_parser(name, help="Measure the local single-thread Proof of Work implementation")
        cmd.add_argument("--seconds", type=int, default=10)
        cmd.add_argument("--cpu")
        cmd.add_argument("--conditions", required=True)
        cmd.add_argument("--out", required=True)
        cmd.add_argument("--expected-seconds", type=int, choices=(30, 300), default=30)
    cmd = sub.add_parser("init-production", help="Write local production configuration; never pushes")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--calibration", required=True)
    cmd.add_argument("--repository", required=True)
    cmd.add_argument("--repository-id", required=True)
    cmd.add_argument("--site-url", required=True)
    cmd.add_argument("--protocol", choices=("v1", "v2", "v3", "v4", "v5"), default="v5")
    cmd = sub.add_parser("rotate")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--dev", action="store_true")
    cmd.add_argument("--repository-id", default="1")
    cmd.add_argument("--protocol", choices=("v1", "v2", "v3", "v4", "v5"), help="Choose a development protocol; current submissions use v5")
    cmd = sub.add_parser("challenge")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--site")
    cmd.add_argument("--dev", action="store_true")
    for name in ("prepare", "revise"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--root", default=".")
        cmd.add_argument("--paper", required=True)
        cmd.add_argument("--metadata", required=True)
        cmd.add_argument("--user-id", required=True)
        cmd.add_argument("--repository-id", required=True)
        cmd.add_argument("--source", help="JSON descriptor of an immutable GitHub source")
        cmd.add_argument("--assets-dir", help="Local image base directory, defaults to manuscript directory")
        cmd.add_argument("--asset-source", help="Pinned source for images when manuscript is inline")
        cmd.add_argument("--out", required=True)
        cmd.add_argument("--dev", action="store_true")
        if name == "revise":
            cmd.add_argument("--work-id", required=True)
            cmd.add_argument("--change-summary", required=True)
    cmd = sub.add_parser("work", help="Download a work registry before preparing a revision")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--site", required=True)
    cmd.add_argument("--work-id", required=True)
    cmd = sub.add_parser("categories")
    cmd.add_argument("--root", default=".")
    cmd = sub.add_parser("format-pr")
    cmd.add_argument("--package", required=True)
    cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("migrate", help="Add local legacy work aliases; never pushes")
    cmd.add_argument("--root", default=".")
    for name in ("pow", "verify-pow", "questions", "pack", "verify"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--root", default=".")
        cmd.add_argument("--package", required=True)
        cmd.add_argument("--dev", action="store_true")
        if name in ("pow", "questions", "pack"):
            cmd.add_argument("--out", required=True)
        if name == "questions":
            cmd.add_argument("--markdown", help="Write English WitnessBench problem statements alongside the JSON")
        if name == "pow":
            cmd.add_argument("--checkpoint", required=True)
            cmd.add_argument("--max-seconds", type=float)
        if name == "pack":
            cmd.add_argument("--answers", required=True)
            cmd.add_argument("--homepages", help="JSON array of author homepage display URLs; does not change Proof of Work")
        if name in ("pack", "verify"):
            cmd.add_argument("--paper", help="Local bytes required for offline verification of a reference source")
            cmd.add_argument("--assets-dir")
    cmd = sub.add_parser("archive-demo", help="Local DEVELOPMENT archive only; no network calls")
    cmd.add_argument("--root", required=True)
    cmd.add_argument("--package", required=True)
    cmd.add_argument("--issue-id", default="1")
    cmd.add_argument("--issue-number", default="1")
    cmd.add_argument("--paper")
    cmd.add_argument("--assets-dir")
    cmd = sub.add_parser("archive-pr-demo", help="Archive a local development PR bundle without network access")
    cmd.add_argument("--root", required=True)
    cmd.add_argument("--package", required=True)
    cmd.add_argument("--paper", required=True)
    cmd.add_argument("--assets-dir")
    cmd.add_argument("--pr", default="1")
    cmd = sub.add_parser("build")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--out", default="_site")
    cmd.add_argument("--base-path")
    cmd.add_argument("--social", help="Optional ephemeral social snapshot JSON")
    cmd = sub.add_parser("submit")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--repository", required=True)
    cmd.add_argument("--package", required=True)
    cmd.add_argument("--paper")
    cmd.add_argument("--assets-dir")
    cmd.add_argument("--checkpoint", help="PR creation checkpoint, defaults beside the package")
    cmd.add_argument("--draft", action="store_true")
    cmd = sub.add_parser("status")
    cmd.add_argument("--repository", required=True)
    cmd.add_argument("--pr", required=True, type=int)
    cmd.add_argument("--wait-seconds", type=int, default=0)
    return p


def execute(args):
    command = args.command
    if command in ("calibrate", "benchmark"):
        measurement = pow.calibrate(args.seconds, args.cpu, args.conditions, args.expected_seconds)
        write_json(args.out, measurement)
        _emit(measurement)
    elif command == "init-production":
        cid = initialize(args.root, read_json(args.calibration), args.repository, args.repository_id, args.site_url,
                         "agent-preprints-" + args.protocol)
        from . import taxonomy
        taxonomy.ensure(args.root)
        _emit({"calibration_id": cid, "status": "configured_locally"})
    elif command == "rotate":
        _emit(rotate(args.root, development=args.dev, repository_id=args.repository_id,
                     protocol="agent-preprints-" + args.protocol if args.protocol else None) or {"status": "calibration_required"})
    elif command == "migrate":
        from .archive import lock
        from .works import migrate, recover
        with lock(args.root):
            recover(args.root)
            _emit({"works": migrate(args.root)})
    elif command == "categories":
        from . import taxonomy
        _emit(taxonomy.load(args.root, taxonomy.ensure(args.root)))
    elif command == "format-pr":
        from .pr_client import format_pr
        from .protocol import validate_package
        package = read_package(args.package)
        validate_package(package)
        require(package["protocol"] in PR_PROTOCOLS, "protocol_version", "PR formatting requires a supported PR package.")
        Path(args.out).write_text(format_pr(package), encoding="utf-8")
        _emit({"status": "formatted", "bytes": str(Path(args.out).stat().st_size)})
    elif command == "work":
        from .works import path
        from .protocol_v2 import work_id
        address = site_address(args.site)
        require(address.hostname.endswith(".github.io"), "invalid_site_url", "Use an official github.io Pages origin.")
        wid = work_id(args.work_id)
        with wall_timeout(20):
            with urllib.request.build_opener(NoRedirect()).open(args.site.rstrip("/") + "/works/" + wid[3:] + ".json", timeout=10) as response:
                work = loads(bounded_read(response, 1_000_000, time.monotonic() + 20), 1_000_000)
        require(work["work_id"] == wid, "invalid_work_id", "Downloaded work ID mismatch.")
        write_json(path(args.root, wid), work)
        _emit(work)
    elif command == "challenge":
        if args.site:
            require(not args.dev, "production_required", "Remote development challenges are unsupported.")
            epoch = download_challenge(args.site, args.root)
        else:
            latest = read_json(Path(args.root) / "challenges" / "latest.json")
            require(latest["status"] == "active", "calibration_required", "No active challenge; production calibration required.")
            ep = read_json(epoch_path(args.root, latest["epoch_id"]))
            epoch = load_epoch(args.root, latest["epoch_id"], latest["epoch_hash"], utcnow(), ep["repository_id"], not args.dev)
        _emit(epoch)
    elif command in ("prepare", "revise"):
        latest = read_json(Path(args.root) / "challenges" / "latest.json")
        require(latest["status"] == "active", "calibration_required", "No active challenge.")
        epoch = load_epoch(args.root, latest["epoch_id"], latest["epoch_hash"], utcnow(), args.repository_id, not args.dev)
        body = Path(args.paper).read_bytes()
        kwargs = {}
        if epoch["protocol"] in (PROTOCOL_V2, *PR_PROTOCOLS):
            from . import assets, taxonomy
            limits = {"max_image": 8_000_000, "max_total": 8_000_000} if epoch["protocol"] in (PROTOCOL_V4, PROTOCOL_V5) else {}
            entries, _ = assets.collect_local(body, args.assets_dir or Path(args.paper).parent, **limits)
            kwargs = {"entries": entries, "asset_source": read_json(args.asset_source) if args.asset_source else None,
                      "catalog": taxonomy.load(args.root, epoch["taxonomy_hash"])}
        if command == "revise":
            from .works import path
            require(epoch["protocol"] in (PROTOCOL_V2, *PR_PROTOCOLS), "protocol_version", "Revisions require a versioned challenge.")
            work = read_json(path(args.root, args.work_id))
            require(work["owner_id"] == args.user_id and work["repository_id"] == args.repository_id,
                    "revision_unauthorized", "The original submitter must prepare this revision.")
            kwargs["submission_intent"] = {"kind": "revision", "work_id": work["work_id"],
                                           "parent_hash": work["versions"][-1]["content_hash"], "change_summary": args.change_summary}
        result = prepare(body, read_json(args.metadata), args.repository_id, args.user_id,
                         epoch, latest["epoch_hash"], read_json(args.source) if args.source else None, **kwargs)
        if epoch["protocol"] == PROTOCOL_V2:
            from .envelope import format_submission
            require(len(format_submission(result).encode()) <= 60000 - 8192, "input_limit",
                    "Leave 8192 bytes for certificates before computing Proof of Work; use shorter metadata.")
        write_json(args.out, result)
        report = {"content_hash": result["content_hash"], "paper_sha256": result["paper_sha256"]}
        if epoch["protocol"] in PR_PROTOCOLS:
            from .protocol_v3 import material_size
            report["material_bytes"] = str(material_size(result))
            report["material_limit"] = str(pr_protocol(epoch["protocol"]).MAX_MATERIAL)
        _emit(report)
    elif command in ("pow", "verify-pow", "questions", "pack", "verify"):
        package = read_package(args.package)
        context = _client_context(package)
        if command == "pow":
            from .protocol import validate_package
            validate_package(package)
            epoch = load_epoch(args.root, package["epoch_id"], package["epoch_hash"], context.received_at,
                               package["repository_id"], not args.dev)
            require(epoch["protocol"] == package["protocol"], "protocol_version", "Package and epoch protocols differ.")
            if package["protocol"] in (PROTOCOL_V2, *PR_PROTOCOLS):
                from . import taxonomy
                require(package["metadata"]["taxonomy_hash"] == epoch["taxonomy_hash"], "taxonomy_mismatch", "Use the epoch's taxonomy.")
                taxonomy.validate_categories(package["metadata"], taxonomy.load(args.root, epoch["taxonomy_hash"]))
            head = pow.header(package["repository_id"], package["epoch_hash"], package["submitter_id"], package["content_hash"], package["protocol"])
            def progress(count, elapsed):
                rate = count / elapsed
                expected = (1 << 256) / int(epoch["target"], 16) / rate
                print(f"{count} attempts; {rate:.0f} hashes/s; local expected total {expected:.1f}s", file=sys.stderr)
            package["nonce"] = pow.mine(head, epoch["target"], args.checkpoint, args.max_seconds, progress)
            write_json(args.out, package)
            _emit({"nonce": package["nonce"], "pow_hash": pow.digest(head, package["nonce"]).hex()})
        elif command in ("questions", "verify-pow"):
            epoch, digest = verify_pow(package, args.root, context, not args.dev)
            if command == "questions":
                engine = poi if package["protocol"] == PROTOCOL_V5 else poa
                seed = pow.seed(digest, package["protocol"])
                value = {"poa_seed": seed.hex(), "problems": engine.sample(seed, epoch["poa_policy"])}
                write_json(args.out, value)
                if args.markdown:
                    require(package["protocol"] == PROTOCOL_V5, "protocol_version", "English WitnessBench statements require v5.")
                    Path(args.markdown).write_text(poi.markdown(value["problems"]), encoding="utf-8")
            else:
                value = {"valid": True, "pow_hash": digest.hex()}
            _emit(value)
        else:
            if command == "pack":
                if package["protocol"] == PROTOCOL_V5:
                    with Path(args.answers).open("rb") as stream:
                        package["answers"] = loads(stream.read(1_000_001), 1_000_000, stringify_integers=True)
                else:
                    package["answers"] = read_json(args.answers)
                if args.homepages:
                    require(package["protocol"] in PR_PROTOCOLS, "protocol_version", "Homepage display fields require a PR protocol.")
                    package["author_homepages"] = read_json(args.homepages)
            result = verify(package, args.root, context, not args.dev,
                            supplied_body=Path(args.paper).read_bytes() if args.paper else None,
                            supplied_assets=_local_assets(args, package))
            if command == "pack":
                write_json(args.out, package)
                if package["protocol"] in PR_PROTOCOLS:
                    from .protocol_v3 import metadata_file
                    write_json(Path(args.out).parent / "metadata.json", metadata_file(package))
            _emit({"valid": True, "paper_id": result["paper_id"], "results": result["proof"]["results"]})
    elif command == "archive-demo":
        package_text = Path(args.package).read_text(encoding="utf-8")
        from .envelope import parse_submission
        package = parse_submission(package_text)
        epoch = read_json(epoch_path(args.root, package["epoch_id"]))
        require(epoch["profile"] == "development", "development_required", "archive-demo only accepts development epochs.")
        issue = {"id": args.issue_id, "number": args.issue_number, "user": {"id": package["submitter_id"]},
                 "title": "[preprint] local-demo", "body": package_text, "created_at": utcnow()}
        snapshot = capture(issue, package["repository_id"], "opened")
        result = process(args.root, snapshot, production=False,
                         supplied_body=Path(args.paper).read_bytes() if args.paper else None,
                         supplied_assets=_local_assets(args, package))
        _emit(public_receipt(result))
        require(result["archived"], result["error_code"], result["message"])
    elif command == "archive-pr-demo":
        from .pull_requests import capture as capture_pr
        from .protocol_v3 import metadata_file
        package = read_package(args.package)
        epoch = read_json(epoch_path(args.root, package["epoch_id"]))
        require(package["protocol"] in PR_PROTOCOLS and epoch["profile"] == "development", "development_required", "This demo only accepts development PR proofs.")
        repository = "local/demo"
        pr = {"id": args.pr, "number": args.pr, "user": {"id": package["submitter_id"]}, "title": "[preprint] development",
              "state": "open", "draft": False, "base": {"sha": "a" * 40, "repo": {"id": package["repository_id"], "full_name": repository}},
              "head": {"sha": "b" * 40, "repo": {"id": "3", "full_name": "participant/demo", "private": False}}}
        snapshot = capture_pr(pr, repository, package["repository_id"])
        result = process(args.root, snapshot, False, supplied_body={"package": package, "paper": Path(args.paper).read_bytes(),
                         "metadata": canonical(metadata_file(package)) + b"\n", "assets": _local_assets(args, package) or {}})
        _emit(public_receipt(result))
        require(result["archived"], result["error_code"], result["message"])
    elif command == "build":
        _emit(build(args.root, args.out, args.base_path, social=read_json(args.social, 4_000_000) if args.social else None))
    elif command == "submit":
        token = participant_token(required=True)
        github = GitHub(token)
        package = read_package(args.package)
        require(args.paper, "body_unavailable", "PR submission requires --paper and its local image files.")
        from .pr_client import submit
        result = submit(github, args.repository, package, args.root, Path(args.paper).read_bytes(),
                        _local_assets(args, package) or {}, args.checkpoint or str(Path(args.package).with_suffix(".pr-checkpoint.json")), args.draft)
        _emit({"pull_request_number": str(result["number"]), "pull_request_id": str(result["id"]), "url": result["html_url"]})
    elif command == "status":
        github = GitHub(participant_token())
        require(args.pr > 0 and 0 <= args.wait_seconds <= 3600, "input_limit", "Invalid PR number or wait limit.")
        from .automation import parse_comment
        deadline, delay = time.monotonic() + args.wait_seconds, 2
        while True:
            found = None
            for page in range(1, 11):
                comments = github.comments(args.repository, args.pr, page)
                for comment in comments:
                    receipt = parse_comment(comment)
                    if receipt:
                        found = receipt
                if len(comments) < 100:
                    break
            if found and (found["published"] or found["status"] == "rejected" or args.wait_seconds == 0):
                _emit(found)
                return
            if time.monotonic() >= deadline:
                _emit(found or {"status": "pending", "message": "No machine-readable bot receipt yet."})
                return
            time.sleep(min(delay, max(0, deadline - time.monotonic())))
            delay = min(30, delay * 2)


def main():
    try:
        execute(parser().parse_args())
    except Rejection as exc:
        failure = exc.as_dict()
        if exc.code == "mining_paused":
            failure.update(error_code="pow_paused", message="Proof of Work paused; checkpoint saved when supplied.")
        _emit({"status": "error", **failure})
        return 2
    except (OSError, ValueError, KeyError) as exc:
        # No raw API bodies, tokens, or arbitrary exception text in machine output.
        _emit({"status": "error", "error_code": "local_io_or_format", "message": "Check local files and arguments; no remote success was recorded."})
        return 2
    return 0
