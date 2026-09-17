import concurrent.futures
import copy
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from agent_preprints import PROTOCOL_V2, assets, pow, taxonomy, works
from agent_preprints.archive import capture, process, mark_deployed, public_receipt
from agent_preprints.codec import canonical, read_json, sha, write_json
from agent_preprints.epochs import rotate, epoch_path, validate_epoch
from agent_preprints.envelope import format_submission, parse_submission
from agent_preprints.errors import Rejection
from agent_preprints.protocol import prepare, verify, verify_pow
from agent_preprints.protocol_v2 import content_hash, document_hash
from agent_preprints.site import build, render_markdown
from agent_preprints.social import sync
from support import META, BODY, NOW, complete, context, fixture


def png(color="blue", size=(20, 20)):
    stream = io.BytesIO()
    Image.new("RGB", size, color).save(stream, format="PNG")
    return stream.getvalue()


class V2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        fixture(self.root)
        self.epoch = rotate(self.root, NOW, True, protocol=PROTOCOL_V2)
        self.ehash = sha(epoch_path(self.root, self.epoch["epoch_id"]).read_bytes())
        self.catalog = taxonomy.load(self.root, self.epoch["taxonomy_hash"])
        self.meta = {**copy.deepcopy(META), "primary_category": "math.OC", "ai_disclosure": "unknown", "agents": []}
        self.package = self.make()

    def make(self, body=BODY, meta=None, intention=None, entries=None, source=None, asset_source=None, uid="2"):
        package = prepare(body, meta or self.meta, "1", uid, self.epoch, self.ehash, source,
                          entries=entries, asset_source=asset_source, submission_intent=intention, catalog=self.catalog)
        return complete(package, self.epoch)

    def snapshot(self, package, number="10"):
        return capture({"id": number, "number": number, "user": {"id": package["submitter_id"]}, "title": "[preprint] test",
                        "body": format_submission(package), "created_at": NOW}, "1", "opened")

    def accept(self, package=None, number="10", **kwargs):
        return process(self.root, self.snapshot(package or self.package, number), False, **kwargs)

    def revision(self, first, body=BODY, **kwargs):
        return self.make(body, intention={"kind": "revision", "work_id": first["work_id"], "parent_hash": first["paper_id"],
                                         "change_summary": "Update the manuscript."}, **kwargs)

    def test_full_v2_roundtrip_and_english_default(self):
        self.assertEqual(self.package["metadata"]["language"], "en")
        self.assertEqual(parse_submission(format_submission(self.package)), self.package)
        result = verify(self.package, self.root, context(), False)
        self.assertEqual(result["body"], BODY)
        receipt = self.accept()
        self.assertEqual((receipt["work_id"], receipt["version"]), ("mx:2609.00001", "1"))
        self.assertEqual(public_receipt(receipt)["receipt_version"], "agent-preprints-receipt-v2")

    def test_complete_taxonomy_and_aliases(self):
        self.assertEqual(len(self.catalog["groups"]), 8)
        self.assertEqual(len(self.catalog["categories"]), 149)
        self.assertEqual(taxonomy.normalize("cs.NA", self.catalog), "math.NA")
        self.assertEqual(taxonomy.normalize("math.MP", self.catalog), "math-ph")
        meta = {**self.meta, "primary_category": "cs.NA", "secondary_categories": ["math.NA", "cs.NA", "math.OC"]}
        package = self.make(meta=meta)
        self.assertEqual(package["metadata"]["secondary_categories"], ["math.OC"])
        with self.assertRaises(Rejection):
            self.make(meta={**self.meta, "primary_category": "invented.AI"})

    def test_ai_disclosure_required_and_consistent(self):
        for meta in (META, {**self.meta, "ai_disclosure": "declared"}, {**self.meta, "ai_disclosure": "none", "agents": [{"provider": "x", "model": "unknown", "client": "x"}]}):
            with self.assertRaises((Rejection, KeyError)):
                self.make(meta=meta)
        self.make(meta={**self.meta, "ai_disclosure": "declared", "agents": [{"provider": "Example", "model": "unknown", "client": "Local", "model_version": "unknown"}]})

    def test_metadata_assets_and_parent_are_bound(self):
        first = self.accept()
        package = self.revision(first, BODY + b"More.\n")
        for mutate in (lambda p: p["metadata"].update(language="zh"),
                       lambda p: p["metadata"].update(ai_disclosure="none"),
                       lambda p: p["metadata"].update(primary_category="cs.AI"),
                       lambda p: p["intent"].update(parent_hash="0" * 64)):
            changed = copy.deepcopy(package)
            mutate(changed)
            with self.assertRaises(Rejection) as caught:
                verify_pow(changed, self.root, context(), False)
            self.assertEqual(caught.exception.code, "content_hash_mismatch")

    def test_development_and_cross_protocol_epochs_fail_production(self):
        with self.assertRaises(Rejection):
            verify(self.package, self.root, context(), True)
        epoch = copy.deepcopy(self.epoch)
        epoch["resource_policy"]["paper_bytes"] = "9999999999"
        with self.assertRaises(Rejection):
            validate_epoch(epoch, False)
        v1_epoch, v1 = fixture(self.root)
        p = copy.deepcopy(self.package)
        p.update(epoch_id=v1["epoch_id"], epoch_hash=v1["epoch_hash"])
        with self.assertRaises(Rejection) as caught:
            verify_pow(p, self.root, context(), False)
        self.assertEqual(caught.exception.code, "protocol_version")

    def test_envelope_ambiguity_and_forged_preview(self):
        text = format_submission(self.package)
        for changed in (text + text, text.replace("## Test preprint", "## Fraudulent title"), text + "\n", text.replace('"agents":[]', '"agents":[],"agents":[]')):
            with self.assertRaises(Rejection):
                parse_submission(changed)
        self.assertEqual(parse_submission(canonical(self.package).decode()), self.package)

    def test_envelope_escapes_mentions_and_html(self):
        package = self.make(meta={**self.meta, "title": "<script>@everyone [click](https://example.org)</script>"})
        preview = format_submission(package).split("<!-- markdownxiv-payload -->")[0]
        self.assertNotIn("<script>", preview)
        self.assertNotIn("@everyone", preview)
        self.assertNotIn("[click]", preview)

    def test_malformed_json_types_reject_without_crashing(self):
        from agent_preprints.envelope import START, PAYLOAD, END
        with self.assertRaises(Rejection):
            parse_submission(START + "\n" + PAYLOAD + "[]" + END)
        for value in ([], {}, None, True):
            entry = {"path": "a.png", "sha256": "0" * 64, "size": "1", "media_type": value}
            with self.assertRaises(Rejection):
                assets.validate_manifest([entry])
            with self.assertRaises(Rejection):
                taxonomy.normalize(value, self.catalog)

    def test_unchanged_revision_is_rejected(self):
        first = self.accept()
        result = self.accept(self.revision(first), "11")
        self.assertEqual(result["error_code"], "revision_unchanged")
        self.assertEqual(len(works.all_works(self.root)[0]["versions"]), 1)

    def test_revisions_metadata_rollback_and_replay(self):
        first = self.accept()
        changed = self.revision(first, meta={**self.meta, "title": "Corrected title"})
        second = self.accept(changed, "11")
        self.assertEqual(second["version"], "2")
        third = self.accept(self.revision(second), "12")
        self.assertEqual(third["version"], "3")
        replay = self.accept(changed, "13")
        self.assertEqual((replay["status"], replay["version"]), ("duplicate", "2"))
        self.assertEqual((self.root / "papers" / first["paper_id"] / "paper.md").read_bytes(), BODY)

    def test_owner_and_parent_conflicts(self):
        first = self.accept()
        unauthorized = self.revision(first, BODY + b"Intrusion", uid="3")
        self.assertEqual(self.accept(unauthorized, "11")["error_code"], "revision_unauthorized")
        packages = [self.revision(first, BODY + str(i).encode()) for i in range(2)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda i: self.accept(packages[i], str(12 + i)), range(2)))
        self.assertEqual(sorted(r["status"] for r in results), ["accepted", "rejected"])
        self.assertEqual([r["error_code"] for r in results if r["status"] == "rejected"], ["revision_conflict"])

    def test_concurrent_new_ids_and_duplicate_documents(self):
        packages = [self.make(BODY + str(i).encode()) for i in range(3)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(lambda i: self.accept(packages[i], str(10 + i)), range(3)))
        self.assertEqual(len({r["work_id"] for r in results}), 3)
        duplicate = self.make(BODY + b"0", meta={**self.meta, "title": "Renamed duplicate"})
        self.assertEqual(self.accept(duplicate, "20")["status"], "duplicate")
        self.assertEqual(len(works.all_works(self.root)), 3)

    def test_cannot_revise_into_other_work(self):
        first = self.accept()
        self.accept(self.make(BODY + b"Other work"), "11")
        result = self.accept(self.revision(first, BODY + b"Other work"), "12")
        self.assertEqual(result["error_code"], "duplicate_other_work")

    def image_package(self, raw=None, intention=None):
        raw = raw or png()
        entry = {"path": "figures/test.png", "sha256": sha(raw), "size": str(len(raw)), "media_type": "image/png"}
        body = BODY + b"\n![English caption](figures/test.png)\n"
        package = self.make(body, entries=[entry], intention=intention,
                            asset_source={"repository": "test/source", "commit": "a" * 40, "directory": ""})
        return package, {entry["path"]: raw}

    def test_images_roundtrip_changed_image_and_dedup_storage(self):
        package, images = self.image_package()
        first = self.accept(package, supplied_assets=images)
        self.assertEqual(first["status"], "accepted")
        intention = {"kind": "revision", "work_id": first["work_id"], "parent_hash": first["paper_id"], "change_summary": "Update figure color."}
        changed, data = self.image_package(png("red"), intention)
        second = self.accept(changed, "11", supplied_assets=data)
        self.assertEqual(second["version"], "2")
        changed_again = self.revision(second, package["body"]["text"].encode(), entries=package["assets"], asset_source=package["asset_source"])
        self.accept(changed_again, "12", supplied_assets=images)
        self.assertEqual(len(list((self.root / "assets").glob("*"))), 2)

    def test_image_hash_and_reference_tampering(self):
        package, images = self.image_package()
        result = self.accept(package, supplied_assets={"figures/test.png": png("red")})
        self.assertEqual(result["error_code"], "asset_hash_mismatch")
        changed = self.make(BODY, entries=package["assets"], asset_source=package["asset_source"])
        self.assertEqual(self.accept(changed, "11", supplied_assets=images)["error_code"], "asset_manifest_mismatch")

    def test_image_decoder_limits_and_formats(self):
        self.assertEqual(assets.inspect_image(png()), "image/png")
        for raw in (b"<svg></svg>", b"x" * (assets.MAX_IMAGE + 1), png()[:30], png(size=(5000, 4001))):
            with self.assertRaises(Rejection):
                assets.inspect_image(raw)
        stream = io.BytesIO()
        Image.new("RGB", (10, 10), "red").save(stream, format="PNG", save_all=True, append_images=[Image.new("RGB", (10, 10), "blue")])
        with self.assertRaises(Rejection):
            assets.inspect_image(stream.getvalue())

    def test_asset_paths_and_symlinks(self):
        for path in ("../a.png", "/a.png", "https://example.org/a.png", "a.svg", "a%2epng", "a//x.png"):
            with self.assertRaises(Rejection):
                assets.logical_path(path)
        (self.root / "actual.png").write_bytes(png())
        (self.root / "link.png").symlink_to(self.root / "actual.png")
        with self.assertRaises(Rejection):
            assets.read_local(self.root, "link.png")
        for body in (b"![x](https://example.org/x.png)", b"![x](../x.png)"):
            with self.assertRaises(Rejection):
                assets.references(body)

    def test_two_mib_manuscript_references_and_limit(self):
        source = {"kind": "github", "repository": "test/source", "commit": "a" * 40, "path": "paper.md"}
        body = (b"A bounded paragraph.\n\n" * 100000)[:assets.MAX_PAPER]
        package = self.make(body, source=source)
        result = verify(package, self.root, context(), False, supplied_body=body)
        self.assertEqual(len(result["body"]), assets.MAX_PAPER)
        with self.assertRaises(Rejection):
            self.make(body + b"x", source=source)

    def test_journal_recovers_after_interrupted_publish(self):
        original = works.os.replace
        count = [0]
        def crash(src, dst):
            if str(dst).endswith("/paper.md"):
                count[0] += 1
                if count[0] == 1:
                    raise OSError("simulated interruption")
            return original(src, dst)
        with patch("agent_preprints.works.os.replace", side_effect=crash):
            with self.assertRaises(OSError):
                self.accept()
        result = self.accept()
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(len(works.all_works(self.root)), 1)
        self.assertFalse(list((self.root / ".transactions").glob("*")))

    def test_legacy_migration_preserves_raw_proofs(self):
        from support import snapshot
        _, legacy = fixture(self.root)
        record = process(self.root, snapshot(legacy), False)
        before = (self.root / "papers" / record["paper_id"] / "proof.json").read_bytes()
        a = works.migrate(self.root)
        self.assertEqual(a, works.migrate(self.root))
        self.assertEqual(before, (self.root / "papers" / record["paper_id"] / "proof.json").read_bytes())
        self.assertEqual(a[0]["work_id"], "mx:2609.00001")

    def test_static_version_routes_and_deploy_status(self):
        package, images = self.image_package()
        first = self.accept(package, supplied_assets=images)
        second = self.accept(self.revision(first, BODY + b"New English text"), "11")
        out = self.root / "_site"
        manifest = build(self.root, out, "/test/", NOW)
        self.assertFalse(second["published"])
        self.assertEqual(len(read_json(out / "index.json")["papers"]), 1)
        self.assertEqual(set(manifest["paper_ids"]), {first["paper_id"], second["paper_id"]})
        for route in ("p/2609.00001/v1", "p/2609.00001/v2", "p/2609.00001", "papers/" + first["paper_id"]):
            self.assertTrue((out / route / "index.html").is_file())
        html = (out / "p/2609.00001/v1/index.html").read_text()
        self.assertIn('<img loading="lazy"', html)
        self.assertIn('/test/media/', html)
        self.assertTrue((out / "categories/math.OC/index.html").exists())
        mark_deployed(self.root, manifest, "https://test.github.io/archive/")
        current = read_json(self.root / "receipts/1-11.json")
        self.assertTrue(current["published"])
        self.assertTrue(current["url"].endswith("/p/2609.00001/v2/"))

    def test_social_edits_deletions_and_failure_do_not_persist_bodies(self):
        self.accept()
        class API:
            values = [{"id": 123, "user": {"login": "reader", "type": "User"}, "body": "First", "updated_at": NOW}]
            def issue(self, *args):
                return {"comments": len(self.values), "reactions": {"+1": 2, "-1": 1}}
            def comments(self, *args):
                return self.values
        api = API()
        a = sync(self.root, api, NOW)
        self.assertEqual(a["works"][0]["comments"][0]["body"], "First")
        api.values[0]["body"] = "Edited"
        self.assertEqual(sync(self.root, api, NOW)["works"][0]["comments"][0]["body"], "Edited")
        api.values = []
        self.assertEqual(sync(self.root, api, NOW)["works"][0]["comments"], [])
        with patch.object(api, "issue", side_effect=Rejection("network", "down", True)):
            self.assertEqual(sync(self.root, api, NOW)["works"][0]["status"], "unavailable")
        self.assertFalse((self.root / "social.json").exists())
        self.assertNotIn("<img", render_markdown("![tracking](https://evil.test/x) <script>bad</script>"))


if __name__ == "__main__":
    unittest.main()
