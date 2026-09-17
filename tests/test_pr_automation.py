import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints.archive import mark_deployed, process, public_receipt, receipt_path
from agent_preprints.automation import sync_receipts
from agent_preprints.codec import read_json, write_json
from agent_preprints.errors import Rejection
from agent_preprints.pr_automation import collect, main
from agent_preprints.pull_requests import capture
from agent_preprints.site import build
from test_archive import CommentAPI
from test_v3 import PRFiles, bundle, pr, v3_fixture
from support import NOW


class PRAutomationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        _, self.package = v3_fixture(self.root)
        self.snapshot = capture(pr(), "test/archive", "1", NOW)

    def test_recovery_reads_prs_and_is_bounded(self):
        class API:
            def request(self, method, path):
                assert "/pulls?" in path
                return [pr(str(i)) for i in range(1, 8)]
        selected, page = collect(self.root, API(), "test/archive", "1", "main", NOW)
        self.assertEqual(len(selected), 5)
        self.assertEqual(page, "1")
        self.assertTrue(all(s["mode"] == "pull_request" and s["received_at"] == NOW for s in selected))

    def test_drafts_other_base_and_missing_forks_do_not_block_scan(self):
        drafts = [pr("1"), pr("2"), pr("3"), pr("4")]
        drafts[0]["draft"] = True
        drafts[1]["base"]["ref"] = "other"
        drafts[2]["head"]["repo"] = None
        class API:
            def request(self, method, path):
                return drafts
        selected, _ = collect(self.root, API(), "test/archive", "1", "main", NOW)
        self.assertEqual([s["issue_number"] for s in selected], ["4"])

    def test_forged_validation_result_does_not_authorize_admission(self):
        event = self.root / "event.json"
        artifact = self.root / "artifact.json"
        write_json(event, {"action": "opened", "repository": {"id": "1", "full_name": "test/archive"}, "pull_request": pr()})
        write_json(artifact, {"validated": [{"snapshot": self.snapshot, "result": {"valid": True, "archived": True}}]})
        environment = {"GITHUB_EVENT_NAME": "pull_request_target", "GITHUB_EVENT_PATH": str(event)}
        with patch.dict(os.environ, environment), patch("sys.argv", ["automation", "ingest-event", "--root", str(self.root), "--artifact", str(artifact)]), \
             patch("agent_preprints.pr_automation._workflow_context", return_value=(PRFiles(self.package), "test/archive", "1", "main")), \
             patch("agent_preprints.pr_automation.GitTransaction") as transaction, \
             patch("agent_preprints.pull_requests.verify_pow", side_effect=Rejection("invalid_pow", "Invalid work")), \
             contextlib.redirect_stdout(io.StringIO()):
            transaction.return_value.run.side_effect = lambda callback: ("c" * 40, callback(self.root))
            self.assertEqual(main(), 0)
        record = read_json(receipt_path(self.root, self.snapshot))
        self.assertFalse(record["archived"])
        self.assertEqual(record["error_code"], "invalid_pow")

    def test_issue_event_is_not_an_admission_entry(self):
        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "issues"}), patch("sys.argv", ["automation", "validate-event"]), \
             patch("agent_preprints.pr_automation._workflow_context", return_value=(PRFiles(self.package), "test/archive", "1", "main")), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(), 2)

    def test_publication_closes_pr_and_retries_close_without_duplicate_comment(self):
        process(self.root, self.snapshot, False, supplied_body=bundle(self.package))
        manifest = build(self.root, self.root / "_site", "/archive/", NOW)
        mark_deployed(self.root, manifest, "https://test.github.io/archive/")
        class API(CommentAPI):
            def __init__(self):
                super().__init__()
                self.close_attempts = 0
            def request(self, method, path, data=None):
                if method == "PATCH" and "/pulls/" in path:
                    self.close_attempts += 1
                    if self.close_attempts == 1:
                        raise Rejection("network_error", "Close unavailable", True)
                    return {"state": "closed"}
                return super().request(method, path, data)
        api = API()
        sync_receipts(self.root, api, "test/archive")
        sync_receipts(self.root, api, "test/archive")
        sync_receipts(self.root, api, "test/archive")
        self.assertEqual(len(api.data), 1)
        self.assertEqual(api.close_attempts, 2)
        record = read_json(receipt_path(self.root, self.snapshot))
        self.assertTrue(record["pr_closed"])
        self.assertEqual(public_receipt(record)["url"], "https://test.github.io/archive/abs/2609.00001v1/")
