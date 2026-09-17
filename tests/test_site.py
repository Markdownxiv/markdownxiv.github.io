import tempfile
import unittest
from pathlib import Path

from agent_preprints.archive import process
from agent_preprints.codec import read_json
from agent_preprints.deployment_guard import guard
from agent_preprints.errors import Rejection
from agent_preprints.site import build, render_markdown, safe_render
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
        self.assertIn('href="/repo-name/challenge/"', page)
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
