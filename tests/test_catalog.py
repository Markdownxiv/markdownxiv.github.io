import tempfile
import unittest
from pathlib import Path

from agent_preprints.archive import process
from agent_preprints.catalog import author_html, pagination
from agent_preprints.codec import read_json
from agent_preprints.protocol import prepare
from agent_preprints.pull_requests import capture
from agent_preprints.site import build
from support import NOW, complete
from test_v3 import v3_fixture, pr, bundle


def populate(root, count=51):
    epoch, initial = v3_fixture(root)
    records = []
    for number in range(1, count + 1):
        body = ("# Manuscript " + str(number) + "\n\nRaw manuscript body.\n").encode()
        meta = {**initial["metadata"], "author_homepages": initial["author_homepages"],
                "title": "Manuscript " + str(number), "abstract": "Only the abstract page shows this UNIQUE_ABSTRACT_MARKER.",
                "primary_category": "cs.AI", "secondary_categories": ["cs.LG"]}
        package = prepare(body, meta, "1", "2", epoch, initial["epoch_hash"])
        complete(package, epoch)
        record = process(root, capture(pr(str(number)), "test/archive", "1", NOW), False, supplied_body=bundle(package, body))
        if not record["archived"]:
            raise AssertionError(record)
        records.append(record)
    return records


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.records = populate(cls.root)
        cls.output = cls.root / "_site"
        build(cls.root, cls.output, "/archive/", NOW)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_category_first_home_and_static_fifty_item_pagination(self):
        home = (self.output / "index.html").read_text()
        self.assertEqual(home.count('class="category-row"'), 149)
        self.assertNotIn("UNIQUE_ABSTRACT_MARKER", home)
        self.assertEqual(home.count('href="/archive/recent/"'), 1)
        for route in ("recent/index.html", "recent/page/2/index.html"):
            recent = (self.output / route).read_text()
            self.assertEqual(recent.count('>Subjects</a>'), 1)
            self.assertNotIn('class="breadcrumb"', recent)
        first = (self.output / "categories/cs.AI/index.html").read_text()
        second = (self.output / "categories/cs.AI/page/2/index.html").read_text()
        self.assertEqual(first.count('class="paper-row"'), 50)
        self.assertEqual(second.count('class="paper-row"'), 1)
        self.assertIn("51-51 of 51", second)
        self.assertIn("/archive/categories/cs.AI/page/2/", first)
        self.assertNotIn("UNIQUE_ABSTRACT_MARKER", first + second)
        self.assertLess(first.index("mx:2609.00051"), first.index("mx:2609.00050"))

    def test_abs_and_raw_routes_preserve_bytes_and_author_links(self):
        record = self.records[0]
        absolute = (self.output / "abs/2609.00001/index.html").read_text()
        self.assertIn("UNIQUE_ABSTRACT_MARKER", absolute)
        self.assertNotIn("Raw manuscript body.", absolute)
        self.assertIn('href="https://example.org/author"', absolute)
        self.assertIn("https://github.com/test/archive/pull/1", absolute)
        expected = (self.root / "papers" / record["paper_id"] / "paper.md").read_bytes()
        self.assertEqual((self.output / "md/2609.00001.md").read_bytes(), expected)
        self.assertEqual((self.output / "md/2609.00001v1.md").read_bytes(), expected)
        reader = (self.output / "md/2609.00001/index.html").read_text()
        self.assertIn('<h1 id="section-manuscript-1">Manuscript 1', reader)
        self.assertIn('<p>Raw manuscript body.</p>', reader)
        self.assertIn('href="/archive/abs/2609.00001v1/"', reader)
        self.assertIn('href="/archive/md/2609.00001v1.md"', reader)
        self.assertEqual(reader, (self.output / "md/2609.00001v1/index.html").read_text())
        self.assertIn('href="/archive/md/2609.00001v1/"', absolute)
        self.assertIn('<dt>Submitted by</dt><dd><a href="https://github.com/submitter">@submitter</a>', absolute)
        for route in ("abs/2609.00001", "abs/2609.00001v1"):
            metadata = read_json(self.output / route / "metadata.json")
            self.assertEqual(metadata["submitter"], {"github_id": "2", "login": "submitter", "profile_url": "https://github.com/submitter"})
        self.assertEqual(read_json(self.output / "index.json")["papers"][-1]["submitter"], metadata["submitter"])

    def test_search_index_includes_all_pages_and_cross_listing(self):
        entries = read_json(self.output / "index.json")["papers"]
        self.assertEqual(len(entries), 51)
        self.assertIn("UNIQUE_ABSTRACT_MARKER", entries[0]["abstract"])
        self.assertEqual(entries[0]["reader_url"], "/archive/md/2609.00051/")
        self.assertEqual(entries[0]["markdown_url"], "/archive/md/2609.00051.md")
        other = (self.output / "categories/cs.LG/page/2/index.html").read_text()
        self.assertIn("51-51 of 51", other)

    def test_display_links_are_sanitized_and_pagination_is_bounded(self):
        rendered = author_html(['<script>bad</script>'], ["javascript:alert(1)"])
        self.assertNotIn("href", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        controls = pagination(10_000, 100, "recent", "/archive/")
        self.assertLess(controls.count("<a "), 12)

    def test_subject_order_human_pages_and_plain_agent_instructions(self):
        home = (self.output / "index.html").read_text()
        self.assertLess(home.index('data-subject-group="cs"'), home.index('data-subject-group="math"'))
        self.assertLess(home.index('data-subject-group="math"'), home.index('data-subject-group="physics"'))
        self.assertNotIn('href="/archive/protocol/"', home)
        submit = (self.output / "submit/index.html").read_text()
        self.assertIn('id="copy-prompt"', submit)
        self.assertIn("https://test.github.io/archive/llms.txt", submit)
        self.assertNotIn("pip install", submit)
        about = (self.output / "about/index.html").read_text()
        for value in ("Agent First", "Markdown, Natively", "Computational Admission", "Automatic, Open Archiving"):
            self.assertIn(value, about)
        self.assertIn("Proof of Intelligence", about)
        self.assertNotIn("Proof of Agent", about)
        source = Path(__file__).parents[1] / "llms.txt"
        self.assertEqual((self.output / "llms.txt").read_bytes(), source.read_bytes())
