import concurrent.futures
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints.archive import process
from agent_preprints.automation import GitTransaction
from agent_preprints.codec import read_json, write_json, content_hash, sha
from agent_preprints.errors import Rejection
from support import fixture, snapshot, complete


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


class GitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.seed = self.root / "seed"
        self.seed.mkdir()
        git(self.root, "init", "--bare", str(self.remote))
        git(self.seed, "init", "-b", "main")
        git(self.seed, "config", "user.name", "Test")
        git(self.seed, "config", "user.email", "test@example.invalid")
        self.epoch, self.package = fixture(self.seed)
        for folder in ("papers", "receipts", "state"):
            (self.seed / folder).mkdir(exist_ok=True)
            (self.seed / folder / ".gitkeep").touch()
        (self.seed / ".gitignore").write_text(".archive.lock\n")
        (self.seed / ".gitattributes").write_bytes((Path(__file__).resolve().parents[1] / ".gitattributes").read_bytes())
        git(self.seed, "add", ".")
        git(self.seed, "commit", "-m", "fixture")
        git(self.seed, "remote", "add", "origin", str(self.remote))
        git(self.seed, "push", "-u", "origin", "main")
        git(self.remote, "symbolic-ref", "HEAD", "refs/heads/main")

    def clone(self, name):
        destination = self.root / name
        git(self.root, "clone", str(self.remote), str(destination))
        return destination

    def test_atomic_paper_and_receipt_commit(self):
        checkout = self.clone("writer")
        tx = GitTransaction(checkout, "main")
        commit, record = tx.run(lambda tree: process(tree, snapshot(self.package), False))
        paths = git(self.remote, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        self.assertIn("papers/" + record["paper_id"] + "/paper.md", paths)
        self.assertIn("receipts/1-10.json", paths)
        same, _ = tx.run(lambda tree: process(tree, snapshot(self.package), False))
        self.assertEqual(same, commit)

    def test_v3_pr_paper_work_and_receipt_commit_together(self):
        from test_v3 import v3_fixture, pr, bundle
        from agent_preprints.pull_requests import capture
        from support import NOW
        _, package = v3_fixture(self.seed)
        git(self.seed, "add", ".")
        git(self.seed, "commit", "-m", "v3 fixture")
        git(self.seed, "push", "origin", "main")
        checkout = self.clone("pr-writer")
        tx = GitTransaction(checkout, "main")
        request = capture(pr(), "test/archive", "1", NOW)
        commit, record = tx.run(lambda tree: process(tree, request, False, supplied_body=bundle(package)))
        names = git(self.remote, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        self.assertIn("receipts/1-pr-1.json", names)
        self.assertIn("works/2609.00001.json", names)
        self.assertIn("papers/" + record["paper_id"] + "/paper.md", names)
        again, _ = tx.run(lambda tree: process(tree, request, False, supplied_body=bundle(package)))
        self.assertEqual(commit, again)

    def test_crlf_paper_is_committed_verbatim_even_with_autocrlf(self):
        checkout = self.clone("crlf-writer")
        git(checkout, "config", "core.autocrlf", "true")
        paper = self.package["body"]["text"].replace("\n", "\r\n").encode()
        self.package["body"]["text"] = paper.decode()
        self.package["paper_sha256"] = sha(paper)
        self.package["content_hash"] = content_hash(self.package["metadata"], sha(paper))
        complete(self.package, self.epoch)
        commit, record = GitTransaction(checkout, "main").run(lambda tree: process(tree, snapshot(self.package), False))
        raw = subprocess.run(["git", "-C", str(self.remote), "show", commit + ":papers/" + record["paper_id"] + "/paper.md"],
                             capture_output=True, check=True).stdout
        self.assertEqual(raw, paper)
        epoch_file = "challenges/epochs/" + self.epoch["epoch_id"] + ".json"
        stored_epoch = subprocess.run(["git", "-C", str(self.remote), "show", commit + ":" + epoch_file],
                                      capture_output=True, check=True).stdout
        self.assertEqual(stored_epoch, (self.seed / epoch_file).read_bytes())

    def test_non_fast_forward_reloads_state_and_revalidates(self):
        checkout = self.clone("writer")
        calls = []
        def mutate(tree):
            calls.append(read_json(tree / "state/scan.json")["page"] if (tree / "state/scan.json").exists() else None)
            return process(tree, snapshot(self.package), False)
        def concurrent_change(attempt):
            if attempt == 0:
                write_json(self.seed / "state/scan.json", {"page": "99"})
                git(self.seed, "add", "state/scan.json")
                git(self.seed, "commit", "-m", "concurrent maintainer change")
                git(self.seed, "push", "origin", "main")
        commit, record = GitTransaction(checkout, "main").run(mutate, concurrent_change)
        self.assertEqual(calls, [None, "99"])
        self.assertEqual(git(self.remote, "show", "main:state/scan.json"), '{"page":"99"}')
        self.assertEqual(len(git(self.remote, "ls-tree", "-r", "--name-only", "main", "papers").splitlines()), 4)

    def test_two_writers_do_not_duplicate(self):
        clones = [self.clone("one"), self.clone("two")]
        def work(index):
            return GitTransaction(clones[index], "main").run(lambda tree: process(tree, snapshot(self.package, str(10 + index)), False))
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(work, range(2)))
        self.assertEqual(sorted(r[1]["status"] for r in results), ["accepted", "duplicate"])
        paths = git(self.remote, "ls-tree", "-r", "--name-only", "main").splitlines()
        self.assertEqual(sum(p.endswith("/paper.md") for p in paths), 1)
        self.assertIn("receipts/1-10.json", paths)
        self.assertIn("receipts/1-11.json", paths)

    def test_push_failure_does_not_claim_remote_archive(self):
        checkout = self.clone("writer")
        tx = GitTransaction(checkout, "main", attempts=2)
        original = tx.git
        def reject_push(root, *args, **kwargs):
            if args[0] == "push":
                return subprocess.CompletedProcess([], 1, "", "simulated rejected push")
            return original(root, *args, **kwargs)
        with patch.object(tx, "git", side_effect=reject_push):
            with self.assertRaises(Rejection) as caught:
                tx.run(lambda tree: process(tree, snapshot(self.package), False))
        self.assertEqual(caught.exception.code, "git_push_failed")
        self.assertNotIn("receipts/1-10.json", git(self.remote, "ls-tree", "-r", "--name-only", "main"))

    def test_forbidden_archive_paths_are_never_pushed(self):
        checkout = self.clone("writer")
        def mutation(tree):
            (tree / "papers" / "execute.sh").write_text("exit 0")
        with self.assertRaises(Rejection) as caught:
            GitTransaction(checkout, "main").run(mutation)
        self.assertEqual(caught.exception.code, "unsafe_write")

    def test_v5_epoch_can_be_published_but_development_epochs_cannot(self):
        from agent_preprints import PROTOCOL_V5, poi, taxonomy
        from agent_preprints.epochs import initialize, rotate
        from support import NOW
        source = Path(__file__).resolve().parents[1] / "challenges/calibrations/f869e8bedc49e3a70c99ed1c9ca8374b7c269ee47f70c4536fb6a4143ed9e2a7.json"
        initialize(self.seed, read_json(source), "test/archive", "1", "https://test.github.io/archive/", PROTOCOL_V5)
        taxonomy.ensure(self.seed)
        git(self.seed, "add", ".")
        git(self.seed, "commit", "-m", "Configure v5 fixture")
        git(self.seed, "push", "origin", "main")
        checkout = self.clone("v5-epoch-writer")
        tx = GitTransaction(checkout, "main")
        commit, epoch = tx.run(lambda tree: rotate(tree, NOW))
        self.assertEqual(epoch["poa_policy"], poi.PRODUCTION_POLICY)
        names = git(self.remote, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        self.assertIn("challenges/epochs/v5-2026-09-17.json", names)
        with self.assertRaises(Rejection) as caught:
            tx.run(lambda tree: rotate(tree, NOW, development=True, protocol=PROTOCOL_V5))
        self.assertEqual(caught.exception.code, "unsafe_write")
        self.assertEqual(git(self.remote, "rev-parse", "main"), commit)

    def v2_package(self, body=b"# A new v2 manuscript\n", intent=None):
        from agent_preprints import PROTOCOL_V2, taxonomy
        from agent_preprints.epochs import rotate, epoch_path
        from agent_preprints.protocol import prepare
        from support import NOW, META
        epoch = rotate(self.seed, NOW, True, protocol=PROTOCOL_V2)
        meta = {**META, "primary_category": "math.CO", "ai_disclosure": "unknown", "agents": []}
        package = prepare(body, meta, "1", "2", epoch, sha(epoch_path(self.seed, epoch["epoch_id"]).read_bytes()),
                          submission_intent=intent, catalog=taxonomy.load(self.seed, epoch["taxonomy_hash"]))
        return complete(package, epoch)

    def test_v2_two_git_writers_allocate_distinct_short_ids(self):
        one = self.v2_package()
        two = self.v2_package(b"# Another v2 manuscript\n")
        git(self.seed, "add", ".")
        git(self.seed, "commit", "-m", "trusted v2 development epoch")
        git(self.seed, "push", "origin", "main")
        clones = [self.clone("v2-one"), self.clone("v2-two")]
        packages = [one, two]
        def write(index):
            return GitTransaction(clones[index], "main").run(lambda tree: process(tree, snapshot(packages[index], str(70 + index)), False))
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(write, range(2)))
        self.assertEqual({r[1]["work_id"] for r in result}, {"mx:2609.00001", "mx:2609.00002"})
        names = git(self.remote, "ls-tree", "-r", "--name-only", "main").splitlines()
        self.assertEqual(sum(p.endswith("/paper.md") for p in names), 2)

    def test_v2_git_retry_rechecks_parent_after_competing_revision(self):
        original = self.v2_package()
        first = process(self.seed, snapshot(original, "70"), False)
        intent = {"kind": "revision", "work_id": first["work_id"], "parent_hash": first["paper_id"], "change_summary": "Change text."}
        one = self.v2_package(b"# Winning revision\n", intent)
        two = self.v2_package(b"# Stale revision\n", intent)
        git(self.seed, "add", ".")
        git(self.seed, "commit", "-m", "v2 work and revision challenge")
        git(self.seed, "push", "origin", "main")
        winner, stale = self.clone("winner"), self.clone("stale")
        def race(attempt):
            if attempt == 0:
                GitTransaction(winner, "main").run(lambda tree: process(tree, snapshot(one, "71"), False))
        _, result = GitTransaction(stale, "main").run(lambda tree: process(tree, snapshot(two, "72"), False), race)
        self.assertEqual(result["error_code"], "revision_conflict")
        latest = self.clone("result")
        from agent_preprints.works import all_works
        versions = all_works(latest)[0]["versions"]
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[-1]["content_hash"], one["content_hash"])
        self.assertFalse((latest / "papers" / two["content_hash"]).exists())
