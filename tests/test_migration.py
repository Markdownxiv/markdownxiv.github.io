import copy
import tempfile
import unittest
from pathlib import Path

from agent_preprints.archive import mark_deployed, process, public_receipt, receipt_path
from agent_preprints.automation import sync_receipts
from agent_preprints.codec import canonical, read_json, write_json
from agent_preprints.errors import Rejection
from agent_preprints.github import GitHub
from agent_preprints.pull_requests import capture, evaluate
from agent_preprints.site import build
from support import NOW
from test_archive import CommentAPI
from test_v3 import PRFiles, bundle, pr, v3_fixture


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        _, self.package = v3_fixture(self.root)
        self.snapshot = capture(pr(), "test/archive", "1", NOW)

    def test_renamed_source_is_resolved_by_id_without_changing_snapshot(self):
        before = canonical(self.snapshot)
        class RenamedAPI(PRFiles):
            def repository_by_id(self, repository_id):
                self.resolved_id = repository_id
                return {"id": 3, "private": False, "full_name": "organization/new-name"}
            def request(self, method, path, **kwargs):
                assert path.startswith("/repos/organization/new-name/compare/")
                return super().request(method, path, **kwargs)
            def fetch_file(self, source, cap, **kwargs):
                assert source["repository"] == "organization/new-name"
                return super().fetch_file(source, cap, **kwargs)
        api = RenamedAPI(self.package)
        result = evaluate(self.snapshot, self.root, False, api)
        self.assertEqual(result["paper_id"], self.package["content_hash"])
        self.assertEqual(api.resolved_id, "3")
        self.assertEqual(canonical(self.snapshot), before)

    def test_source_id_and_visibility_cannot_change_during_transfer(self):
        for repository in ({"id": 4, "private": False, "full_name": "org/new"},
                           {"id": 3, "private": True, "full_name": "org/new"}):
            api = PRFiles(self.package)
            api.repository_by_id = lambda _: repository
            with self.assertRaises(Rejection) as caught:
                evaluate(self.snapshot, self.root, False, api)
            self.assertEqual(caught.exception.code, "source_mismatch")
            self.assertEqual(api.reads, [])

    def test_repository_lookup_uses_validated_numeric_id(self):
        class API(GitHub):
            def request(self, method, path):
                return {"method": method, "path": path}
        self.assertEqual(API().repository_by_id("123"), {"method": "GET", "path": "/repositories/123"})
        with self.assertRaises(Rejection):
            API().repository_by_id("../other")

    def test_new_deployment_reconciles_links_and_reuses_the_original_comment(self):
        record = process(self.root, self.snapshot, False, supplied_body=bundle(self.package))
        old_manifest = build(self.root, self.root / "_old", "/archive/", NOW)
        mark_deployed(self.root, old_manifest, "https://test.github.io/archive/")
        class API(CommentAPI):
            def request(self, method, path, data=None):
                if method == "PATCH" and "/pulls/" in path:
                    return {"state": "closed"}
                return super().request(method, path, data)
        api = API()
        sync_receipts(self.root, api, "test/archive")
        old_receipt = copy.deepcopy(read_json(receipt_path(self.root, self.snapshot)))
        immutable = {str(p.relative_to(self.root)): p.read_bytes()
                     for folder in ("papers", "works", "assets", "challenges/epochs", "challenges/calibrations")
                     for p in (self.root / folder).rglob("*") if p.is_file()}
        config = read_json(self.root / "config/production.json")
        config.update(repository="organization/organization.github.io", site_url="https://organization.github.io/")
        write_json(self.root / "config/production.json", config)
        manifest = build(self.root, self.root / "_new", now="2026-09-17T12:01:00Z")
        # A build is not publication and must not rewrite successful receipt URLs.
        self.assertEqual(read_json(receipt_path(self.root, self.snapshot)), old_receipt)
        mark_deployed(self.root, manifest, config["site_url"])
        sync_receipts(self.root, api, config["repository"])
        receipt = read_json(receipt_path(self.root, self.snapshot))
        self.assertEqual(receipt["snapshot"], old_receipt["snapshot"])
        self.assertEqual(receipt["comment_id"], old_receipt["comment_id"])
        self.assertEqual(receipt["work_url"], "https://organization.github.io/abs/2609.00001/")
        self.assertEqual(receipt["discussion_url"], "https://github.com/organization/organization.github.io/pull/1")
        self.assertEqual(public_receipt(receipt)["url"], "https://organization.github.io/abs/2609.00001v1/")
        self.assertEqual(len(api.data), 1)
        self.assertIn(receipt["work_url"], api.data[0]["body"])
        for name, raw in immutable.items():
            self.assertEqual((self.root / name).read_bytes(), raw, name)
