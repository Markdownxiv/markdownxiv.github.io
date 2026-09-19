import base64
import copy
import json
import multiprocessing
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_preprints import PROTOCOL_V5, PROTOCOL_V6, poi, poi_v6, pow, witnessbench
from agent_preprints.archive import process
from agent_preprints.cli import execute, parser
from agent_preprints.codec import canonical, read_json, sha, write_json
from agent_preprints.epochs import epoch_path, initialize, load_epoch, rotate, validate_epoch
from agent_preprints.errors import Rejection
from agent_preprints.pr_client import submit
from agent_preprints.protocol import Context, read_package, verify, verify_pow
from agent_preprints.protocol_v6 import MAX_MATERIAL, metadata_file, prepare, validate_package
from agent_preprints.pull_requests import capture, evaluate
from agent_preprints.site import build
from test_pr_client import ParticipantAPI
from test_v3 import PRFiles, pr


FIXTURES = Path(__file__).parent / "fixtures"
PROJECT = Path(__file__).resolve().parents[1]


class IsotropicOnlyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "archive"
        shutil.copytree(FIXTURES / "witnessbench-isotropic-development", self.root)
        self.package = read_package(self.root / "submission.json")
        self.body = (self.root / "paper.md").read_bytes()
        self.at = read_json(self.root / "experiment.json")["received_at"]
        self.context = Context("1", "2", self.at)
        self.epoch, self.digest = verify_pow(self.package, self.root, self.context, False)
        self.problems = poi_v6.sample(pow.seed(self.digest, PROTOCOL_V6), self.epoch["poa_policy"])

    def test_only_isotropic_is_sampled_and_verified_at_both_profiles(self):
        for fixture in ("witnessbench-isotropic-development", "witnessbench-isotropic-full-profile"):
            with self.subTest(fixture=fixture):
                root = FIXTURES / fixture
                package = read_package(root / "submission.json")
                with patch.object(witnessbench, "sample", wraps=witnessbench.sample) as sampler:
                    result = verify(package, root, self.context, False, supplied_body=self.body, supplied_assets={})
                self.assertEqual(sampler.call_count, 1)
                self.assertEqual(sampler.call_args.args[0], "isotropic")
                self.assertIsNotNone(sampler.call_args.kwargs["index"])
                self.assertEqual(result["proof"]["results"], [{"family": "common-isotropic-v1", "valid": True}])
                self.assertEqual(len(result["proof"]["problems"]), 1)
                if fixture.endswith("full-profile"):
                    self.assertEqual(result["proof"]["problems"][0]["instance"]["parameters"],
                                     {"p": "3", "m": "8", "k": "3", "n": "35"})

    def test_question_derivation_binds_protocol_and_matches_fixed_instance(self):
        seed = pow.seed(self.digest, PROTOCOL_V6)
        self.assertNotEqual(seed, pow.seed(self.digest, PROTOCOL_V5))
        self.assertEqual(poi_v6.sample(seed, self.epoch["poa_policy"]), self.problems)
        self.assertEqual(self.problems[0]["instance"]["instance_id"], self.package["answers"][0]["instance_id"])
        self.assertNotEqual(poi_v6.sample(bytes(32), self.epoch["poa_policy"]), self.problems)
        self.assertEqual(self.problems[0], poi.sample_problem(seed, 0, poi_v6.DEV_POLICY[0]))

    def test_empty_additional_and_wrong_family_answers_are_rejected(self):
        old = read_package(FIXTURES / "witnessbench-development/submission.json")
        for answers in ([], self.package["answers"] * 2, old["answers"], [old["answers"][0]]):
            package = {**self.package, "answers": answers}
            with self.subTest(count=len(answers)), self.assertRaises(Rejection):
                verify(package, self.root, self.context, False, supplied_body=self.body, supplied_assets={})
        validate_package({**self.package, "answers": []})
        with self.assertRaises(Rejection):
            poi_v6.verify_all([{"family": "picard-fuchs-v1"}], self.package["answers"])

    def test_old_v5_contract_cannot_be_relaxed_or_relabelled(self):
        root = FIXTURES / "witnessbench-development"
        package = read_package(root / "submission.json")
        at = read_json(root / "experiment.json")["received_at"]
        context = Context("1", "2", at)
        body = (root / "paper.md").read_bytes()
        result = verify(package, root, context, False, supplied_body=body, supplied_assets={})
        self.assertEqual(len(result["proof"]["results"]), 2)
        with self.assertRaises(Rejection):
            verify({**package, "answers": package["answers"][1:]}, root, context, False, supplied_body=body, supplied_assets={})
        with self.assertRaises(Rejection):
            verify({**package, "protocol": PROTOCOL_V6}, root, context, False, supplied_body=body, supplied_assets={})

    def test_bound_identity_basis_and_formats_are_checked(self):
        mutations = [{"instance_id": "0" * 64}, {"basis": [["0"] * 3]}, {"basis": [["0", "1"]]},
                     {"basis": [["0", "1", "3"]]}, {"basis": [["0", "1", True]]},
                     {"basis": [["0", "1", "01"]]}, {"basis": [["0", "1", "-1"]]},
                     {"basis": [["0", "1", "2"], ["0", "1", "2"]]}, {"extra": "forbidden"}]
        for mutation in mutations:
            answer = {**self.package["answers"][0], **mutation}
            with self.subTest(mutation=mutation), self.assertRaises(Rejection):
                poi_v6.verify_all(self.problems, [answer])

    def test_full_profile_requires_all_cross_terms_and_independence(self):
        instance = witnessbench.sample("isotropic", index=0, p=3, m=8, k=3)
        vectors = [[int(i == j) for i in range(35)] for j in range(3)]
        answer = {"instance_id": instance["instance_id"], "basis": vectors}
        problem = {"family": "common-isotropic-v1", "instance": poi.encode(instance)}
        self.assertEqual(poi_v6.verify_all([problem], [poi.encode(answer)]), [{"family": "common-isotropic-v1", "valid": True}])
        instance["coefficients"][0][1] = 1
        instance = witnessbench.bind({k: v for k, v in instance.items() if k != "instance_id"})
        problem["instance"] = poi.encode(instance)
        answer["instance_id"] = instance["instance_id"]
        with self.assertRaises(Rejection):
            poi_v6.verify_all([problem], [poi.encode(answer)])
        answer["basis"][1] = vectors[0][:]
        with self.assertRaises(Rejection):
            poi_v6.verify_all([problem], [poi.encode(answer)])

    def test_resource_limit_and_worker_cleanup(self):
        before = {p.pid for p in multiprocessing.active_children()}
        with self.assertRaises(Rejection) as caught:
            poi_v6.verify_all(self.problems, self.package["answers"], seconds=0)
        self.assertEqual(caught.exception.code, "verification_resource_limit")
        self.assertEqual(before, {p.pid for p in multiprocessing.active_children()})
        with self.assertRaises(Rejection):
            poi_v6.verify_all(self.problems, [{"instance_id": "0" * 450001, "basis": []}])

    def test_cli_questions_and_native_answer_packing_use_only_one_instance(self):
        native = [poi.native_answer(self.problems[0], self.package["answers"][0])]
        (self.root / "answers.json").write_text(json.dumps(native))
        for command in ("questions", "pack", "verify"):
            args = [command, "--root", str(self.root), "--package", str(self.root / "submission.json"), "--dev"]
            if command == "questions":
                args += ["--out", str(self.root / "questions.json"), "--markdown", str(self.root / "questions.md")]
            else:
                args += ["--paper", str(self.root / "paper.md")]
                if command == "pack":
                    args += ["--answers", str(self.root / "answers.json"), "--out", str(self.root / "packed.json")]
            with patch("agent_preprints.cli.utcnow", return_value=self.at), patch("agent_preprints.cli._emit"):
                execute(parser().parse_args(args))
        self.assertEqual(read_package(self.root / "packed.json"), self.package)
        self.assertEqual(read_json(self.root / "questions.json")["problems"], self.problems)
        statement = (self.root / "questions.md").read_text()
        self.assertIn("one-element JSON array", statement)
        self.assertIn("Common Totally Isotropic", statement)
        self.assertNotIn("Picard", statement)
        self.assertNotIn("both", statement)

    def test_pr_revalidation_archives_one_certificate_and_preserves_raw_bytes(self):
        request = capture(pr(), "test/archive", "1", self.at)
        api = PRFiles(self.package)
        api.files["paper.md"] = self.body
        result = evaluate(request, self.root, False, api)
        self.assertEqual(len(result["proof"]["results"]), 1)
        api.reads.clear()
        with patch("agent_preprints.pull_requests.verify_pow", side_effect=Rejection("invalid_pow", "Invalid")):
            with self.assertRaises(Rejection):
                evaluate(request, self.root, False, api)
        self.assertEqual(api.reads, [api.directory + "submission.json"])
        receipt = process(self.root, request, False, supplied_body={"package": self.package, "paper": self.body,
                          "metadata": canonical(metadata_file(self.package)) + b"\n", "assets": {}})
        self.assertTrue(receipt["archived"], receipt)
        self.assertEqual(receipt, process(self.root, request, False))
        output = self.root / "_site"
        build(self.root, output, "/", self.at)
        self.assertEqual((output / "md/2609.00001.md").read_bytes(), self.body)
        self.assertEqual(read_json(output / "abs/2609.00001/proof.json")["package"]["answers"], self.package["answers"])
        for route in ("submit/index.html", "about/index.html", "challenge/index.html", "llms.txt"):
            self.assertNotIn("Picard-Fuchs", (output / route).read_text())

    def test_client_uploads_only_the_single_certificate_package(self):
        api = ParticipantAPI()
        from agent_preprints.protocol import verify as real_verify
        def local_verify(package, root, context, production, **kwargs):
            return real_verify(package, root, self.context, False, **kwargs)
        with patch("agent_preprints.pr_client.verify", side_effect=local_verify):
            result = submit(api, "test/archive", self.package, self.root, self.body, {}, self.root / "checkpoint.json")
        self.assertEqual(result["number"], 10)
        blobs = [base64.b64decode(data["content"]) for method, path, data in api.calls if path.endswith("/git/blobs")]
        self.assertIn(canonical(self.package) + b"\n", blobs)
        tree = next(data for _, path, data in api.calls if path.endswith("/git/trees"))
        self.assertEqual(len(tree["tree"]), 3)

    def test_production_profile_and_publication_remain_fail_closed(self):
        source = PROJECT / "challenges/calibrations/f869e8bedc49e3a70c99ed1c9ca8374b7c269ee47f70c4536fb6a4143ed9e2a7.json"
        calibration = read_json(source)
        initialize(self.root, calibration, "test/archive", "1", "https://test.github.io/archive/", PROTOCOL_V6)
        with self.assertRaises(Rejection) as caught:
            verify(self.package, self.root, self.context, True, supplied_body=self.body, supplied_assets={})
        self.assertEqual(caught.exception.code, "production_required")
        epoch = rotate(self.root, self.at)
        self.assertEqual(epoch["question_count"], "1")
        self.assertEqual(epoch["poa_policy"], poi_v6.PRODUCTION_POLICY)
        self.assertEqual(epoch["target"], calibration["target"])
        self.assertEqual(rotate(self.root, self.at), epoch)
        digest = sha(epoch_path(self.root, epoch["epoch_id"]).read_bytes())
        with self.assertRaises(Rejection) as caught:
            load_epoch(self.root, epoch["epoch_id"], digest, self.at, "1", True)
        self.assertEqual(caught.exception.code, "epoch_unpublished")
        for changes in ({"question_count": "2"}, {"poa_policy": poi_v6.DEV_POLICY}, {"poa_policy": poi.PRODUCTION_POLICY}):
            with self.subTest(changes=changes), self.assertRaises(Rejection):
                validate_epoch({**epoch, **changes})
        registry = read_json(self.root / "challenges/registry.json")
        registry["epochs"][-1]["published_at"] = self.at
        write_json(self.root / "challenges/registry.json", registry)
        self.assertEqual(load_epoch(self.root, epoch["epoch_id"], digest, self.at, "1", True), epoch)
        path = self.root / "challenges/calibrations" / (epoch["calibration_id"] + ".json")
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaises(Rejection) as caught:
            load_epoch(self.root, epoch["epoch_id"], digest, self.at, "1", True)
        self.assertEqual(caught.exception.code, "calibration_required")

    def test_production_pr_requires_current_protocol_but_old_local_proofs_still_verify(self):
        old = read_package(FIXTURES / "witnessbench-development/submission.json")
        request = capture(pr(), "test/archive", "1", self.at)
        api = PRFiles(old)
        with self.assertRaises(Rejection) as caught:
            evaluate(request, self.root, True, api)
        self.assertEqual(caught.exception.code, "protocol_version")
        self.assertEqual(api.reads, [api.directory + "submission.json"])

    def test_material_budget_and_identity_binding_unchanged(self):
        meta = metadata_file(self.package)
        overhead = len(canonical(meta)) + 1
        body = b"x" * (MAX_MATERIAL - overhead)
        prepare(body, meta, "1", "2", self.epoch, self.package["epoch_hash"])
        with self.assertRaises(Rejection):
            prepare(body + b"x", meta, "1", "2", self.epoch, self.package["epoch_hash"])
        with self.assertRaises(Rejection) as caught:
            verify(self.package, self.root, Context("1", "3", self.at), False, supplied_body=self.body, supplied_assets={})
        self.assertEqual(caught.exception.code, "identity_mismatch")


if __name__ == "__main__":
    unittest.main()
