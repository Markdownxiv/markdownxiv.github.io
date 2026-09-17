"""Production PR-only entry points. All executable code comes from the default branch."""
import argparse
import json
import os
from pathlib import Path

from .archive import atomic_json, evaluate, mark_deployed, process, public_receipt, receipt_path
from .automation import GitTransaction, _workflow_context, sync_receipts
from .codec import canonical, decimal, fields, read_json, timestamp, utcnow, write_json
from .epochs import rotate
from .errors import Rejection, require
from .pull_requests import capture, event_snapshot


def collect(root, github, repository, repository_id, branch, now=None):
    root, now = Path(root), now or utcnow()
    snapshots = []
    for path in sorted((root / "receipts").glob("*-pr-*.json")):
        record = read_json(path)
        attempts = int(record["attempts"])
        if record["status"] == "retryable" and attempts < 8:
            elapsed = (timestamp(now) - timestamp(record["last_attempt_at"] or now)).total_seconds()
            if elapsed >= min(86400, 60 * 2**attempts):
                snapshots.append(record["snapshot"])
        if len(snapshots) == 5:
            break
    cursor = root / "state/scan.json"
    page = int(read_json(cursor)["page"]) if cursor.exists() else 1
    for _ in range(2):
        pulls = github.request("GET", "/repos/" + repository + "/pulls?state=open&sort=created&direction=asc&per_page=100&page=" + str(page))
        require(isinstance(pulls, list) and len(pulls) <= 100, "github_response", "Invalid PR listing.")
        for pr in pulls:
            if pr.get("draft") is not False or pr.get("base", {}).get("ref") != branch or not str(pr.get("title", "")).startswith("[preprint] "):
                continue
            try:
                snapshot = capture(pr, repository, repository_id, now)
            except Rejection:
                continue
            if receipt_path(root, snapshot).exists():
                continue
            if len(snapshots) == 5:
                return snapshots, str(page)
            snapshots.append(snapshot)
        if len(pulls) < 100:
            page = 1
            break
        page += 1
    return snapshots, str(page)


def validate(root, snapshot, github):
    path = receipt_path(root, snapshot)
    if path.exists():
        record = read_json(path)
        if record["status"] != "retryable":
            return {"snapshot": record["snapshot"], "result": public_receipt(record)}
        snapshot = record["snapshot"]
    try:
        result = evaluate(snapshot, root, True, fetch_body=github)
        outcome = {"valid": True, "paper_id": result["paper_id"]}
    except Rejection as exc:
        outcome = exc.as_dict()
    return {"snapshot": snapshot, "result": outcome}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate-event", "collect", "ingest-event", "maintain", "finalize"))
    parser.add_argument("--root", default=".")
    parser.add_argument("--artifact", default=".work/validated.json")
    parser.add_argument("--manifest", default=".work/manifest.json")
    args = parser.parse_args()
    try:
        github, repository, repository_id, branch = _workflow_context()
        event = None
        if args.command in ("validate-event", "ingest-event"):
            require(os.environ.get("GITHUB_EVENT_NAME") == "pull_request_target", "event_mismatch", "Only trusted PR target events admit manuscripts.")
            event_file = Path(os.environ["GITHUB_EVENT_PATH"])
            require(event_file.stat().st_size <= 2_000_000, "input_limit", "Event payload is too large.")
            event = json.loads(event_file.read_bytes())
            require(event.get("pull_request", {}).get("base", {}).get("ref") == branch, "event_mismatch", "Submit to the default branch.")
            snapshot = event_snapshot(event, repository, repository_id)
        else:
            require(os.environ.get("GITHUB_REF") == "refs/heads/" + branch or args.command == "finalize",
                    "event_mismatch", "Maintenance requires the default branch.")
        if args.command == "validate-event":
            write_json(args.artifact, {"validated": [validate(args.root, snapshot, github)]})
            return 0
        if args.command == "collect":
            snapshots, page = collect(args.root, github, repository, repository_id, branch)
            write_json(args.artifact, {"validated": [validate(args.root, s, github) for s in snapshots], "next_page": page})
            return 0
        data = read_json(args.artifact, 1_000_000) if args.command in ("ingest-event", "maintain") else None
        if data is not None:
            fields(data, ["validated"] + (["next_page"] if args.command == "maintain" else []))
            require(isinstance(data["validated"], list) and len(data["validated"]) <= (5 if args.command == "maintain" else 1), "artifact_limit", "PR batch exceeds its limit.")
        if args.command == "maintain":
            decimal(data["next_page"], 1, 1_000_000)
        def mutate(root):
            from .archive import lock
            from .works import recover
            with lock(root):
                recover(root)
            results = []
            if args.command == "maintain":
                rotate(root)
                for item in data["validated"]:
                    candidate = item["snapshot"]
                    path = receipt_path(root, candidate)
                    if path.exists():
                        candidate = read_json(path)["snapshot"]
                    else:
                        number = candidate["issue_number"]
                        decimal(number, 1)
                        pr = github.request("GET", "/repos/" + repository + "/pulls/" + number)
                        if pr.get("draft") or pr.get("state") != "open":
                            continue
                        require(pr["base"]["ref"] == branch, "event_mismatch", "Recovery PR changed its target.")
                        # A cache cannot supply a historical observation time or a source identity.
                        candidate = capture(pr, repository, repository_id)
                    require(candidate["mode"] == "pull_request" and candidate["repository_id"] == repository_id,
                            "event_mismatch", "Only this repository's PR snapshots are accepted.")
                    results.append(public_receipt(process(root, candidate, True, fetch_body=github)))
                atomic_json(root / "state/scan.json", {"page": data["next_page"], "kind": "pull_request"})
            elif args.command == "ingest-event":
                # Seal the original event's head at first durable processing. Never trust artifact acceptance.
                candidate = event_snapshot(event, repository, repository_id)
                results.append(public_receipt(process(root, candidate, True, fetch_body=github)))
            else:
                if os.environ.get("DEPLOYMENT_RESULT") == "success":
                    config = read_json(root / "config/production.json")
                    mark_deployed(root, read_json(args.manifest), config["site_url"])
                sync_receipts(root, github, repository)
            return results
        commit, results = GitTransaction(args.root, branch).run(mutate)
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                output.write("sha=" + commit + "\n")
                deploy = args.command == "maintain" or any(r["archived"] and not r["published"] for r in results)
                output.write("needs_deploy=" + ("true" if deploy else "false") + "\n")
        print(canonical({"commit": commit, "receipts": results}).decode())
        return 0
    except Rejection as exc:
        print(canonical({"status": "error", **exc.as_dict()}).decode())
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
