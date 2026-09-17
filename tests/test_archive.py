import copy
import concurrent.futures
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints.archive import capture, evaluate, mark_deployed, process, public_receipt, receipt_path
from agent_preprints.automation import parse_comment, upsert_comment
from legacy_automation import collect, sync_receipts
from agent_preprints.codec import canonical, content_hash, read_json, write_json
from agent_preprints.errors import Rejection
from agent_preprints.site import build
from support import NOW, complete, fixture, snapshot


class CommentAPI:
    def __init__(self):
        self.data = []
        self.fail = False
        self.calls = []

    def comments(self, repository, number, page=1):
        return self.data if page == 1 else []

    def request(self, method, path, data=None):
        self.calls.append((method, path))
        if self.fail:
            raise Rejection("network_error", "temporary", True)
        if method == "GET":
            return next(x for x in self.data if str(x["id"]) == path.rsplit("/", 1)[1])
        if method == "PATCH":
            item = next(x for x in self.data if str(x["id"]) == path.rsplit("/", 1)[1])
            item["body"] = data["body"]
            return item
        item = {"id": len(self.data) + 1, "body": data["body"], "user": {"login": "github-actions[bot]", "type": "Bot"}}
        self.data.append(item)
        return item


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.epoch, self.package = fixture(self.root)

    def accept(self, package=None, issue_id="10"):
        return process(self.root, snapshot(package or self.package, issue_id), production=False)

    def test_archive_and_repeat_are_one_record(self):
        result = self.accept()
        self.assertEqual(result["status"], "accepted")
        self.assertFalse(result["published"])
        second = self.accept()
        self.assertEqual(second, result)
        self.assertEqual(len(list((self.root / "papers").glob("*/paper.md"))), 1)
        self.assertEqual(public_receipt(result)["publication_status"], "pending")

    def test_duplicate_body_even_with_new_title(self):
        first = self.accept()
        changed = copy.deepcopy(self.package)
        changed["metadata"]["title"] = "Renamed exactly the same body"
        changed["content_hash"] = content_hash(changed["metadata"], changed["paper_sha256"])
        complete(changed, self.epoch)
        result = self.accept(changed, "11")
        self.assertEqual(result["status"], "duplicate")
        self.assertEqual(result["paper_id"], first["paper_id"])
        self.assertNotEqual(result["content_hash"], first["content_hash"])
        self.assertEqual(len(list((self.root / "papers").glob("*/paper.md"))), 1)

    def test_concurrent_writes_do_not_overwrite(self):
        def submit(i):
            return self.accept(issue_id=str(10 + i))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as workers:
            results = list(workers.map(submit, range(8)))
        self.assertEqual(sum(r["status"] == "accepted" for r in results), 1)
        self.assertEqual(len(list((self.root / "papers").glob("*/proof.json"))), 1)
        self.assertEqual(len(list((self.root / "receipts").glob("*.json"))), 8)

    def test_edit_cannot_fill_missing_answers_or_replace_rejection(self):
        changed = copy.deepcopy(self.package)
        changed["answers"] = []
        first = self.accept(changed)
        self.assertEqual(first["error_code"], "answer_count")
        second = self.accept(self.package)
        self.assertEqual(first, second)
        self.assertEqual(len(list((self.root / "papers").glob("*/paper.md"))), 0)

    def test_transient_failure_preserves_original_snapshot(self):
        opened = snapshot(self.package)
        with patch("agent_preprints.archive.evaluate", side_effect=Rejection("network_error", "retry", True)):
            first = process(self.root, opened, False)
        self.assertEqual(first["status"], "retryable")
        changed = copy.deepcopy(self.package)
        changed["answers"] = []
        edited = snapshot(changed)
        accepted = process(self.root, edited, False)
        self.assertEqual(accepted["snapshot"], opened)
        self.assertTrue(accepted["archived"])

    def test_missing_original_snapshot_uses_observed_time(self):
        observed = snapshot(self.package, mode="observed", at="2026-09-20T00:00:00Z")
        result = process(self.root, observed, False)
        self.assertEqual(result["error_code"], "original_snapshot_unavailable")
        self.assertFalse(result["archived"])

    def test_deploy_failure_and_retry(self):
        record = self.accept()
        manifest = build(self.root, self.root / "_site", "/archive/", now=NOW)
        # Failed deployment performs no mark_deployed operation.
        self.assertFalse(read_json(receipt_path(self.root, record["snapshot"]))["published"])
        mark_deployed(self.root, manifest, "https://test.github.io/archive/")
        after = read_json(receipt_path(self.root, record["snapshot"]))
        self.assertTrue(after["published"])
        self.assertEqual(public_receipt(after)["publication_status"], "published")
        self.assertIn("/archive/papers/", after["url"])
        mark_deployed(self.root, manifest, "https://test.github.io/archive/")
        self.assertEqual(len(list((self.root / "papers").glob("*/paper.md"))), 1)

    def test_comment_failure_and_ambiguous_success(self):
        record = self.accept()
        api = CommentAPI()
        api.fail = True
        sync_receipts(self.root, api, "test/archive")
        self.assertIsNone(read_json(receipt_path(self.root, record["snapshot"]))["comment_id"])
        api.fail = False
        # Simulate successful POST followed by a process crash before the comment ID is committed.
        upsert_comment(api, "test/archive", record)
        sync_receipts(self.root, api, "test/archive")
        self.assertEqual(len(api.data), 1)
        self.assertIsNotNone(read_json(receipt_path(self.root, record["snapshot"]))["comment_id"])
        sync_receipts(self.root, api, "test/archive")
        self.assertEqual(len(api.data), 1)
        self.assertEqual(len(list((self.root / "papers").glob("*/paper.md"))), 1)

    def test_fake_receipt_ignored(self):
        api = CommentAPI()
        upsert_comment(api, "test/archive", self.accept())
        self.assertIsNotNone(parse_comment(api.data[0]))
        api.data[0]["user"] = {"login": "attacker", "type": "User"}
        self.assertIsNone(parse_comment(api.data[0]))

    def test_bounded_scan_and_edit_time(self):
        issues = [{"id": i, "number": i, "title": "[preprint] x", "user": {"id": 2},
                   "body": canonical(self.package).decode(), "created_at": NOW} for i in range(1, 101)]
        class API:
            calls = []
            def issues_page(self, repo, page):
                self.calls.append(page)
                return issues if page == 1 else []
        api = API()
        plan = collect(self.root, api, "test/archive", "1", "2026-09-18T13:00:00Z", batch=3)
        self.assertEqual(len(plan["snapshots"]), 3)
        self.assertEqual(api.calls, [1])
        self.assertEqual(plan["next_page"], "1")
        self.assertEqual(plan["snapshots"][0]["received_at"], "2026-09-18T13:00:00Z")
        self.assertEqual(plan["snapshots"][0]["mode"], "observed")
        for snap in plan["snapshots"]:
            process(self.root, snap, False)
        next_plan = collect(self.root, api, "test/archive", "1", "2026-09-18T13:00:00Z", batch=3)
        self.assertEqual(next_plan["snapshots"][0]["issue_id"], "4")

    def test_retry_backoff_and_cap(self):
        with patch("agent_preprints.archive.evaluate", side_effect=Rejection("network_error", "retry", True)):
            record = self.accept()
        api = type("API", (), {"issues_page": lambda *args: []})()
        current = record["last_attempt_at"]
        self.assertEqual(collect(self.root, api, "test/archive", "1", current)["snapshots"], [])
        record["attempts"] = "8"
        write_json(receipt_path(self.root, record["snapshot"]), record)
        self.assertEqual(collect(self.root, api, "test/archive", "1", "2099-01-01T00:00:00Z")["snapshots"], [])
