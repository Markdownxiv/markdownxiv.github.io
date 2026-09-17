import copy
import io
import os
import shutil
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from agent_preprints import PROTOCOL_V3, PROTOCOL_V4, assets, pow
from agent_preprints.archive import process
from agent_preprints.cli import participant_token, parser
from agent_preprints.codec import canonical, read_json, sha, write_json
from agent_preprints.epochs import initialize, load_epoch, rotate
from agent_preprints.errors import Rejection
from agent_preprints.protocol import Context, prepare, verify, verify_pow
from agent_preprints.protocol_v4 import MAX_MATERIAL, material_size, metadata_file
from agent_preprints.pull_requests import capture, evaluate
from agent_preprints.site import build
from support import BODY, NOW, complete, context
from test_v3 import PRFiles, bundle, pr, v3_fixture
from test_github import MockAPI, SOURCE


def v4_fixture(root):
    _, previous = v3_fixture(root)
    config = read_json(root / "config/production.json")
    config["protocol"] = PROTOCOL_V4
    write_json(root / "config/production.json", config)
    epoch = rotate(root, NOW, development=True, protocol=PROTOCOL_V4)
    meta = metadata_file(previous)
    package = prepare(BODY, meta, "1", "2", epoch, read_json(root / "challenges/latest.json")["epoch_hash"])
    complete(package, epoch)
    return epoch, package


def padded_png(size):
    stream = io.BytesIO()
    Image.new("RGB", (2, 2), "white").save(stream, "PNG")
    raw = stream.getvalue()
    chunk = b"npAd" + b"x" * (size - len(raw) - 12)
    return raw[:-12] + (len(chunk) - 4).to_bytes(4, "big") + chunk + zlib.crc32(chunk).to_bytes(4, "big") + raw[-12:]


