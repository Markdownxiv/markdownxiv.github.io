"""Replay a fixed development certificate package without a solver or network."""
import argparse
import shutil
from pathlib import Path

from agent_preprints.archive import process, public_receipt
from agent_preprints.codec import canonical, read_json
from agent_preprints.errors import require
from agent_preprints.protocol import Context, read_package, verify
from agent_preprints.protocol_v5 import metadata_file
from agent_preprints.pull_requests import capture
from agent_preprints.site import build


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".demo-v5")
    args = parser.parse_args()
    root = Path(args.out).resolve()
    require(not root.exists() or not any(root.iterdir()), "invalid_output", "Use an empty demo directory.")
    source = Path(__file__).resolve().parents[1] / "tests/fixtures/witnessbench-development"
    shutil.copytree(source, root, dirs_exist_ok=True)
    package = read_package(root / "submission.json")
    moment = read_json(root / "experiment.json")["received_at"]
    body = (root / "paper.md").read_bytes()
    verify(package, root, Context("1", "2", moment), False, supplied_body=body, supplied_assets={})
    pr = {"id": "1", "number": "1", "user": {"id": "2", "login": "development-fixture"},
          "title": "[preprint] WitnessBench development", "state": "open", "draft": False,
          "base": {"sha": "a" * 40, "repo": {"id": "1", "full_name": "local/demo"}},
          "head": {"sha": "b" * 40, "repo": {"id": "3", "full_name": "participant/demo", "private": False}}}
    snapshot = capture(pr, "local/demo", "1", moment)
    receipt = process(root, snapshot, False, supplied_body={"package": package, "paper": body,
                      "metadata": canonical(metadata_file(package)) + b"\n", "assets": {}})
    require(receipt["archived"], receipt["error_code"], receipt["message"])
    build(root, root / "_site", "/", moment)
    print(canonical(public_receipt(receipt)).decode())
    print("Both WitnessBench certificates verified and archived locally. No solver, network, or production publication.")


if __name__ == "__main__":
    main()
