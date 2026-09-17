import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints import poa, pow
from agent_preprints.codec import canonical, content_hash, decimal, loads, read_json, sha, write_json
from agent_preprints.epochs import epoch_path, load_epoch, rotate
from agent_preprints.errors import Rejection
from agent_preprints.protocol import Context, verify, verify_pow
from support import BODY, NOW, complete, context, fixture


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.epoch, self.package = fixture(self.root)

    def reject(self, code, function, *args, **kwargs):
        with self.assertRaises(Rejection) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def verify(self, package=None, ctx=None):
        return verify(package or self.package, self.root, ctx or context(), production=False)

    def test_valid_package(self):
        result = self.verify()
        self.assertEqual(result["body"], BODY)
        self.assertTrue(all(r["valid"] for r in result["proof"]["results"]))

    def test_strict_json(self):
        for value in (b'{"x":1}', b'{"x":1.0}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":"a","x":"b"}',
                      b'{"x":"\\ud800"}', b'\xef\xbb\xbf{}', b'{"UPPER":"x"}'):
            self.reject("invalid_json", loads, value)
        for value in ("01", "+1", "-0", "1e3", " 1", True):
            self.reject("invalid_integer", decimal, value)
        self.assertEqual(canonical({"z": "汉字\n", "a": [None, True, "\\\""]}),
                         '{"a":[null,true,"\\\\\\\""],"z":"汉字\\n"}'.encode())

    def test_json_size_and_nesting(self):
        self.reject("input_limit", loads, b'"' + b'a' * 60000 + b'"')
        self.reject("input_limit", loads, b"[" * 26 + b'"x"' + b"]" * 26)

    def test_nonce_boundary_and_endian(self):
        head = pow.header("1", "00" * 32, "2", "11" * 32)
        digest = pow.digest(head, "0000000000000001")
        self.assertNotEqual(digest, pow.digest(head, "0100000000000000"))
        target = int.from_bytes(digest, "big")
        self.reject("invalid_pow", pow.verify, head, "0000000000000001", f"{target:064x}")
        self.assertEqual(pow.verify(head, "0000000000000001", f"{target+1:064x}"), digest)
        self.assertEqual(pow.nonce_bytes("ffffffffffffffff"), b"\xff" * 8)
        for nonce in ("1", "0" * 17, "A" * 16, "-1", 0):
            self.reject("invalid_nonce", pow.nonce_bytes, nonce)

    def test_wrong_nonce(self):
        package = copy.deepcopy(self.package)
        head = pow.header("1", package["epoch_hash"], "2", package["content_hash"])
        package["nonce"] = next(f"{n:016x}" for n in range(1000) if int.from_bytes(pow.digest(head, f"{n:016x}"), "big") >= int(self.epoch["target"], 16))
        self.reject("invalid_pow", self.verify, package)

    def test_cross_identity_and_repository(self):
        self.reject("identity_mismatch", self.verify, ctx=Context("1", "3", NOW))
        self.reject("repository_mismatch", self.verify, ctx=Context("9", "2", NOW))
        original = pow.header("1", self.package["epoch_hash"], "2", self.package["content_hash"])
        self.assertNotEqual(pow.digest(original, self.package["nonce"]), pow.digest(pow.header("9", self.package["epoch_hash"], "2", self.package["content_hash"]), self.package["nonce"]))

    def test_body_and_metadata_binding(self):
        changed = copy.deepcopy(self.package)
        changed["body"]["text"] += "x"
        self.reject("body_hash_mismatch", self.verify, changed)
        changed = copy.deepcopy(self.package)
        changed["metadata"]["title"] += " changed"
        self.reject("content_hash_mismatch", self.verify, changed)
        changed = copy.deepcopy(self.package)
        changed["body"]["text"] = changed["body"]["text"].replace("\n", "\r\n")
        self.reject("body_hash_mismatch", self.verify, changed)

    def test_epoch_bounds_and_delayed_execution(self):
        self.reject("epoch_unpublished_at_submission", self.verify, ctx=context("2026-09-17T11:59:59Z"))
        self.reject("epoch_expired", self.verify, ctx=context("2026-09-19T12:00:00Z"))
        self.verify(ctx=context("2026-09-19T11:59:59Z"))
        with patch("agent_preprints.codec.utcnow", return_value="2099-01-01T00:00:00Z"):
            self.verify()  # Original receipt time, not execution time.

    def test_not_before_and_unpublished(self):
        registry = read_json(self.root / "challenges/registry.json")
        registry["epochs"][0]["published_at"] = "2026-09-17T11:00:00Z"
        write_json(self.root / "challenges/registry.json", registry)
        self.reject("epoch_not_yet_valid", self.verify, ctx=context("2026-09-17T11:59:59Z"))
        registry["epochs"][0]["published_at"] = None
        write_json(self.root / "challenges/registry.json", registry)
        self.reject("epoch_unpublished", self.verify)

    def test_production_fails_closed(self):
        self.reject("calibration_required", verify, self.package, self.root, context())
        config = read_json(self.root / "config/production.json")
        config.update({"enabled": True, "calibration_id": "00" * 32})
        write_json(self.root / "config/production.json", config)
        self.reject("production_required", verify, self.package, self.root, context())
        changed = copy.deepcopy(self.package)
        changed["epoch_hash"] = "ff" * 32
        self.reject("epoch_hash_mismatch", self.verify, changed)
        changed["epoch_id"] = "2026-09-16"
        self.reject("unknown_epoch", self.verify, changed)

    def test_client_cannot_change_policy_or_seed(self):
        for key, value in (("seed", "00" * 32), ("poa_policy", []), ("target", "f" * 64), ("profile", "development")):
            changed = copy.deepcopy(self.package)
            changed[key] = value
            self.reject("invalid_fields", self.verify, changed)
        changed = copy.deepcopy(self.package)
        changed["answers"] = changed["answers"][:1]
        self.reject("answer_count", self.verify, changed)
        changed = copy.deepcopy(self.package)
        changed["answers"].reverse()
        self.reject("invalid_fields", self.verify, changed)
        changed = copy.deepcopy(self.package)
        changed["answers"][0]["family"] = "easy"
        self.reject("invalid_fields", self.verify, changed)

    def test_poW_before_body_fetch(self):
        changed = copy.deepcopy(self.package)
        changed["body"] = {"kind": "github", "repository": "test/source", "commit": "a" * 40, "path": "paper.md"}
        changed["nonce"] = "f" * 16
        with patch("agent_preprints.protocol.pow.verify", side_effect=Rejection("invalid_pow", "bad")):
            with patch("agent_preprints.github.GitHub.fetch_paper") as fetch:
                self.reject("invalid_pow", verify, changed, self.root, context(), False, fetch)
                fetch.assert_not_called()

    def test_epoch_rotation_idempotence_and_tamper(self):
        path = epoch_path(self.root, self.epoch["epoch_id"])
        raw = path.read_bytes()
        rotate(self.root, "2026-09-17T23:00:00Z", True)
        self.assertEqual(path.read_bytes(), raw)
        path.write_bytes(raw + b" ")
        self.reject("immutable_conflict", rotate, self.root, NOW, True)

    def test_mining_checkpoint_and_resume(self):
        path = self.root / "checkpoint.json"
        head = pow.header("1", "11" * 32, "2", "22" * 32)
        self.reject("mining_paused", pow.mine, head, "0" * 63 + "1", path, 0)
        self.assertGreater(int(read_json(path)["next_nonce"]), 0)
        self.reject("checkpoint_mismatch", pow.mine, head + b"x", "0" * 63 + "1", path)
        path.unlink()
        nonce = pow.mine(head, "f" * 64, path)
        self.assertEqual(pow.mine(head, "f" * 64, path), nonce)

    def test_golden_vector(self):
        vector = read_json(Path(__file__).parent / "fixtures" / "protocol-vector.json")
        head = pow.header(vector["repository_id"], vector["epoch_hash"], vector["submitter_id"], vector["content_hash"])
        self.assertEqual(head.hex(), vector["header_hex"])
        self.assertEqual(pow.digest(head, vector["nonce"]).hex(), vector["pow_hash"])
        self.assertEqual(pow.seed(bytes.fromhex(vector["pow_hash"])).hex(), vector["poa_seed"])
        self.assertEqual(poa.sample(bytes.fromhex(vector["poa_seed"]), poa.DEV_POLICY), vector["problems"])

    def test_published_valid_and_invalid_json_examples(self):
        examples = Path(__file__).resolve().parents[1] / "examples"
        self.verify(read_json(examples / "valid-development-submission.json"))
        self.reject("answer_count", self.verify, read_json(examples / "invalid-submission.json"))


if __name__ == "__main__":
    unittest.main()
