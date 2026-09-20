import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from agent_preprints.archive import process
from agent_preprints.catalog import author_html, pagination, ranked_entries
from agent_preprints.codec import read_json, timestamp
from agent_preprints.protocol import prepare
from agent_preprints.pull_requests import capture
from agent_preprints.site import build
from agent_preprints.site_papers import reaction_counts, reaction_summary
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
        snapshots = [{"work_id": record["work_id"], "status": "synced", "likes": "0", "dislikes": "0",
                      "comment_count": "1", "last_synced_at": NOW, "comments": []} for record in cls.records[:-1]]
        snapshots[0].update(likes="6", dislikes="1")
        snapshots[1].update(likes="10", dislikes="9")
        snapshots[2].update(dislikes="2")
        build(cls.root, cls.output, "/archive/", NOW, {"generated_at": NOW, "works": snapshots})

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

    def test_discussion_counts_are_shared_by_abstracts_listings_and_index(self):
        absolute = (self.output / "abs/2609.00001/index.html").read_text()
        self.assertIn("1 comment / +6 / -1", absolute)
        self.assertNotIn("comments / +1 6", absolute)
        for route in ("recent", "categories/cs.AI", "categories/cs.LG"):
            second = (self.output / route / "page/2/index.html").read_text()
            self.assertIn('href="https://github.com/test/archive/pull/1"', second)
            self.assertIn("1 comment / +6 / -1", second)
            first = (self.output / route / "index.html").read_text()
            self.assertIn("— comments / +— / -—", first)
        entries = read_json(self.output / "index.json")["papers"]
        self.assertIsNone(entries[0]["social"])
        self.assertEqual(entries[-1]["social"]["score"], "5")
        self.assertNotIn("comments", entries[-1]["social"])
        self.assertEqual(entries[-1]["discussion_url"], "https://github.com/test/archive/pull/1")

    def test_score_sorting_precedes_pagination_and_retains_category_and_window(self):
        for route in ("recent", "categories/cs.AI", "categories/cs.LG"):
            for period in ("week", "month", "year", "all"):
                first = (self.output / route / "top" / period / "index.html").read_text()
                second = (self.output / route / "top" / period / "page/2/index.html").read_text()
                self.assertEqual(first.count('class="paper-row"'), 50)
                self.assertEqual(second.count('class="paper-row"'), 1)
                self.assertLess(first.index("mx:2609.00001"), first.index("mx:2609.00002"))
                self.assertLess(first.index("mx:2609.00002"), first.index("mx:2609.00050"))
                self.assertLess(first.index("mx:2609.00050"), first.index("mx:2609.00049"))
                self.assertIn("mx:2609.00003", first)  # Negative score precedes unknown counts.
                self.assertNotIn("mx:2609.00051", first)
                self.assertIn("mx:2609.00051", second)
                self.assertIn('/archive/' + route + '/top/' + period + '/page/2/', first)
                self.assertIn('href="/archive/' + route + '/top/' + period + '/"', second)
                self.assertIn('href="/archive/' + route + '/">Newest</a>', second)
                self.assertNotIn("UNIQUE_ABSTRACT_MARKER", first + second)

    def test_rolling_windows_use_original_submission_time_and_build_clock(self):
        now = timestamp(NOW)
        def entry(number, age, score):
            return {"work_id": "mx:2609." + str(number).zfill(5),
                    "received_at": (now - timedelta(seconds=age)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "revised_at": NOW, "social": {"score": str(score)}}
        day = 24 * 60 * 60
        entries = [entry(1, 0, 1), entry(2, 7 * day, 2), entry(3, 7 * day + 1, 3),
                   entry(4, 30 * day, 4), entry(5, 30 * day + 1, 5), entry(6, 365 * day, 6),
                   entry(7, 365 * day + 1, 7), entry(8, -1, 8)]
        for period, expected in (("week", [2, 1]), ("month", [4, 3, 2, 1]), ("year", [6, 5, 4, 3, 2, 1]),
                                 ("all", [8, 7, 6, 5, 4, 3, 2, 1])):
            selected = ranked_entries(entries, period, NOW)
            self.assertEqual([int(e["work_id"].split(".")[1]) for e in selected], expected)
        self.assertEqual(ranked_entries([entries[6]], "week", NOW), [])

    def test_unavailable_counts_are_distinct_from_zero_and_unsafe_counts_are_ignored(self):
        self.assertIsNone(reaction_counts(None))
        self.assertIsNone(reaction_counts({"status": "unavailable", "likes": "9"}))
        counts = {"status": "synced", "likes": "0", "dislikes": "0", "comment_count": "0"}
        self.assertEqual(reaction_summary(reaction_counts(counts)), "0 comments / +0 / -0")
        self.assertIsNone(reaction_counts({**counts, "likes": '<script>alert(1)</script>'}))

    def test_subject_order_human_pages_and_plain_agent_instructions(self):
        home = (self.output / "index.html").read_text()
        self.assertLess(home.index('data-subject-group="cs"'), home.index('data-subject-group="math"'))
        self.assertLess(home.index('data-subject-group="math"'), home.index('data-subject-group="physics"'))
        self.assertNotIn('href="/archive/protocol/"', home)
        submit = (self.output / "submit/index.html").read_text()
        self.assertIn('id="copy-prompt"', submit)
        self.assertIn('<pre id="submission-prompt">Read https://test.github.io/archive/llms.txt '
                      'and help me submit my Markdown manuscript to Markdownxiv.</pre>', submit)
        self.assertNotIn("pip install", submit)
        about = (self.output / "about/index.html").read_text()
        for value in ("Agent First", "Markdown, Natively", "Computational Admission", "Automatic, Open Archiving"):
            self.assertIn(value, about)
        self.assertIn("Proof of Intelligence", about)
        self.assertNotIn("Proof of Agent", about)
        source = Path(__file__).parents[1] / "llms.txt"
        self.assertEqual((self.output / "llms.txt").read_bytes(), source.read_bytes())
