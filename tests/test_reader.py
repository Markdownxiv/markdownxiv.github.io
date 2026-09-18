import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from agent_preprints import assets
from agent_preprints.archive import process
from agent_preprints.protocol import prepare
from agent_preprints.protocol_v4 import metadata_file
from agent_preprints.pull_requests import capture
from agent_preprints.site import build
from support import NOW, complete
from test_v3 import pr, bundle
from test_v4 import v4_fixture


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.epoch, self.initial = v4_fixture(self.root)

    def archive(self, body, number="1", intent=None, image=False):
        source = self.root / "source"
        source.mkdir(exist_ok=True)
        if image:
            (source / "figures").mkdir(exist_ok=True)
            Image.new("RGB", (120, 60), "white").save(source / "figures/result.png")
        entries, data = assets.collect_local(body, source)
        package = prepare(body, metadata_file(self.initial), "1", "2", self.epoch, self.initial["epoch_hash"],
                          entries=entries, submission_intent=intent)
        complete(package, self.epoch)
        record = process(self.root, capture(pr(number), "test/archive", "1", NOW), False,
                         supplied_body={**bundle(package, body), "assets": data})
        self.assertTrue(record["archived"], record)
        return record, package

    def test_reader_formats_math_tables_images_and_escapes_html(self):
        body = (b"# A Readable Manuscript\n\n**Strong** and *emphasis*.\n\n$x^2$\n\n"
                b"| Value | Result |\n| --- | --- |\n| One | Two |\n\n"
                b"![Result](figures/result.png)\n\n[Figure file](figures/result.png)\n\n"
                b"<script>alert(1)</script>\n\n[Unsafe](javascript:alert(2))\n")
        _, package = self.archive(body, image=True)
        output = self.root / "_site"
        build(self.root, output, "/archive/", NOW)
        page = (output / "md/2609.00001/index.html").read_text()
        self.assertIn("<strong>Strong</strong>", page)
        self.assertIn("<em>emphasis</em>", page)
        self.assertIn("<table>", page)
        self.assertIn("<math ", page)
        media = "/archive/media/" + assets.filename(package["assets"][0])
        self.assertIn('src="' + media + '"', page)
        self.assertIn('href="' + media + '"', page)
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>", page)
        self.assertNotIn('href="javascript:', page)
        self.assertEqual((output / "md/2609.00001.md").read_bytes(), body)

    def test_latest_reader_changes_while_version_reader_and_raw_stay_fixed(self):
        old = b"# First Version\n\nAn original paragraph.\n"
        record, _ = self.archive(old)
        new = b"# Second Version\n\nA revised paragraph.\n"
        self.archive(new, "2", {"kind": "revision", "work_id": record["work_id"], "parent_hash": record["paper_id"],
                                "change_summary": "Update the text."})
        output = self.root / "_site"
        build(self.root, output, "/", NOW)
        self.assertIn('<h1 id="section-second-version">Second Version', (output / "md/2609.00001/index.html").read_text())
        self.assertIn('<h1 id="section-first-version">First Version', (output / "md/2609.00001v1/index.html").read_text())
        self.assertEqual((output / "md/2609.00001v1.md").read_bytes(), old)
        self.assertEqual((output / "md/2609.00001.md").read_bytes(), new)
        self.assertEqual((output / "md/2609.00001v2.md").read_bytes(), new)

    def test_failed_renderer_leaves_raw_source_and_a_reader_page(self):
        body = b"# A Manuscript\n\nRaw text.\n"
        self.archive(body)
        output = self.root / "_site"
        with patch("agent_preprints.reader.render_reader", return_value={"html": "<pre>Escaped fallback text</pre>", "headings": [], "has_title": False, "css": ""}):
            build(self.root, output, "/", NOW)
        page = (output / "md/2609.00001/index.html").read_text()
        self.assertIn('<pre>Escaped fallback text</pre>', page)
        self.assertEqual((output / "md/2609.00001.md").read_bytes(), body)
