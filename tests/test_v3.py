import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints import PROTOCOL_V3, taxonomy
from agent_preprints.archive import process, public_receipt
from agent_preprints.codec import canonical, read_json, sha, write_json
from agent_preprints.epochs import rotate
from agent_preprints.errors import Rejection
from agent_preprints.protocol import prepare, verify, verify_pow
from agent_preprints.protocol_v3 import content_hash, material_size, metadata_file, validate_package
from agent_preprints.pull_requests import capture, evaluate, event_snapshot
from support import NOW, BODY, complete, context, fixture


def v3_fixture(root, body=BODY):
    fixture(root)
    config = read_json(Path(root) / "config/production.json")
    config["protocol"] = PROTOCOL_V3
    write_json(Path(root) / "config/production.json", config)
    epoch = rotate(root, NOW, development=True, protocol=PROTOCOL_V3)
    meta = read_json(Path(__file__).parents[1] / "examples/metadata-v2.json")
    meta["author_homepages"] = ["https://example.org/author"] * len(meta["authors"])
    package = prepare(body, meta, "1", "2", epoch, read_json(Path(root) / "challenges/latest.json")["epoch_hash"],
                      catalog=taxonomy.load(root, epoch["taxonomy_hash"]))
    complete(package, epoch)
    return epoch, package


def pr(number="1", head="b" * 40):
    return {"id": number, "number": number, "user": {"id": "2"}, "title": "[preprint] test", "state": "open", "draft": False,
            "created_at": "2000-01-01T00:00:00Z", "base": {"sha": "a" * 40, "ref": "main", "repo": {"id": "1", "full_name": "test/archive"}},
            "head": {"sha": head, "repo": {"id": "3", "full_name": "author/archive", "private": False}}}


def bundle(package, paper=BODY):
    return {"package": package, "paper": paper, "metadata": canonical(metadata_file(package)) + b"\n", "assets": {}}


class PRFiles:
    def __init__(self, package):
        self.package = package
        self.directory = "submissions/" + "c" * 32 + "/"
        self.files = {"paper.md": BODY, "metadata.json": canonical(metadata_file(package)) + b"\n", "submission.json": canonical(package) + b"\n"}
        self.names = list(self.files)
        self.reads = []

    def repository_by_id(self, repository_id):
        assert repository_id == "3"
        return {"id": 3, "private": False, "full_name": "author/archive"}

    def request(self, method, path, **kwargs):
        assert path.endswith("a" * 40 + "..." + "b" * 40)
        return {"base_commit": {"sha": "a" * 40}, "files": [{"filename": self.directory + name, "status": "added"} for name in self.names]}

    def fetch_file(self, source, cap, **kwargs):
        self.reads.append(source["path"])
        assert source["commit"] == "b" * 40
        return self.files[source["path"][len(self.directory):]]


