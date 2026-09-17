import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints.archive import capture, receipt_path
from agent_preprints.automation import ingest, opened_snapshot, validate_snapshot
from agent_preprints.codec import canonical, read_json
from agent_preprints.errors import Rejection


class AutomationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "archive"
        shutil.copytree(Path(__file__).parent / "fixtures/production", self.root)
        self.package = read_json(self.root / "submission.json")
        self.received = read_json(self.root / "experiment.json")["received_at"]
        self.event = {"action": "opened", "repository": {"id": 1, "full_name": "test/offline-fixture"},
                      "issue": {"id": 55, "number": 4, "created_at": self.received, "title": "[preprint] fixture",
                                "user": {"id": 2}, "body": canonical(self.package).decode()}}
        self.api = type("API", (), {"fetch_paper": lambda *a: (_ for _ in ()).throw(AssertionError("Inline source should not fetch"))})()

    def test_original_event_verified_then_privileged_stage_rechecks(self):
        snapshot = opened_snapshot(self.event, "test/offline-fixture", "1")
        validated = validate_snapshot(self.root, snapshot, self.api)
        self.assertTrue(validated["result"]["valid"])
        records = ingest(self.root, [validated], self.api, "1")
        self.assertEqual(records[0]["status"], "accepted")
        self.assertEqual(records[0]["snapshot"]["received_at"], self.received)
        with patch("agent_preprints.archive.evaluate", side_effect=AssertionError("Already sealed success must not revalidate")):
            repeated = ingest(self.root, [validated], self.api, "1")
        self.assertEqual(repeated, records)

    def test_forged_artifact_acceptance_flag_cannot_skip_mathematics(self):
        package = copy.deepcopy(self.package)
        package["answers"] = []
        event = copy.deepcopy(self.event)
        event["issue"]["body"] = canonical(package).decode()
        snapshot = opened_snapshot(event, "test/offline-fixture", "1")
        records = ingest(self.root, [{"snapshot": snapshot, "body_base64": None, "result": {"valid": True}}], self.api, "1")
        self.assertEqual(records[0]["status"], "rejected")
        self.assertEqual(records[0]["error_code"], "answer_count")
        self.assertFalse((self.root / "papers" / self.package["content_hash"]).exists())

    def test_trusted_event_ids_and_action_are_required(self):
        for field, value in (("action", "edited"), ("repository", {"id": 99, "full_name": "test/offline-fixture"})):
            event = {**self.event, field: value}
            with self.assertRaises(Rejection) as caught:
                opened_snapshot(event, "test/offline-fixture", "1")
            self.assertEqual(caught.exception.code, "event_mismatch")

    def test_shell_syntax_in_paper_is_only_data(self):
        # A rejected uncommitted alteration must not execute shell syntax or code.
        event = copy.deepcopy(self.event)
        marker = self.root / "must-not-exist"
        changed = copy.deepcopy(self.package)
        changed["body"]["text"] += f"\n$(touch {marker})\n`touch {marker}`\n${{{{ secrets.GITHUB_TOKEN }}}}"
        event["issue"]["body"] = canonical(changed).decode()
        snapshot = opened_snapshot(event, "test/offline-fixture", "1")
        records = ingest(self.root, [{"snapshot": snapshot, "body_base64": None, "result": {"valid": True}}], self.api, "1")
        self.assertEqual(records[0]["error_code"], "body_hash_mismatch")
        self.assertFalse(marker.exists())

    def test_full_production_verification_with_mocked_github_file_source(self):
        from test_github import MockAPI, SOURCE
        from agent_preprints.protocol import Context, verify
        package = copy.deepcopy(self.package)
        body = package["body"]["text"].encode()
        package["body"] = dict(SOURCE)
        api = MockAPI(body)
        result = verify(package, self.root, Context("1", "2", self.received), fetch_body=api.fetch_paper)
        self.assertEqual(result["body"], body)
        self.assertEqual(len(api.calls), 5)

    def test_binary_artifact_roundtrip_and_untrusted_digest(self):
        cache = self.root / "cache"
        snapshot = opened_snapshot(self.event, "test/offline-fixture", "1")
        artifact = validate_snapshot(self.root, snapshot, self.api, cache)
        self.assertIn("body_file", artifact)
        self.assertNotIn("body_base64", artifact)
        original = (cache / artifact["body_file"]).read_bytes()
        (cache / artifact["body_file"]).write_bytes(original + b"tampering")
        with self.assertRaises(Rejection) as caught:
            ingest(self.root, [artifact], self.api, "1", cache)
        self.assertEqual(caught.exception.code, "artifact_limit")
        (cache / artifact["body_file"]).write_bytes(original)
        records = ingest(self.root, [artifact], self.api, "1", cache)
        self.assertEqual(records[0]["status"], "accepted")

    def test_artifact_paths_and_symlinks_are_rejected(self):
        cache = self.root / "cache"
        artifact = validate_snapshot(self.root, opened_snapshot(self.event, "test/offline-fixture", "1"), self.api, cache)
        changed = copy.deepcopy(artifact)
        changed["body_file"] = "../submission.json"
        with self.assertRaises(Rejection):
            ingest(self.root, [changed], self.api, "1", cache)
        file = cache / artifact["body_file"]
        raw = file.read_bytes()
        file.unlink()
        target = self.root / "image-data"
        target.write_bytes(raw)
        file.symlink_to(target)
        with self.assertRaises(Rejection):
            ingest(self.root, [artifact], self.api, "1", cache)
