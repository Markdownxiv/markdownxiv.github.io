"""PoW-bound WitnessBench instances and isolated exact certificate verification."""
import hashlib
import multiprocessing
import re
import signal

from . import witnessbench
from .codec import canonical, decimal, fields, hexhash
from .errors import Rejection, require

DEV_POLICY = [{"family": "picard-fuchs-v1", "genus": "1", "t_degree": "1", "bound": "1"},
              {"family": "common-isotropic-v1", "p": "3", "m": "1", "k": "1"}]
PRODUCTION_POLICY = [{"family": "picard-fuchs-v1", "genus": "2", "t_degree": "2", "bound": "3"},
                     {"family": "common-isotropic-v1", "p": "3", "m": "8", "k": "3"}]
MAX_CERTIFICATE = 450_000
MAX_TERMS = 6000
MAX_COEFFICIENT_BITS = 12000
CPU_SECONDS = 10
WALL_SECONDS = 15
MEMORY_BYTES = 512 * 1024 * 1024
FAMILIES = {"picard-fuchs-v1": "picard_fuchs", "common-isotropic-v1": "isotropic"}


def validate_policy(policy, production=False):
    require(policy == PRODUCTION_POLICY or (not production and policy == DEV_POLICY),
            "invalid_policy", "Use the versioned WitnessBench profile with both mathematical families.")


def encode(value):
    if type(value) is int:
        return str(value)
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    return value


def _integer(value):
    require(isinstance(value, str) and len(value) <= 3614 and
            re.fullmatch(r"0|-?[1-9][0-9]*", value, flags=re.ASCII),
            "invalid_certificate", "Witness integers must be canonical decimal strings.")
    number = int(value)
    require(number.bit_length() <= MAX_COEFFICIENT_BITS, "certificate_limit", "Witness integer exceeds 12000 bits.")
    return number


def _numbers(value):
    if isinstance(value, list):
        return [_numbers(item) for item in value]
    return _integer(value)


def native_instance(problem):
    fields(problem, ["family", "instance"])
    require(problem["family"] in FAMILIES, "unknown_family", "Unsupported WitnessBench family version.")
    instance = problem["instance"]
    fields(instance, ["version", "family", "parameters", "coefficients", "instance_id"])
    require(instance["family"] == FAMILIES[problem["family"]], "unknown_family", "WitnessBench family mismatch.")
    hexhash(instance["instance_id"])
    fields(instance["parameters"], ["genus", "t_degree", "bound"] if instance["family"] == "picard_fuchs" else ["p", "m", "k", "n"])
    native = {**instance, "parameters": {key: decimal(value, 1, 100) for key, value in instance["parameters"].items()},
              "coefficients": _numbers(instance["coefficients"])}
    try:
        return witnessbench.validate_instance(native)
    except (ValueError, TypeError, KeyError) as exc:
        raise Rejection("invalid_problem", "Invalid WitnessBench instance or digest.") from exc


def sample(seed, policy):
    require(isinstance(seed, bytes) and len(seed) == 32, "invalid_seed", "Expected a derived 32-byte seed.")
    validate_policy(policy)
    problems = []
    for index, params in enumerate(policy):
        kwargs = {key: int(value) for key, value in params.items() if key != "family"}
        family = FAMILIES[params["family"]]
        if family == "picard_fuchs":
            base, count = 2 * kwargs["bound"] + 1, (2 * kwargs["genus"] + 1) * kwargs["t_degree"]
        else:
            n = (kwargs["m"] + 1) * kwargs["k"] + kwargs["m"]
            base, count = kwargs["p"], kwargs["m"] * n * (n + 1) // 2
        prefix = b"markdownxiv-witnessbench-sample-v1\0" + seed + index.to_bytes(4, "big")
        digits, counter = [], 0
        while len(digits) < count:
            block = hashlib.sha256(prefix + counter.to_bytes(8, "big")).digest()
            counter += 1
            digits.extend(byte % base for byte in block if byte < 256 - 256 % base)
        coefficient_index = 0
        for digit in reversed(digits[:count]):
            coefficient_index = coefficient_index * base + digit
        instance = witnessbench.sample(family, index=coefficient_index, **kwargs)
        problems.append({"family": params["family"], "instance": encode(instance)})
    return problems


