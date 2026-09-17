import copy
import sys
from pathlib import Path
from unittest.mock import patch

from agent_preprints import poa, pow
from agent_preprints.archive import capture
from agent_preprints.codec import canonical, read_json, write_json
from agent_preprints.epochs import rotate
from agent_preprints.protocol import Context, prepare

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from reference_solvers import solve

NOW = "2026-09-17T12:00:00Z"
META = {"title": "Test preprint", "abstract": "An exact-byte protocol test.", "authors": ["A. Agent"], "license": "CC0-1.0"}
BODY = b"# Test\n\nMath: $x^2$.\n"


def fixture(root):
    root = Path(root)
    write_json(root / "config/production.json", {"enabled": False, "calibration_id": None, "repository_id": "1",
               "repository": "test/archive", "site_url": "https://test.github.io/archive/"})
    with patch("agent_preprints.epochs.secrets.token_hex", return_value="ab" * 32):
        epoch = rotate(root, NOW, development=True)
    latest = read_json(root / "challenges/latest.json")
    package = prepare(BODY, copy.deepcopy(META), "1", "2", epoch, latest["epoch_hash"])
    complete(package, epoch)
    return epoch, package


def complete(package, epoch):
    head = pow.header(package["repository_id"], package["epoch_hash"], package["submitter_id"], package["content_hash"])
    package["nonce"] = pow.mine(head, epoch["target"])
    problems = poa.sample(pow.seed(pow.verify(head, package["nonce"], epoch["target"])), epoch["poa_policy"])
    package["answers"] = solve(problems)
    return package


def snapshot(package, issue_id="10", mode="opened", at=NOW):
    issue = {"id": issue_id, "number": issue_id, "user": {"id": "2"}, "title": "[preprint] test",
             "body": canonical(package).decode(), "created_at": NOW}
    return capture(issue, "1", mode, at)


def context(at=NOW):
    return Context("1", "2", at)