class V3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.epoch, self.package = v3_fixture(self.root)
        self.snapshot = capture(pr(), "test/archive", "1", NOW)

    def test_homepage_change_does_not_change_pow_but_names_do(self):
        package = copy.deepcopy(self.package)
        package["author_homepages"] = ["https://example.net/new"] * len(package["metadata"]["authors"])
        self.assertEqual(verify_pow(package, self.root, context(), False), verify_pow(self.package, self.root, context(), False))
        verify(package, self.root, context(), False, supplied_body=BODY, supplied_assets={})
        package["metadata"]["authors"][0] = "Another author"
        with self.assertRaises(Rejection) as caught:
            validate_package(package)
        self.assertEqual(caught.exception.code, "content_hash_mismatch")

    def test_homepage_schemes_credentials_and_control_characters(self):
        for bad in ("javascript:alert(1)", "http://example.org", "https://user:password@example.org", "https://example.org\n", "https://[bad"):
            with self.subTest(bad=bad):
                package = copy.deepcopy(self.package)
                package["author_homepages"][0] = bad
                with self.assertRaises(Rejection):
                    validate_package(package)

    def test_exact_material_limit_and_plus_one(self):
        package = copy.deepcopy(self.package)
        package["paper_size"] = str(1_000_000 - len(canonical(metadata_file(package)) + b"\n"))
        self.assertEqual(material_size(package), 1_000_000)
        validate_package(package)
        package["paper_size"] = str(int(package["paper_size"]) + 1)
        with self.assertRaises(Rejection) as caught:
            validate_package(package)
        self.assertEqual(caught.exception.code, "material_limit")

    def test_full_material_boundary_checks_real_bytes(self):
        meta = metadata_file(self.package)
        size = 1_000_000 - len(canonical(meta) + b"\n")
        body = b"# " + b"x" * (size - 3) + b"\n"
        package = prepare(body, meta, "1", "2", self.epoch, self.package["epoch_hash"])
        complete(package, self.epoch)
        result = verify(package, self.root, context(), False, supplied_body=body, supplied_assets={})
        self.assertEqual(result["body"], body)
        with self.assertRaises(Rejection) as caught:
            prepare(body + b"x", meta, "1", "2", self.epoch, self.package["epoch_hash"])
        self.assertEqual(caught.exception.code, "material_limit")

    def test_draft_and_wrong_repository_rejected(self):
        value = pr()
        value["draft"] = True
        with self.assertRaises(Rejection):
            capture(value, "test/archive", "1", NOW)
        with self.assertRaises(Rejection):
            capture(pr(), "test/other", "1", NOW)

    def test_ready_event_uses_observation_time(self):
        event = {"action": "ready_for_review", "repository": {"full_name": "test/archive", "id": 1}, "pull_request": pr()}
        self.assertEqual(event_snapshot(event, "test/archive", "1", NOW)["received_at"], NOW)
        event["action"] = "synchronize"
        with self.assertRaises(Rejection):
            event_snapshot(event, "test/archive", "1", NOW)

    def test_sealed_pr_replay_and_changed_head(self):
        first = process(self.root, self.snapshot, False, supplied_body=bundle(self.package))
        self.assertEqual(first["status"], "accepted")
        changed = capture(pr(head="d" * 40), "test/archive", "1", NOW)
        second = process(self.root, changed, False, supplied_body=bundle(self.package, b"changed"))
        self.assertEqual(first, second)
        receipt = public_receipt(first)
        self.assertEqual(receipt["head_sha"], "b" * 40)
        self.assertEqual(receipt["receipt_version"], "markdownxiv-receipt-v3")
        self.assertIn("/pull/1", receipt["discussion_url"])
        self.assertEqual(len(list((self.root / "works").glob("*.json"))), 1)

    def test_remote_pr_reads_pinned_files_and_metadata(self):
        api = PRFiles(self.package)
        result = evaluate(self.snapshot, self.root, False, api)
        self.assertEqual(result["body"], BODY)
        self.assertEqual(len(api.reads), 3)
        api.files["metadata.json"] = b"{}"
        with self.assertRaises(Rejection) as caught:
            evaluate(self.snapshot, self.root, False, api)
        self.assertEqual(caught.exception.code, "metadata_mismatch")

    def test_pow_checked_before_manuscript_read(self):
        api = PRFiles(self.package)
        package = copy.deepcopy(self.package)
        package["nonce"] = "ffffffffffffffff"
        api.files["submission.json"] = canonical(package)
        with patch("agent_preprints.protocol.pow.verify", side_effect=Rejection("invalid_pow", "Invalid")):
            with self.assertRaises(Rejection):
                evaluate(self.snapshot, self.root, False, api)
        self.assertEqual(api.reads, [api.directory + "submission.json"])

    def test_extra_executable_or_unlisted_file_is_rejected(self):
        for name in ("run.py", "../escape.md", "figures/unused.png"):
            api = PRFiles(self.package)
            api.names.append(name)
            with self.assertRaises(Rejection):
                evaluate(self.snapshot, self.root, False, api)

    def test_v3_cannot_accept_development_in_production(self):
        with self.assertRaises(Rejection):
            verify(self.package, self.root, context(), True, supplied_body=BODY, supplied_assets={})

    def test_local_bundle_is_never_production_evidence(self):
        with self.assertRaises(Rejection) as caught:
            evaluate(self.snapshot, self.root, True, bundle=bundle(self.package))
        self.assertEqual(caught.exception.code, "trusted_context_required")
