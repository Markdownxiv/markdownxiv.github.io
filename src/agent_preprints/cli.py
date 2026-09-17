import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from . import poa, pow, PROTOCOL_V2
from .archive import capture, process, public_receipt
from .codec import MAX_PAPER, canonical, loads, read_json, sha, utcnow, write_json
from .epochs import epoch_path, initialize, load_epoch, rotate, validate_epoch
from .errors import Rejection, require
from .github import GitHub, NoRedirect, bounded_read, repository_name, wall_timeout
from .protocol import Context, prepare, verify, verify_pow
from .site import build, site_address


def _emit(value):
    print(canonical(value).decode("utf-8"))


def _client_context(package, at=None):
    return Context(package["repository_id"], package["submitter_id"], at or utcnow())


def _local_assets(args, package):
    from .assets import read_local
    directory = getattr(args, "assets_dir", None)
    if directory is None and getattr(args, "paper", None):
        directory = Path(args.paper).parent
    return ({e["path"]: read_local(directory, e["path"]) for e in package.get("assets", [])}
            if directory is not None else None)


def download_challenge(site, output):
    address = site_address(site)
    require(address.hostname.endswith(".github.io"), "invalid_site_url", "v1 challenge downloads require an official github.io Pages origin.")
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
    if epoch["protocol"] == PROTOCOL_V2:
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
        cmd = sub.add_parser(name, help="Measure the local one-thread reference miner")
        cmd.add_argument("--seconds", type=int, default=10)
        cmd.add_argument("--cpu")
        cmd.add_argument("--conditions", required=True)
        cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("init-production", help="Write local production configuration; never pushes")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--calibration", required=True)
    cmd.add_argument("--repository", required=True)
    cmd.add_argument("--repository-id", required=True)
    cmd.add_argument("--site-url", required=True)
    cmd = sub.add_parser("rotate")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--dev", action="store_true")
    cmd.add_argument("--repository-id", default="1")
    cmd.add_argument("--protocol", choices=("v1", "v2"), help="New development roots default to v1 for compatibility; use v2 explicitly")
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
    cmd = sub.add_parser("format-issue")
    cmd.add_argument("--package", required=True)
    cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("migrate", help="Add local legacy work aliases; never pushes")
    cmd.add_argument("--root", default=".")
    for name in ("mine", "verify-pow", "questions", "pack", "verify"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--root", default=".")
        cmd.add_argument("--package", required=True)
        cmd.add_argument("--dev", action="store_true")
        if name in ("mine", "questions", "pack"):
            cmd.add_argument("--out", required=True)
        if name == "mine":
            cmd.add_argument("--checkpoint", required=True)
            cmd.add_argument("--max-seconds", type=float)
        if name == "pack":
            cmd.add_argument("--answers", required=True)
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
    cmd = sub.add_parser("status")
    cmd.add_argument("--repository", required=True)
    cmd.add_argument("--issue", required=True, type=int)
    cmd.add_argument("--wait-seconds", type=int, default=0)
    return p


def execute(args):
    command = args.command
    if command in ("calibrate", "benchmark"):
        measurement = pow.calibrate(args.seconds, args.cpu, args.conditions)
        write_json(args.out, measurement)
        _emit(measurement)
    elif command == "init-production":
        cid = initialize(args.root, read_json(args.calibration), args.repository, args.repository_id, args.site_url)
        config_path = Path(args.root) / "config/production.json"
        config = read_json(config_path)
        config["protocol"] = PROTOCOL_V2
        write_json(config_path, config)
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
    elif command == "format-issue":
        from .envelope import format_submission
        from .protocol import validate_package
        package = read_json(args.package, 60000)
        validate_package(package)
        Path(args.out).write_text(format_submission(package), encoding="utf-8")
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
        if epoch["protocol"] == PROTOCOL_V2:
            from . import assets, taxonomy
            entries, _ = assets.collect_local(body, args.assets_dir or Path(args.paper).parent)
            kwargs = {"entries": entries, "asset_source": read_json(args.asset_source) if args.asset_source else None,
                      "catalog": taxonomy.load(args.root, epoch["taxonomy_hash"])}
        if command == "revise":
            from .works import path
            require(epoch["protocol"] == PROTOCOL_V2, "protocol_version", "Revisions require a v2 challenge.")
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
                    "Leave 8192 bytes for certificates before mining; use a pinned manuscript source or shorter metadata.")
        write_json(args.out, result)
        _emit({"content_hash": result["content_hash"], "paper_sha256": result["paper_sha256"]})
    elif command in ("mine", "verify-pow", "questions", "pack", "verify"):
        package = read_json(args.package, 60_000)
        context = _client_context(package)
        if command == "mine":
            from .protocol import validate_package
            validate_package(package)
            epoch = load_epoch(args.root, package["epoch_id"], package["epoch_hash"], context.received_at,
                               package["repository_id"], not args.dev)
            require(epoch["protocol"] == package["protocol"], "protocol_version", "Package and epoch protocols differ.")
            if package["protocol"] == PROTOCOL_V2:
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
                value = {"poa_seed": pow.seed(digest).hex(), "problems": poa.sample(pow.seed(digest), epoch["poa_policy"])}
                write_json(args.out, value)
            else:
                value = {"valid": True, "pow_hash": digest.hex()}
            _emit(value)
        else:
            if command == "pack":
                package["answers"] = read_json(args.answers)
            result = verify(package, args.root, context, not args.dev,
                            supplied_body=Path(args.paper).read_bytes() if args.paper else None,
                            supplied_assets=_local_assets(args, package))
            if command == "pack":
                write_json(args.out, package)
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
    elif command == "build":
        _emit(build(args.root, args.out, args.base_path, social=read_json(args.social, 4_000_000) if args.social else None))
    elif command == "submit":
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        require(token, "auth_required", "Set the participant's GH_TOKEN locally; tokens are never part of submissions.")
        github = GitHub(token)
        repository = github.repository(args.repository)
        require(repository.get("private") is False, "private_repository", "The target must be public.")
        user = github.request("GET", "/user")
        package = read_json(args.package, 60_000)
        context = Context(str(repository["id"]), str(user["id"]), utcnow())
        verify(package, args.root, context, True, github.fetch_paper_v2,
               Path(args.paper).read_bytes() if args.paper else None, github.fetch_asset, _local_assets(args, package))
        # On a transport ambiguity, do not automatically create a second Issue.
        from .envelope import format_submission
        title = package["metadata"]["title"]
        if package.get("intent", {}).get("kind") == "revision":
            title = package["intent"]["work_id"] + " · " + title
        result = github.create_issue(args.repository, format_submission(package), package["content_hash"], title=title)
        _emit({"issue_number": str(result["number"]), "issue_id": str(result["id"]), "url": result["html_url"]})
    elif command == "status":
        github = GitHub(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
        require(args.issue > 0 and 0 <= args.wait_seconds <= 3600, "input_limit", "Invalid issue or wait limit.")
        from .automation import parse_comment
        deadline, delay = time.monotonic() + args.wait_seconds, 2
        while True:
            found = None
            for page in range(1, 11):
                comments = github.comments(args.repository, args.issue, page)
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
        _emit({"status": "error", **exc.as_dict()})
        return 2
    except (OSError, ValueError, KeyError) as exc:
        # No raw API bodies, tokens, or arbitrary exception text in machine output.
        _emit({"status": "error", "error_code": "local_io_or_format", "message": "Check local files and arguments; no remote success was recorded."})
        return 2
    return 0