class V4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.epoch, self.package = v4_fixture(self.root)

    def test_eight_mb_exact_markdown_boundary_and_plus_one(self):
        meta = metadata_file(self.package)
        size = MAX_MATERIAL - len(canonical(meta) + b"\n")
        body = b"# " + b"x" * (size - 3) + b"\n"
        package = prepare(body, meta, "1", "2", self.epoch, self.package["epoch_hash"])
        complete(package, self.epoch)
        self.assertEqual(material_size(package), MAX_MATERIAL)
        result = verify(package, self.root, context(), False, supplied_body=body, supplied_assets={})
        self.assertEqual(result["body"], body)
        with self.assertRaises(Rejection) as caught:
            prepare(body + b"x", meta, "1", "2", self.epoch, self.package["epoch_hash"])
        self.assertEqual(caught.exception.code, "material_limit")
        old = read_json(self.root / "challenges/epochs/dev-v3-2026-09-17.json")
        with self.assertRaises(Rejection):
            prepare(body, meta, "1", "2", old, sha((self.root / "challenges/epochs/dev-v3-2026-09-17.json").read_bytes()))

    def test_large_image_exact_total_collection_archive_and_build(self):
        body = b"# Image budget\n\n![Test](figures/test.png)\n"
        meta = metadata_file(self.package)
        image = padded_png(MAX_MATERIAL - len(body) - len(canonical(meta) + b"\n"))
        directory = self.root / "source"
        (directory / "figures").mkdir(parents=True)
        (directory / "figures/test.png").write_bytes(image)
        entries, data = assets.collect_local(body, directory, MAX_MATERIAL, MAX_MATERIAL)
        package = prepare(body, meta, "1", "2", self.epoch, self.package["epoch_hash"], entries=entries)
        complete(package, self.epoch)
        self.assertEqual(material_size(package), MAX_MATERIAL)
        request = capture(pr(), "test/archive", "1", NOW)
        local = {**bundle(package, body), "assets": data}
        record = process(self.root, request, False, supplied_body=local)
        self.assertTrue(record["archived"], record)
        build(self.root, self.root / "_site", "/", NOW)
        self.assertEqual((self.root / "_site/media" / assets.filename(entries[0])).read_bytes(), image)
        with self.assertRaises(Rejection):
            assets.inspect_image(image)
        with self.assertRaises(Rejection):
            prepare(body + b"x", meta, "1", "2", self.epoch, self.package["epoch_hash"], entries=entries)

    def test_github_blob_budget_covers_large_base64_and_preserves_old_cap(self):
        body = b"x" * 7_900_000
        class API(MockAPI):
            def request(self, method, path, data=None, **kwargs):
                result = super().request(method, path, data, **kwargs)
                if "/git/blobs/" in path:
                    import json
                    self.asserted_limit = kwargs["limit"]
                    assert len(json.dumps(result).encode()) <= self.asserted_limit
                return result
        api = API(body)
        self.assertEqual(api.fetch_file(SOURCE, MAX_MATERIAL), body)
        self.assertEqual(api.asserted_limit, 2 * MAX_MATERIAL)
        with self.assertRaises(Rejection):
            MockAPI(body).fetch_paper_v2(SOURCE)

    def test_pr_network_path_checks_large_v4_manuscript_and_proof_first(self):
        body = b"# " + b"x" * 2_500_000
        package = prepare(body, metadata_file(self.package), "1", "2", self.epoch, self.package["epoch_hash"])
        complete(package, self.epoch)
        api = PRFiles(package)
        api.files["paper.md"] = body
        result = evaluate(capture(pr(), "test/archive", "1", NOW), self.root, False, api)
        self.assertEqual(result["body"], body)

    def test_homepage_is_still_unbound_and_cross_protocol_fails(self):
        changed = copy.deepcopy(self.package)
        changed["author_homepages"][0] = "https://example.net/new"
        self.assertEqual(verify_pow(changed, self.root, context(), False), verify_pow(self.package, self.root, context(), False))
        changed["protocol"] = PROTOCOL_V3
        with self.assertRaises(Rejection):
            verify_pow(changed, self.root, context(), False)

    def test_thirty_second_calibration_does_not_redefine_legacy(self):
        old = read_json(next((Path(__file__).parent / "fixtures/production/challenges/calibrations").glob("*.json")))
        new = {**old, "expected_seconds": "30", "calibration_version": "ap-calibration-v2"}
        target = ((1 << 256) * int(new["elapsed_ns"])) // (int(new["attempts"]) * 30 * 1_000_000_000)
        new["target"] = f"{target:064x}"
        pow.validate_calibration(old)
        pow.validate_calibration(new, 30)
        with self.assertRaises(Rejection):
            pow.validate_calibration(new)
        with self.assertRaises(Rejection):
            pow.validate_calibration(old, 30)
        initialized = self.root / "production"
        initialize(initialized, new, "test/archive", "1", "https://test.github.io/archive/", PROTOCOL_V4)
        epoch = rotate(initialized, NOW)
        latest = read_json(initialized / "challenges/latest.json")
        with self.assertRaises(Rejection) as caught:
            load_epoch(initialized, epoch["epoch_id"], latest["epoch_hash"], NOW, "1")
        self.assertEqual(caught.exception.code, "epoch_unpublished")
        registry = read_json(initialized / "challenges/registry.json")
        registry["epochs"][0]["published_at"] = NOW
        write_json(initialized / "challenges/registry.json", registry)
        self.assertEqual(load_epoch(initialized, epoch["epoch_id"], latest["epoch_hash"], NOW, "1")["target"], new["target"])
        self.assertEqual(rotate(initialized, NOW), epoch)
        new["target"] = "f" * 64
        with self.assertRaises(Rejection):
            pow.validate_calibration(new, 30)

    def test_old_production_proof_works_with_new_platform_config(self):
        folder = self.root / "legacy"
        shutil.copytree(Path(__file__).parent / "fixtures/production", folder)
        config = read_json(folder / "config/production.json")
        config["protocol"] = PROTOCOL_V4
        write_json(folder / "config/production.json", config)
        package = read_json(folder / "submission.json")
        at = read_json(folder / "experiment.json")["received_at"]
        result = verify(package, folder, Context("1", "2", at))
        self.assertEqual(result["paper_id"], package["content_hash"])

    def test_cli_auth_reuses_gh_without_exposing_credentials(self):
        with patch.dict(os.environ, {}, clear=True), patch("agent_preprints.cli.subprocess.run") as run:
            run.return_value.returncode, run.return_value.stdout = 0, "a-secret-token\n"
            self.assertEqual(participant_token(True), "a-secret-token")
            self.assertEqual(run.call_args.args[0], ["gh", "auth", "token"])
            run.return_value.returncode, run.return_value.stdout = 1, ""
            with self.assertRaises(Rejection) as caught:
                participant_token(True)
            self.assertNotIn("a-secret-token", caught.exception.message)
        options = parser().parse_args(["calibrate", "--conditions", "test", "--out", "unused.json"])
        self.assertEqual(options.expected_seconds, 30)
