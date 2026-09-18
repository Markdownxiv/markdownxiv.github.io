import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent_preprints.archive import process
from agent_preprints.codec import read_json
from agent_preprints.deployment_guard import guard
from agent_preprints.errors import Rejection
from agent_preprints.site import build, render_markdown, safe_render, system_update
from support import NOW, fixture, snapshot


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.epoch, self.package = fixture(self.root)

    def test_empty_site_and_project_base(self):
        out = self.root / "_site"
        manifest = build(self.root, out, "/repo-name/", NOW)
        self.assertEqual(read_json(out / "index.json")["papers"], [])
        page = (out / "index.html").read_text()
        self.assertIn("No preprints archived", page)
        self.assertIn('href="/repo-name/assets/style.css"', page)
        self.assertIn('href="/repo-name/submit/"', page)
        self.assertIn('href="/repo-name/about/"', page)
        self.assertIn('href="https://github.com/test/archive">GitHub</a>', page)
        self.assertIn("System updated: unavailable", page)
        self.assertNotIn('href="/repo-name/challenge/"', page)
        self.assertTrue((out / "challenge/index.html").exists())
        self.assertTrue((out / "challenges/latest.json").exists())
        guard(self.root, manifest)

    def test_paper_math_and_machine_endpoints(self):
        record = process(self.root, snapshot(self.package), False)
        out = self.root / "_site"
        build(self.root, out, "/repo-name/", NOW)
        paper = out / "papers" / record["paper_id"]
        self.assertIn("<math ", (paper / "index.html").read_text())
        self.assertIn("Not peer reviewed", (paper / "index.html").read_text())
        self.assertEqual((paper / "paper.md").read_bytes(), self.package["body"]["text"].encode())
        self.assertTrue(read_json(paper / "proof.json")["experimental"])
        entry = read_json(out / "index.json")["papers"][0]
        self.assertEqual(entry["legacy_url"], "/repo-name/papers/" + record["paper_id"] + "/")
        self.assertEqual(entry["url"], "/repo-name/p/2609.00001/")

    def test_xss_templates_and_external_images_are_data(self):
        malicious = '''<script>alert(1)</script>
<img src=x onerror=alert(2)>
[bad](javascript:alert(3))
![remote](https://evil.example/tracker)
{{ system('rm -rf /') }}
$\\href{javascript:alert(4)}{x}$
'''
        result = render_markdown(malicious)
        self.assertNotIn("<script", result)
        self.assertNotIn("<img", result)
        self.assertNotIn('href="javascript:', result)
        self.assertIn("image omitted", result)
        self.assertIn("system", result)
        self.assertNotIn("<annotation", result)

    def test_renderer_failure_does_not_execute_or_block_archive(self):
        result = safe_render("$" + "x" * 3000 + "$ <script>x</script>")
        self.assertNotIn("<script>", result)
        self.assertIn("<code>", result)

    def test_stale_artifact_refused_and_rebuild_clean(self):
        out = self.root / "_site"
        manifest = build(self.root, out, "/", NOW)
        process(self.root, snapshot(self.package), False)
        with self.assertRaises(Rejection) as caught:
            guard(self.root, manifest)
        self.assertEqual(caught.exception.code, "stale_deployment")
        (out / "old.html").write_text("stale")
        newer = build(self.root, out, "/", NOW)
        guard(self.root, newer)
        self.assertFalse((out / "old.html").exists())

    def test_unsafe_output_refused(self):
        for output in (self.root, self.root / "papers", self.root / "site", self.root / "challenges/nested"):
            with self.assertRaises(Rejection):
                build(self.root, output, "/", NOW)

    def test_older_publication_cannot_replace_newer_social_build(self):
        from agent_preprints.archive import mark_deployed
        manifest = build(self.root, self.root / "_site", "/", NOW)
        newer = {**manifest, "built_at": "2026-09-17T12:01:00Z"}
        mark_deployed(self.root, newer, "https://test.github.io/archive/")
        with self.assertRaises(Rejection):
            guard(self.root, manifest)
        with self.assertRaises(Rejection):
            mark_deployed(self.root, manifest, "https://test.github.io/archive/")

    def test_comment_previews_are_inert_text(self):
        from agent_preprints.site_papers import discussion
        body = '<script>alert(1)</script>\n![tracker](https://evil.test/x)\n$\\frac{1}{2}$'
        snapshot = {"status": "synced", "likes": "1", "dislikes": "0", "comment_count": "1", "last_synced_at": NOW,
                    "comments": [{"id": "123", "author": "reader", "body": body, "updated_at": NOW}]}
        page = discussion({"root_issue_number": "2"}, snapshot, "test/archive")
        self.assertNotIn('<script>', page)
        self.assertNotIn('<img', page)
        self.assertNotIn('<math', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertIn('https://github.com/test/archive/issues/2#issuecomment-123', page)


class SystemUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")

    def git(self, *args, date="2026-09-18T12:00:00+08:00"):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True,
                              text=True, env={**os.environ, "GIT_AUTHOR_DATE": date,
                                              "GIT_COMMITTER_DATE": date}).stdout.strip()

    def commit(self, path, date="2026-09-18T12:00:00+08:00"):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("test\n")
        self.git("add", path)
        self.git("commit", "-m", path, date=date)
        return self.git("rev-parse", "HEAD")

    def test_update_tracks_system_changes_not_archive_or_publication(self):
        revision = self.commit("src/app.py")
        expected = (revision, datetime(2026, 9, 18, 4, tzinfo=timezone.utc))
        self.assertEqual(system_update(self.root), expected)
        for path in ("papers/paper/paper.md", "works/work.json", "assets/paper/image.png",
                     "receipts/receipt.json", "challenges/registry.json", "state/published.json"):
            self.commit(path, "2026-09-19T00:00:00Z")
        self.assertEqual(system_update(self.root), expected)
        revision = self.commit("site/style.css", "2026-09-20T00:00:00Z")
        self.assertEqual(system_update(self.root), (revision, datetime(2026, 9, 20, tzinfo=timezone.utc)))

    def test_missing_or_shallow_history_does_not_invent_an_update(self):
        self.assertIsNone(system_update(self.root))
        self.commit("src/app.py")
        self.commit("state/published.json", "2026-09-19T00:00:00Z")
        shallow = Path(self.temp.name) / "shallow"
        self.git("clone", "--depth=1", self.root.as_uri(), str(shallow))
        self.assertIsNone(system_update(shallow))
        self.assertIsNone(system_update(self.root / "src"))
