import copy
import json
import multiprocessing
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints import PROTOCOL_V4, PROTOCOL_V5, poi, pow, witnessbench
from agent_preprints.archive import process
from agent_preprints.cli import execute, parser
from agent_preprints.codec import canonical, loads, read_json, sha, write_json
from agent_preprints.epochs import epoch_path, initialize, load_epoch, rotate, validate_epoch
from agent_preprints.errors import Rejection
from agent_preprints.protocol import Context, load_package, read_package, verify, verify_pow
from agent_preprints.protocol_v5 import MAX_PACKAGE, MAX_MATERIAL, metadata_file, prepare
from agent_preprints.pull_requests import capture, evaluate
from agent_preprints.site import build
from test_v3 import PRFiles, pr, v3_fixture


FIXTURES = Path(__file__).parent / "fixtures"
PROJECT = Path(__file__).resolve().parents[1]


class WitnessBenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "archive"
        shutil.copytree(FIXTURES / "witnessbench-development", self.root)
        self.package = read_package(self.root / "submission.json")
        self.body = (self.root / "paper.md").read_bytes()
        self.at = read_json(self.root / "experiment.json")["received_at"]
        self.context = Context("1", "2", self.at)
        self.epoch, self.digest = verify_pow(self.package, self.root, self.context, False)
        self.problems = poi.sample(pow.seed(self.digest, PROTOCOL_V5), self.epoch["poa_policy"])

    def test_upstream_verifier_is_the_supplied_unmodified_public_file(self):
        self.assertEqual(sha(Path(witnessbench.__file__).read_bytes()), "6d8e81c71f11539359a11252a71b7636d6227ba383dca3bae6c8b87e2c1d405f")

    def test_fixed_bound_certificates_verify_without_any_solver(self):
        with patch.object(witnessbench, "sample", wraps=witnessbench.sample) as sampler:
            result = verify(self.package, self.root, self.context, False, supplied_body=self.body, supplied_assets={})
        self.assertEqual([v["family"] for v in result["proof"]["results"]], list(poi.FAMILIES))
        self.assertEqual(result["proof"]["problems"], self.problems)
        self.assertEqual(len(sampler.call_args_list), 2)
        self.assertTrue(all(call.kwargs["index"] is not None for call in sampler.call_args_list))
        self.assertNotEqual(pow.seed(self.digest), pow.seed(self.digest, PROTOCOL_V5))

    def test_full_production_parameters_with_development_epoch(self):
        root = FIXTURES / "witnessbench-full-profile"
        package = read_package(root / "submission.json")
        result = verify(package, root, self.context, False, supplied_body=(root / "paper.md").read_bytes(), supplied_assets={})
        problems = result["proof"]["problems"]
        self.assertEqual(problems[0]["instance"]["parameters"], {"genus": "2", "t_degree": "2", "bound": "3"})
        self.assertEqual(problems[1]["instance"]["parameters"], {"p": "3", "m": "8", "k": "3", "n": "35"})
        self.assertTrue(all(item["valid"] for item in result["proof"]["results"]))

    def test_sampling_is_deterministic_and_matches_upstream_numeric_digest(self):
        again = poi.sample(pow.seed(self.digest, PROTOCOL_V5), self.epoch["poa_policy"])
        self.assertEqual(again, self.problems)
        other = poi.sample(bytes(32), self.epoch["poa_policy"])
        self.assertNotEqual(other, self.problems)
        for problem in self.problems:
            instance = poi.native_instance(problem)
            digest = witnessbench.bind({key: value for key, value in instance.items() if key != "instance_id"})["instance_id"]
            self.assertEqual(digest, problem["instance"]["instance_id"])
        malformed = copy.deepcopy(self.problems)
        malformed[0]["instance"]["coefficients"][0][0] = "9"
        with self.assertRaises(Rejection):
            poi.verify_all(malformed, self.package["answers"])

    def test_wrong_certificate_instance_zero_rank_and_operator_are_rejected(self):
        cases = []
        bad = copy.deepcopy(self.package["answers"])
        bad[0]["instance_id"] = "0" * 64
        cases.append(bad)
        bad = copy.deepcopy(self.package["answers"])
        bad[0]["operator"][-1] = []
        cases.append(bad)
        bad = copy.deepcopy(self.package["answers"])
        bad[1]["basis"] = [["0"] * 3]
        cases.append(bad)
        bad = copy.deepcopy(self.package["answers"])
        bad[0]["operator"][0] = [["0", "7"]]
        cases.append(bad)
        bad = copy.deepcopy(self.package["answers"])
        bad[0]["certificate"] = [["0", "0", "1"], ["0", "0", "2"]]
        cases.append(bad)
        for answers in cases:
            with self.subTest(answers=cases.index(answers)), self.assertRaises(Rejection):
                poi.verify_all(self.problems, answers)
        scaled = copy.deepcopy(self.package["answers"])
        for poly in scaled[0]["operator"] + [scaled[0]["certificate"]]:
            for term in poly:
                term[-1] = str(int(term[-1]) * 2)
        self.assertTrue(all(r["valid"] for r in poi.verify_all(self.problems, scaled)))

    def test_isotropic_verifier_checks_cross_terms_and_rank(self):
        native = witnessbench.sample("isotropic", index=0, m=1, k=2)
        native["coefficients"][0][1] = 1
        native = witnessbench.bind({k: v for k, v in native.items() if k != "instance_id"})
        n = native["parameters"]["n"]
        basis = [[int(i == j) for i in range(n)] for j in (0, 1)]
        answer = {"instance_id": native["instance_id"], "basis": basis}
        self.assertFalse(witnessbench.verify(native, answer)["accepted"])
        answer["basis"][1] = basis[0][:]
        self.assertFalse(witnessbench.verify(native, answer)["accepted"])

    def test_byte_integer_and_term_limits_are_fail_closed(self):
        for value in (True, 1.0, "01", "-0", "1e2", "9" * 3615):
            answer = copy.deepcopy(self.package["answers"])
            answer[0]["operator"][-1][0][-1] = value
            with self.subTest(value=str(value)[:8]), self.assertRaises(Rejection):
                poi.verify_all(self.problems, answer)
        for certificate in ([["0", "0", "1"]] * 6001, [["0", "0", "9" * 450001]]):
            answer = copy.deepcopy(self.package["answers"])
            answer[0]["certificate"] = certificate
            with self.assertRaises(Rejection):
                poi.verify_all(self.problems, answer)

    def test_timeout_reaps_worker_and_is_not_reported_as_invalid_math(self):
        before = {p.pid for p in multiprocessing.active_children()}
        started = time.monotonic()
        with self.assertRaises(Rejection) as caught:
            poi.verify_all(self.problems, self.package["answers"], seconds=0)
        self.assertEqual(caught.exception.code, "verification_resource_limit")
        self.assertLess(time.monotonic() - started, 3)
        self.assertEqual({p.pid for p in multiprocessing.active_children()}, before)

    def test_v5_package_supports_larger_certificates_without_widening_old_protocols(self):
        package = copy.deepcopy(self.package)
        for poly in package["answers"][0]["operator"] + [package["answers"][0]["certificate"]]:
            for term in poly:
                term[-1] = str(int(term[-1]) * 10**2500)
        raw = canonical(package) + b"\n"
        self.assertGreater(len(raw), 60000)
        self.assertEqual(load_package(raw), package)
        verify(package, self.root, self.context, False, supplied_body=self.body, supplied_assets={})
        old = {**package, "protocol": PROTOCOL_V4}
        with self.assertRaises(Rejection):
            load_package(canonical(old))
        with self.assertRaises(Rejection):
            load_package(raw + b" " * MAX_PACKAGE)

    def test_native_integer_answers_are_only_converted_at_v5_cli_boundary(self):
        answers = [poi.native_answer(p, a) for p, a in zip(self.problems, self.package["answers"])]
        raw = json.dumps(answers).encode()
        self.assertEqual(loads(raw, stringify_integers=True), self.package["answers"])
        with self.assertRaises(Rejection):
            loads(raw)
        for raw in (b'{"a":1,"a":2}', b'[1.5]', b'[NaN]'):
            with self.assertRaises(Rejection):
                loads(raw, stringify_integers=True)
        (self.root / "answers.json").write_bytes(json.dumps(answers).encode())
        for command in ("questions", "pack"):
            arguments = [command, "--root", str(self.root), "--package", str(self.root / "submission.json"), "--dev", "--out", str(self.root / "result.json")]
            if command == "pack":
                arguments += ["--answers", str(self.root / "answers.json"), "--paper", str(self.root / "paper.md")]
            else:
                arguments += ["--markdown", str(self.root / "questions.md")]
            with patch("agent_preprints.cli.utcnow", return_value=self.at), patch("agent_preprints.cli._emit"):
                execute(parser().parse_args(arguments))
        self.assertEqual(read_package(self.root / "result.json"), self.package)
        text = (self.root / "questions.md").read_text()
        self.assertIn("Picard-Fuchs", text)
        self.assertIn("Common Totally Isotropic", text)
        self.assertIn("Do not publish solution walkthroughs", text)

    def test_pr_admission_publication_and_pow_before_body_read(self):
        request = capture(pr(), "test/archive", "1", self.at)
        api = PRFiles(self.package)
        api.files["paper.md"] = self.body
        result = evaluate(request, self.root, False, api)
        self.assertEqual(result["body"], self.body)
        api.reads.clear()
        with patch("agent_preprints.pull_requests.verify_pow", side_effect=Rejection("invalid_pow", "Invalid")):
            with self.assertRaises(Rejection):
                evaluate(request, self.root, False, api)
        self.assertEqual(api.reads, [api.directory + "submission.json"])
        receipt = process(self.root, request, False, supplied_body={"package": self.package, "paper": self.body,
                          "metadata": canonical(metadata_file(self.package)) + b"\n", "assets": {}})
        self.assertTrue(receipt["archived"], receipt)
        output = self.root / "_site"
        build(self.root, output, "/", self.at)
        self.assertEqual((output / "md/2609.00001.md").read_bytes(), self.body)
        self.assertEqual(read_json(output / "abs/2609.00001/proof.json")["protocol"], PROTOCOL_V5)

    def test_measured_production_epoch_and_development_rejection(self):
        cal_path = PROJECT / "challenges/calibrations/f869e8bedc49e3a70c99ed1c9ca8374b7c269ee47f70c4536fb6a4143ed9e2a7.json"
        calibration = read_json(cal_path)
        initialize(self.root, calibration, "test/archive", "1", "https://test.github.io/archive/", PROTOCOL_V5)
        with self.assertRaises(Rejection) as caught:
            verify(self.package, self.root, self.context, True, supplied_body=self.body, supplied_assets={})
        self.assertEqual(caught.exception.code, "production_required")
        epoch = rotate(self.root, self.at)
        self.assertEqual(epoch["poa_policy"], poi.PRODUCTION_POLICY)
        self.assertEqual(epoch["target"], calibration["target"])
        digest = sha(epoch_path(self.root, epoch["epoch_id"]).read_bytes())
        with self.assertRaises(Rejection) as caught:
            load_epoch(self.root, epoch["epoch_id"], digest, self.at, "1", True)
        self.assertEqual(caught.exception.code, "epoch_unpublished")
        downgraded = {**epoch, "poa_policy": poi.DEV_POLICY}
        with self.assertRaises(Rejection):
            validate_epoch(downgraded)

    def test_material_limit_stays_eight_mb(self):
        metadata = metadata_file(self.package)
        overhead = len(canonical(metadata)) + 1
        body = b"x" * (MAX_MATERIAL - overhead)
        package = prepare(body, metadata, "1", "2", self.epoch, self.package["epoch_hash"])
        self.assertEqual(int(package["paper_size"]) + overhead, MAX_MATERIAL)
        with self.assertRaises(Rejection):
            prepare(body + b"x", metadata, "1", "2", self.epoch, self.package["epoch_hash"])

    def test_new_production_pr_cannot_fall_back_to_the_old_gate(self):
        _, old = v3_fixture(self.root)
        config = read_json(self.root / "config/production.json")
        config["protocol"] = PROTOCOL_V5
        write_json(self.root / "config/production.json", config)
        api = PRFiles(old)
        snapshot = capture(pr(), "test/archive", "1", self.at)
        with self.assertRaises(Rejection) as caught:
            evaluate(snapshot, self.root, True, api)
        self.assertEqual(caught.exception.code, "protocol_version")
        self.assertEqual(api.reads, [api.directory + "submission.json"])