def markdown(problems):
    text = ["# Proof of Intelligence\n\nSolve both instances in the accompanying questions.json. "
            "Return a JSON array containing the two certificates in the same order. "
            "The CLI accepts integer numbers or canonical decimal strings in answers.json; "
            "the archived package encodes all integers as decimal strings.\n"]
    for problem in problems:
        instance = native_instance(problem)
        p = instance["parameters"]
        if problem["family"] == "picard-fuchs-v1":
            text.append(f"## Picard-Fuchs Certificate\n\nInstance ID: `{instance['instance_id']}`\n\n"
                        f"Let g = {p['genus']}, h = {p['t_degree']}, and d = {2 * p['genus'] + 1}. Define\n\n"
                        "$$Q(t,x)=x^d-1+\\sum_{i=1}^h t^i\\sum_{j=0}^{d-1}c_{ij}x^j.$$\n\n"
                        "The coefficient rows in JSON start at t^1 and columns start at x^0. "
                        "Find integer polynomials p_0(t), ..., p_r(t) and A(t,x), with "
                        "1 <= r <= 2g and p_r nonzero, satisfying the exact identity\n\n"
                        "$$\\sum_{j=0}^r p_j(t)\\partial_t^j Q(t,x)^{-1/2}"
                        "=\\partial_x\\left(\\frac{A(t,x)}{Q(t,x)^{r-1/2}}\\right).$$\n\n"
                        "Each partial derivative holds the other variable fixed. The identity is in "
                        "Q(t,x)[y]/(y^2-Q), with Q^(-1/2) = 1/y. Minimal order is not required. "
                        "Submit instance_id, operator, and certificate. operator[j] lists "
                        "[t_degree, nonzero_coefficient] terms of p_j; certificate lists "
                        "[t_degree, x_degree, nonzero_coefficient] terms of A. Empty lists denote zero. "
                        "No duplicate exponents or zero-coefficient terms.\n")
        else:
            text.append(f"## Common Totally Isotropic Subspace\n\nInstance ID: `{instance['instance_id']}`\n\n"
                        f"Work over F_{p['p']} in dimension {p['n']}. The JSON contains {p['m']} symmetric matrices. "
                        "Each coefficient row is one upper triangle in the order (0,0), (0,1), ..., "
                        "(0,n-1), (1,1), ..., (n-1,n-1); reflect it to obtain the lower triangle. "
                        f"Find {p['k']} linearly independent row vectors u_a such that\n\n"
                        "$$u_a^{\\mathsf T}Q_i u_b=0\\pmod p\\quad\\text{for every }i,a,b.$$\n\n"
                        "All cross terms must vanish, not just each vector's quadratic value. "
                        f"Submit instance_id and basis, a {p['k']} by {p['n']} array with entries in "
                        f"0, ..., {p['p'] - 1}. Any valid basis is accepted; maximal dimension is not required.\n")
    text.append("## Limits and Disclosure\n\nEach certificate is limited to 450,000 canonical bytes. "
                "The polynomial certificate and operator together have at most 6,000 terms, exponents "
                "at most 1,000, and coefficients at most 12,000 bits. Verification runs in an isolated "
                "process with 10 CPU seconds, 15 wall seconds, and 512 MiB. A resource-limit rejection "
                "does not establish mathematical invalidity.\n\n"
                "Do not publish solution walkthroughs, solver code, tutorials, or standalone answer sets. "
                "Keep working files local. The required submission certificates remain public.\n")
    return "\n".join(text)


def native_answer(problem, answer):
    require(len(canonical(answer)) <= MAX_CERTIFICATE, "certificate_limit", "Witness certificate exceeds 450000 bytes.")
    pf = problem["family"] == "picard-fuchs-v1"
    fields(answer, ["instance_id", "operator", "certificate"] if pf else ["instance_id", "basis"])
    require(hexhash(answer["instance_id"]) == problem["instance"]["instance_id"],
            "instance_mismatch", "Certificate belongs to another mathematical instance.")
    if pf:
        require(isinstance(answer["operator"], list) and 2 <= len(answer["operator"]) <= 5 and
                all(isinstance(poly, list) for poly in answer["operator"]) and isinstance(answer["certificate"], list),
                "invalid_certificate", "Expected a bounded polynomial operator and certificate.")
        require(sum(map(len, answer["operator"])) + len(answer["certificate"]) <= MAX_TERMS,
                "certificate_limit", "Certificate exceeds 6000 total polynomial terms.")
    return {key: value if key == "instance_id" else _numbers(value) for key, value in answer.items()}


def _verify_worker(connection, problems, answers):
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
        results = []
        for problem, answer in zip(problems, answers):
            instance = native_instance(problem)
            result = witnessbench.verify(instance, native_answer(problem, answer))
            if not result["accepted"]:
                code = "verification_resource_limit" if result["status"] == "resource_limit" else "invalid_certificate"
                raise Rejection(code, "WitnessBench certificate check: " + result["status"] + ".")
            results.append({"family": problem["family"], "valid": True})
        connection.send({"results": results})
    except Rejection as exc:
        connection.send({"error": exc.as_dict()})
    except MemoryError:
        connection.send({"error": {"error_code": "verification_resource_limit", "message": "Certificate memory budget exceeded.", "retryable": False}})
    except Exception:
        connection.send({"error": {"error_code": "verification_unavailable", "message": "Isolated verifier failed.", "retryable": True}})
    finally:
        connection.close()


def verify_all(problems, answers, seconds=WALL_SECONDS):
    require(isinstance(problems, list) and len(problems) == 2 and
            [p.get("family") for p in problems if isinstance(p, dict)] == list(FAMILIES),
            "invalid_problem", "Both versioned WitnessBench problems are required in order.")
    require(isinstance(answers, list) and len(answers) == 2, "answer_count", "Both WitnessBench certificates are required.")
    require(len(canonical(answers)) <= 2 * MAX_CERTIFICATE + 3, "certificate_limit", "Certificate collection is too large.")
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_verify_worker, args=(child, problems, answers))
    try:
        process.start()
        child.close()
        if not parent.poll(seconds):
            raise Rejection("verification_resource_limit", "Mathematical verification exceeded its wall-time limit.")
        try:
            response = parent.recv()
        except EOFError as exc:
            process.join(timeout=1)
            limited = process.exitcode in (-signal.SIGKILL, -signal.SIGXCPU)
            raise Rejection("verification_resource_limit" if limited else "verification_unavailable",
                            "Isolated verifier exited without a result.", not limited) from exc
        if "error" in response:
            error = response["error"]
            raise Rejection(error["error_code"], error["message"], error.get("retryable", False))
        return response["results"]
    finally:
        child.close()
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join()
            process.close()
        parent.close()
