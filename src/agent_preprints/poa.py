"""Versioned deterministic tasks; no solvers or hidden planted answers in this module."""
import hashlib
import time

from .codec import canonical, decimal, fields
from .errors import Rejection, require

DEV_POLICY = [{"family": "gf2-factor-v1", "degree": "20"},
              {"family": "assignment-dual-v1", "size": "6", "cost_bits": "12"}]
PRODUCTION_POLICY = [{"family": "gf2-factor-v1", "degree": "192"},
                     {"family": "assignment-dual-v1", "size": "96", "cost_bits": "30"}]


class Stream:
    def __init__(self, seed, index):
        self.prefix = b"agent-preprints-sample-v1\0" + seed + index.to_bytes(4, "big")
        self.counter = 0
        self.buffer = b""

    def take(self, length):
        while len(self.buffer) < length:
            self.buffer += hashlib.sha256(self.prefix + self.counter.to_bytes(4, "big")).digest()
            self.counter += 1
        result, self.buffer = self.buffer[:length], self.buffer[length:]
        return result

    def bits(self, count):
        return int.from_bytes(self.take((count + 7) // 8), "big") & ((1 << count) - 1)


def validate_policy(policy, production=False):
    require(isinstance(policy, list) and len(policy) == 2, "invalid_policy", "Exactly two tasks are required.")
    seen = set()
    for item in policy:
        require(isinstance(item, dict), "invalid_policy", "Invalid family policy.")
        family = item.get("family")
        if family == "gf2-factor-v1":
            fields(item, ["family", "degree"])
            decimal(item["degree"], 128 if production else 8, 256)
        elif family == "assignment-dual-v1":
            fields(item, ["family", "size", "cost_bits"])
            decimal(item["size"], 64 if production else 2, 128)
            decimal(item["cost_bits"], 20 if production else 4, 30)
        else:
            raise Rejection("unknown_family", "Unsupported mathematical family version.")
        seen.add(family)
    require(seen == {"gf2-factor-v1", "assignment-dual-v1"}, "invalid_policy", "Both mathematical families are required.")


def sample(seed, policy):
    require(isinstance(seed, bytes) and len(seed) == 32, "invalid_seed", "Expected a 32-byte derived seed.")
    validate_policy(policy)
    result = []
    for index, params in enumerate(policy):
        stream = Stream(seed, index)
        family = params["family"]
        if family == "gf2-factor-v1":
            degree = int(params["degree"])
            polynomial = (1 << degree) | stream.bits(degree) | 1
            result.append({"family": family, "polynomial": str(polynomial), "degree": str(degree)})
        else:
            size, bits = int(params["size"]), int(params["cost_bits"])
            result.append({"family": family, "size": str(size), "cost_bits": str(bits),
                           "costs": [[str(stream.bits(bits)) for _ in range(size)] for _ in range(size)]})
    return result


class Budget:
    def __init__(self, seconds=2.0):
        self.deadline = time.monotonic() + seconds

    def check(self):
        if time.monotonic() > self.deadline:
            raise Rejection("verification_timeout", "Mathematical verification exceeded its time budget.", True)


def pmod(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def pmul(a, b):
    value = 0
    while b:
        if b & 1:
            value ^= a
        a <<= 1
        b >>= 1
    return value


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def irreducible(f, budget):
    """Rabin criterion over F2: x^(2^d)=x and coprimality at d/q."""
    d = f.bit_length() - 1
    if d < 1:
        return False
    n, q, divisors = d, 2, set()
    while q * q <= n:
        if n % q == 0:
            divisors.add(q)
            while n % q == 0:
                n //= q
        q += 1
    if n > 1:
        divisors.add(n)
    checkpoints = {d // prime for prime in divisors}
    x = pmod(2, f)
    power = x
    for k in range(1, d + 1):
        budget.check()
        power = pmod(pmul(power, power), f)
        if k in checkpoints and pgcd(power ^ x, f) != 1:
            return False
    return power == x


def verify(problem, answer, budget=None):
    budget = budget or Budget()
    budget.check()
    require(len(canonical(answer)) <= 24_000, "certificate_limit", "Certificate exceeds 24000 bytes.")
    family = problem["family"]
    if family == "gf2-factor-v1":
        fields(problem, ["family", "degree", "polynomial"])
        fields(answer, ["factors"])
        degree = decimal(problem["degree"], 8, 256)
        f = decimal(problem["polynomial"], 1 << degree, (1 << (degree + 1)) - 1)
        factors = answer["factors"]
        require(isinstance(factors, list) and 1 <= len(factors) <= degree,
                "invalid_certificate", "Expected a bounded list of irreducible factors with multiplicity.")
        values = [decimal(v, 2, (1 << (degree + 1)) - 1) for v in factors]
        require(sum(v.bit_length() - 1 for v in values) == degree,
                "invalid_certificate", "Factor degrees do not add up.")
        product = 1
        for value in values:
            budget.check()
            product = pmul(product, value)
        require(product == f, "invalid_certificate", "Factor product does not equal the sampled polynomial.")
        require(all(irreducible(value, budget) for value in set(values)),
                "invalid_certificate", "A claimed factor is reducible.")
    elif family == "assignment-dual-v1":
        fields(problem, ["family", "size", "cost_bits", "costs"])
        fields(answer, ["permutation", "u", "v"])
        size = decimal(problem["size"], 2, 128)
        bits = decimal(problem["cost_bits"], 4, 30)
        require(isinstance(problem["costs"], list) and len(problem["costs"]) == size,
                "invalid_problem", "Cost matrix has the wrong height.")
        for name in ("permutation", "u", "v"):
            require(isinstance(answer[name], list) and len(answer[name]) == size,
                    "invalid_certificate", "Certificate vector has the wrong size.")
        perm = [decimal(v, 0, size - 1) for v in answer["permutation"]]
        require(len(set(perm)) == size, "invalid_certificate", "Matching is not a permutation.")
        bound = 2 * size * (1 << bits)
        u = [decimal(v, -bound, bound, signed=True) for v in answer["u"]]
        v = [decimal(v, -bound, bound, signed=True) for v in answer["v"]]
        for i, row in enumerate(problem["costs"]):
            budget.check()
            require(isinstance(row, list) and len(row) == size and
                    all(isinstance(c, str) and 1 <= len(c) <= 10 for c in row),
                    "invalid_problem", "Cost matrix has invalid dimensions or integer lengths.")
            try:
                costs = [int(c) for c in row]
            except ValueError as exc:
                raise Rejection("invalid_problem", "Cost matrix contains a non-integer.") from exc
            require(all(0 <= c < (1 << bits) and str(c) == raw for c, raw in zip(costs, row)),
                    "invalid_problem", "Cost matrix contains an out-of-range or noncanonical integer.")
            require(all(u[i] + v[j] <= cost for j, cost in enumerate(costs)),
                    "invalid_certificate", "Dual feasibility inequality failed.")
            require(u[i] + v[perm[i]] == costs[perm[i]],
                    "invalid_certificate", "Matched edge is not tight.")
    else:
        raise Rejection("unknown_family", "Unknown mathematical family.")
    return {"family": family, "valid": True}


def verify_all(problems, answers, seconds=2.0):
    require(isinstance(answers, list) and len(answers) == len(problems),
            "answer_count", "Every sampled problem needs exactly one certificate.")
    budget = Budget(seconds)
    return [verify(problem, answer, budget) for problem, answer in zip(problems, answers)]
