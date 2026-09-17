import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints.codec import read_json, write_json
from agent_preprints.epochs import rotate
from agent_preprints.errors import Rejection
from agent_preprints.protocol import Context, verify


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "fixture"
        source = Path(__file__).parent / "fixtures/production"
        shutil.copytree(source, self.root)
        self.package = read_json(self.root / "submission.json")
        self.experiment = read_json(self.root / "experiment.json")
        self.context = Context("1", "2", self.experiment["received_at"])

    def test_real_measured_target_and_saved_production_certificate(self):
        # No mining and no solver: only constant-time PoW and bounded certificate verification.
        with patch("agent_preprints.pow.mine", side_effect=AssertionError("Server must not mine")):
            result = verify(self.package, self.root, self.context)
        self.assertEqual(result["paper_id"], self.experiment["paper_id"])
        self.assertEqual(result["proof"]["problems"][0]["degree"], "192")
        self.assertEqual(result["proof"]["problems"][1]["size"], "96")

    def test_unpublished_epoch_is_not_production_admission(self):
        registry = read_json(self.root / "challenges/registry.json")
        registry["epochs"][0]["published_at"] = None
        write_json(self.root / "challenges/registry.json", registry)
        with self.assertRaises(Rejection) as caught:
            verify(self.package, self.root, self.context)
        self.assertEqual(caught.exception.code, "epoch_unpublished")

    def test_calibration_hash_corruption_fails_closed(self):
        path = next((self.root / "challenges/calibrations").glob("*.json"))
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaises(Rejection) as caught:
            verify(self.package, self.root, self.context)
        self.assertEqual(caught.exception.code, "calibration_required")

    def test_client_cannot_supply_easy_target(self):
        changed = copy.deepcopy(self.package)
        changed["target"] = "f" * 64
        with self.assertRaises(Rejection) as caught:
            verify(changed, self.root, self.context)
        self.assertEqual(caught.exception.code, "invalid_fields")

    def test_calibrated_rotation_is_idempotent_and_new_salt_each_day(self):
        previous = rotate(self.root, self.experiment["received_at"])
        again = rotate(self.root, self.experiment["received_at"])
        self.assertEqual(previous, again)
        next_epoch = rotate(self.root, "2026-09-18T08:00:00Z")
        self.assertNotEqual(previous["salt"], next_epoch["salt"])
        self.assertEqual(previous["target"], next_epoch["target"])
        self.assertIsNone(read_json(self.root / "challenges/registry.json")["epochs"][-1]["published_at"])
