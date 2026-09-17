import copy
import itertools
import time
import unittest

from agent_preprints import poa
from agent_preprints.errors import Rejection
from support import solve
from reference_solvers import assignment, factor


class MathTests(unittest.TestCase):
    def test_sampling_is_reproducible_and_changes_content(self):
        a = poa.sample(bytes(32), poa.DEV_POLICY)
        self.assertEqual(a, poa.sample(bytes(32), poa.DEV_POLICY))
        b = poa.sample(bytes([1]) * 32, poa.DEV_POLICY)
        self.assertNotEqual(a[0]["polynomial"], b[0]["polynomial"])
        self.assertNotEqual(a[1]["costs"], b[1]["costs"])

    def test_many_actual_instances(self):
        for i in range(24):
            problems = poa.sample(i.to_bytes(32, "big"), poa.DEV_POLICY)
            self.assertTrue(all(r["valid"] for r in poa.verify_all(problems, solve(problems))))

    def test_all_degree_eight_polynomials(self):
        # Independent trial division confirms irreducibility of the returned factors.
        for f in range(257, 512, 2):
            answer = {"factors": list(map(str, factor(f)))}
            poa.verify({"family": "gf2-factor-v1", "degree": "8", "polynomial": str(f)}, answer)
            for g in map(int, answer["factors"]):
                for trial in range(2, 1 << ((g.bit_length() - 1) // 2 + 1)):
                    self.assertNotEqual(poa.pmod(g, trial), 0)

    def test_irreducibility_is_not_just_product(self):
        f = poa.pmul(0b10011, 0b10011)
        problem = {"family": "gf2-factor-v1", "degree": "8", "polynomial": str(f)}
        poa.verify(problem, {"factors": ["19", "19"]})
        with self.assertRaises(Rejection):
            poa.verify(problem, {"factors": [str(f)]})
        with self.assertRaises(Rejection):
            poa.verify(problem, {"factors": ["19", "17"]})

    def test_repeated_factors_and_upper_degree(self):
        f = (1 << 256) | 1  # (x+1)^256 in characteristic two
        poa.verify({"family": "gf2-factor-v1", "degree": "256", "polynomial": str(f)}, {"factors": ["3"] * 256})

    def test_assignment_optimum_against_exhaustive_search(self):
        costs = [[7, 2, 8, 3], [9, 4, 1, 9], [8, 4, 6, 3], [5, 8, 3, 5]]
        answer = assignment(costs)
        objective = sum(costs[i][int(j)] for i, j in enumerate(answer["permutation"]))
        brute = min(sum(costs[i][j] for i, j in enumerate(p)) for p in itertools.permutations(range(4)))
        self.assertEqual(objective, brute)
        problem = {"family": "assignment-dual-v1", "size": "4", "cost_bits": "4", "costs": [[str(c) for c in r] for r in costs]}
        poa.verify(problem, answer)
        shifted = copy.deepcopy(answer)
        shifted["u"] = [str(int(v) + 1) for v in answer["u"]]
        shifted["v"] = [str(int(v) - 1) for v in answer["v"]]
        poa.verify(problem, shifted)

    def test_multiple_perfect_matchings(self):
        problem = {"family": "assignment-dual-v1", "size": "2", "cost_bits": "4", "costs": [["7", "7"], ["7", "7"]]}
        for p in (["0", "1"], ["1", "0"]):
            poa.verify(problem, {"permutation": p, "u": ["7", "7"], "v": ["0", "0"]})

    def test_bad_dual_and_fake_matching(self):
        problem = poa.sample(bytes(32), poa.DEV_POLICY)[1]
        valid = solve([problem])[0]
        for key, value in (("u", ["9999999999999999999"] * 6), ("permutation", ["0"] * 6), ("v", ["1"] * 6)):
            answer = copy.deepcopy(valid)
            answer[key] = value
            with self.assertRaises(Rejection):
                poa.verify(problem, answer)

    def test_certificate_and_parameter_limits(self):
        problem = poa.sample(bytes(32), poa.DEV_POLICY)[0]
        for answer in ({"factors": ["9" * 25000]}, {"factors": ["9" * 81]}, {"factors": []}, {"factors": ["3"] * 1000}):
            with self.assertRaises(Rejection):
                poa.verify(problem, answer)
        for value in ("7", "257", "-1"):
            policy = copy.deepcopy(poa.DEV_POLICY)
            policy[0]["degree"] = value
            with self.assertRaises(Rejection):
                poa.sample(bytes(32), policy)
        with self.assertRaises(Rejection):
            poa.validate_policy(poa.DEV_POLICY, production=True)

    def test_timeout_is_explicit_and_retryable(self):
        problems = poa.sample(bytes(32), poa.DEV_POLICY)
        with self.assertRaises(Rejection) as caught:
            poa.verify_all(problems, solve(problems), seconds=-1)
        self.assertEqual(caught.exception.code, "verification_timeout")
        self.assertTrue(caught.exception.retryable)

    def test_family_interface_rejects_malformed_problem_objects(self):
        problem = poa.sample(bytes(32), poa.DEV_POLICY)[1]
        answer = solve([problem])[0]
        for costs in ([], [[]] * 6, [["00"] * 6] * 6, [["9" * 1000] * 6] * 6, [["-1"] * 6] * 6):
            with self.assertRaises(Rejection) as caught:
                poa.verify({**problem, "costs": costs}, answer)
            self.assertEqual(caught.exception.code, "invalid_problem")
