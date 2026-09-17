import base64
import hashlib
import io
import time
import unittest

from agent_preprints.codec import MAX_PAPER
from agent_preprints.errors import Rejection
from agent_preprints.github import GitHub, NoRedirect, bounded_read, validate_source, wall_timeout


SOURCE = {"kind": "github", "repository": "test/source", "commit": "a" * 40, "path": "docs/paper.md"}


class MockAPI(GitHub):
    def __init__(self, body=b"# Paper\n"):
        super().__init__()
        self.body = body
        self.mode = "100644"
        self.private = False
        self.size = len(body)
        self.calls = []

    def request(self, method, path, data=None, **kwargs):
        self.calls.append(path)
        blobhash = hashlib.sha1(b"blob " + str(len(self.body)).encode() + b"\0" + self.body).hexdigest()
        if path == "/repos/test/source":
            return {"private": self.private, "visibility": "private" if self.private else "public"}
        if "/git/commits/" in path:
            return {"sha": "a" * 40, "tree": {"sha": "b" * 40}}
        if path.endswith("/git/trees/" + "b" * 40):
            return {"tree": [{"path": "docs", "type": "tree", "mode": "040000", "sha": "c" * 40}]}
        if path.endswith("/git/trees/" + "c" * 40):
            return {"tree": [{"path": "paper.md", "type": "blob", "mode": self.mode, "sha": blobhash, "size": self.size}]}
        if "/git/blobs/" in path:
            return {"encoding": "base64", "size": len(self.body), "content": base64.b64encode(self.body).decode()}
        raise AssertionError(path)


class SourceTests(unittest.TestCase):
    def test_only_one_immutable_file_read(self):
        api = MockAPI()
        self.assertEqual(api.fetch_paper(SOURCE), b"# Paper\n")
        self.assertEqual(len(api.calls), 5)
        self.assertFalse(any("raw.githubusercontent.com" in c for c in api.calls))

    def test_reject_mutable_ref_traversal_and_arbitrary_url(self):
        for key, value in (("commit", "main"), ("commit", "a" * 39), ("path", "../paper.md"),
                           ("path", "/paper.md"), ("path", "docs//paper.md"), ("path", "x%2f..%2fpaper.md"),
                           ("path", "paper.md;touch /tmp/pwned"), ("repository", "https://evil.example/x")):
            with self.assertRaises(Rejection):
                validate_source({**SOURCE, key: value})

    def test_symlink_submodule_and_oversize_refused_before_blob(self):
        for mode in ("120000", "160000", "040000"):
            api = MockAPI()
            api.mode = mode
            with self.assertRaises(Rejection) as caught:
                api.fetch_paper(SOURCE)
            self.assertEqual(caught.exception.code, "unsafe_source")
            self.assertFalse(any("/git/blobs/" in c for c in api.calls))
        api = MockAPI()
        api.size = MAX_PAPER + 1
        with self.assertRaises(Rejection):
            api.fetch_paper(SOURCE)
        self.assertFalse(any("/git/blobs/" in c for c in api.calls))

    def test_private_source(self):
        api = MockAPI()
        api.private = True
        with self.assertRaises(Rejection) as caught:
            api.fetch_paper(SOURCE)
        self.assertEqual(caught.exception.code, "private_source")

    def test_v2_reads_two_mib_without_weakening_v1(self):
        body = b"A" * (2 * 1024 * 1024)
        api = MockAPI(body)
        self.assertEqual(api.fetch_paper_v2(SOURCE), body)
        with self.assertRaises(Rejection):
            MockAPI(body).fetch_paper(SOURCE)
        api = MockAPI(body + b"x")
        with self.assertRaises(Rejection):
            api.fetch_paper_v2(SOURCE)
        self.assertFalse(any("/git/blobs/" in c for c in api.calls))

    def test_response_size_and_deadline(self):
        response = io.BytesIO(b"abcde")
        response.headers = {}
        with self.assertRaises(Rejection) as caught:
            bounded_read(response, 4, time.monotonic() + 1)
        self.assertEqual(caught.exception.code, "download_limit")
        response = io.BytesIO(b"abc")
        response.headers = {"Content-Length": "999"}
        with self.assertRaises(Rejection):
            bounded_read(response, 4, time.monotonic() + 1)
        response.headers = {}
        with self.assertRaises(Rejection) as caught:
            bounded_read(response, 4, time.monotonic() - 1)
        self.assertEqual(caught.exception.code, "network_timeout")

    def test_redirect_refused(self):
        with self.assertRaises(Rejection) as caught:
            NoRedirect().redirect_request(None, None, 302, "redirect", {}, "http://169.254.169.254/")
        self.assertEqual(caught.exception.code, "redirect_forbidden")

    def test_absolute_wall_timer_interrupts_stalled_read(self):
        class Stalled:
            headers = {}
            def read(self, _):
                time.sleep(1)
                return b""
        start = time.monotonic()
        with self.assertRaises(Rejection) as caught:
            with wall_timeout(0.02):
                bounded_read(Stalled(), 100, time.monotonic() + 1)
        self.assertEqual(caught.exception.code, "network_timeout")
        self.assertLess(time.monotonic() - start, 0.5)

    def test_nested_request_cannot_extend_bundle_deadline(self):
        start = time.monotonic()
        with self.assertRaises(Rejection) as caught:
            with wall_timeout(.02):
                with wall_timeout(2):
                    time.sleep(1)
        self.assertEqual(caught.exception.code, "network_timeout")
        self.assertLess(time.monotonic() - start, .3)
