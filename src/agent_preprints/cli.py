import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from . import poa, pow
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
    cmd = sub.add_parser("challenge")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--site")
    cmd.add_argument("--dev", action="store_true")
    cmd = sub.add_parser("prepare")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--paper", required=True)
    cmd.add_argument("--metadata", required=True)
    cmd.add_argument("--user-id", required=True)
    cmd.add_argument("--repository-id", required=True)
    cmd.add_argument("--source", help="JSON descriptor of an immutable GitHub source")
    cmd.add_argument("--out", required=True)
    cmd.add_argument("--dev", action="store_true")
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
    cmd = sub.add_parser("archive-demo", help="Local DEVELOPMENT archive only; no network calls")
    cmd.add_argument("--root", required=True)
    cmd.add_argument("--package", required=True)
    cmd.add_argument("--issue-id", default="1")
    cmd.add_argument("--issue-number", default="1")
    cmd.add_argument("--paper")
    cmd = sub.add_parser("build")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--out", default="_site")
    cmd.add_argument("--base-path")
    cmd = sub.add_parser("submit")
    cmd.add_argument("--root", default=".")
    cmd.add_argument("--repository", required=True)
    cmd.add_argument("--package", required=True)
    cmd.add_argument("--paper")
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
        _emit({"calibration_id": cid, "status": "configured_locally"})
    elif command == "rotate":
        _emit(rotate(args.root, development=args.dev, repository_id=args.repository_id) or {"status": "calibration_required"})
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
    elif command == "prepare":
        latest = read_json(Path(args.root) / "challenges" / "latest.json")
        require(latest["status"] == "active", "calibration_required", "No active challenge.")
        epoch = load_epoch(args.root, latest["epoch_id"], latest["epoch_hash"], utcnow(), args.repository_id, not args.dev)
        result = prepare(Path(args.paper).read_bytes(), read_json(args.metadata), args.repository_id, args.user_id,
                         epoch, latest["epoch_hash"], read_json(args.source) if args.source else None)
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
            head = pow.header(package["repository_id"], package["epoch_hash"], package["submitter_id"], package["content_hash"])
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
                            supplied_body=Path(args.paper).read_bytes() if args.paper else None)
            if command == "pack":
                write_json(args.out, package)
            _emit({"valid": True, "paper_id": result["paper_id"], "results": result["proof"]["results"]})
    elif command == "archive-demo":
        package_text = Path(args.package).read_text(encoding="utf-8")
        package = loads(package_text)
        epoch = read_json(epoch_path(args.root, package["epoch_id"]))
        require(epoch["profile"] == "development", "development_required", "archive-demo only accepts development epochs.")
        issue = {"id": args.issue_id, "number": args.issue_number, "user": {"id": package["submitter_id"]},
                 "title": "[preprint] local-demo", "body": package_text, "created_at": utcnow()}
        snapshot = capture(issue, package["repository_id"], "opened")
        result = process(args.root, snapshot, production=False,
                         supplied_body=Path(args.paper).read_bytes() if args.paper else None)
        _emit(public_receipt(result))
        require(result["archived"], result["error_code"], result["message"])
    elif command == "build":
        _emit(build(args.root, args.out, args.base_path))
    elif command == "submit":
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        require(token, "auth_required", "Set the participant's GH_TOKEN locally; tokens are never part of submissions.")
        github = GitHub(token)
        repository = github.repository(args.repository)
        require(repository.get("private") is False, "private_repository", "The target must be public.")
        user = github.request("GET", "/user")
        package = read_json(args.package, 60_000)
        context = Context(str(repository["id"]), str(user["id"]), utcnow())
        verify(package, args.root, context, True, github.fetch_paper,
               Path(args.paper).read_bytes() if args.paper else None)
        # On a transport ambiguity, do not automatically create a second Issue.
        result = github.create_issue(args.repository, canonical(package).decode(), package["content_hash"])
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
