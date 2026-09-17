import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints.errors import Rejection
from agent_preprints.pr_client import submit
from test_v3 import v3_fixture
from support import BODY


class ParticipantAPI:
    def __init__(self, owner=False, ambiguous=False):
        self.owner, self.ambiguous = owner, ambiguous
        self.calls, self.created = [], []
        self.fork_exists = owner
        self.login = "test" if owner else "author"

    def repository(self, name):
        if name == "test/archive":
            return {"id": 1, "name": "archive", "full_name": name, "private": False, "default_branch": "main"}
        if not self.fork_exists:
            raise Rejection("github_not_found", "Missing")
        return {"id": 3, "fork": True, "private": False, "parent": {"id": 1}}

    def request(self, method, path, data=None):
        self.calls.append((method, path, data))
        if path == "/user":
            return {"id": 2, "login": self.login}
        if method == "GET" and "/pulls?" in path:
            return self.created
        if path.endswith("/forks"):
            self.fork_exists = True
            return {}
        if "/git/ref/heads/" in path:
            return {"object": {"sha": "a" * 40}}
        if method == "GET" and "/git/commits/" in path:
            return {"tree": {"sha": "c" * 40}}
        if path.endswith("/git/commits"):
            return {"sha": "b" * 40}
        if path.endswith("/pulls"):
            if self.ambiguous:
                raise Rejection("network_error", "Ambiguous response", True)
            result = {"number": 10, "id": 100, "html_url": "https://github.com/test/archive/pull/10", "head": {"sha": "b" * 40}}
            self.created = [result]
            return result
        return {"sha": "c" * 40}


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        _, self.package = v3_fixture(self.root)
        self.checkpoint = self.root / "pr-checkpoint.json"

    def send(self, api):
        with patch("agent_preprints.pr_client.verify"):
            return submit(api, "test/archive", self.package, self.root, BODY, {}, self.checkpoint)

    def test_fork_and_file_upload_then_idempotent_retry(self):
        api = ParticipantAPI()
        result = self.send(api)
        again = self.send(api)
        self.assertEqual(result, again)
        self.assertEqual(sum(method == "POST" and path.endswith("/pulls") for method, path, _ in api.calls), 1)
        self.assertEqual(sum(path.endswith("/forks") for _, path, _ in api.calls), 1)
        tree = next(data for method, path, data in api.calls if path.endswith("/git/trees"))
        self.assertEqual({item["path"].split("/")[-1] for item in tree["tree"]}, {"paper.md", "metadata.json", "submission.json"})
        self.assertTrue(all(item["mode"] == "100644" for item in tree["tree"]))
        self.assertFalse(any(path.endswith("/merges") or "/issues" in path for _, path, _ in api.calls))

    def test_owner_uses_new_branch_without_forking_self(self):
        api = ParticipantAPI(owner=True)
        self.send(api)
        self.assertFalse(any(path.endswith("/forks") for _, path, _ in api.calls))
        refs = [data["ref"] for _, path, data in api.calls if path.endswith("/git/refs")]
        self.assertEqual(len(refs), 1)
        self.assertTrue(refs[0].startswith("refs/heads/preprint/"))

    def test_ambiguous_creation_is_not_posted_twice(self):
        api = ParticipantAPI(ambiguous=True)
        with self.assertRaises(Rejection):
            self.send(api)
        with self.assertRaises(Rejection) as caught:
            self.send(api)
        self.assertEqual(caught.exception.code, "submission_pending")
        self.assertEqual(sum(method == "POST" and path.endswith("/pulls") for method, path, _ in api.calls), 1)

    def test_local_verification_precedes_all_remote_writes(self):
        api = ParticipantAPI()
        with patch("agent_preprints.pr_client.verify", side_effect=Rejection("invalid_pow", "Bad proof")):
            with self.assertRaises(Rejection):
                submit(api, "test/archive", self.package, self.root, BODY, {}, self.checkpoint)
        self.assertFalse(any(method == "POST" for method, _, _ in api.calls))
