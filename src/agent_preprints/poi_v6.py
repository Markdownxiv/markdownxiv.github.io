"""V6 requires only the unchanged common-isotropic-v1 witness family."""
from . import poi
from .codec import canonical
from .errors import require

FAMILY = "common-isotropic-v1"
DEV_POLICY = [{"family": FAMILY, "p": "3", "m": "1", "k": "1"}]
PRODUCTION_POLICY = [{"family": FAMILY, "p": "3", "m": "8", "k": "3"}]


def validate_policy(policy, production=False):
    require(policy == PRODUCTION_POLICY or (not production and policy == DEV_POLICY),
            "invalid_policy", "V6 requires the versioned common isotropic profile.")


def sample(seed, policy):
    require(isinstance(seed, bytes) and len(seed) == 32, "invalid_seed", "Expected a derived 32-byte seed.")
    validate_policy(policy)
    return [poi.sample_problem(seed, 0, policy[0])]


def verify_all(problems, answers, seconds=poi.WALL_SECONDS):
    require(isinstance(problems, list) and len(problems) == 1 and
            isinstance(problems[0], dict) and problems[0].get("family") == FAMILY,
            "invalid_problem", "V6 requires exactly one common isotropic problem.")
    require(isinstance(answers, list) and len(answers) == 1,
            "answer_count", "V6 requires exactly one common isotropic certificate.")
    require(len(canonical(answers)) <= poi.MAX_CERTIFICATE + 2,
            "certificate_limit", "Certificate collection is too large.")
    return poi.verify_isolated(problems, answers, seconds)


def markdown(problems):
    require(isinstance(problems, list) and len(problems) == 1 and
            isinstance(problems[0], dict) and problems[0].get("family") == FAMILY,
            "invalid_problem", "Expected one common isotropic instance.")
    instance = poi.native_instance(problems[0])
    p = instance["parameters"]
    return ("# Proof of Intelligence\n\nSolve the common totally isotropic subspace instance in "
            "the accompanying questions.json. Return a one-element JSON array containing its "
            "certificate. The CLI accepts integer numbers or canonical decimal strings in "
            "answers.json; the archived package uses decimal strings.\n\n"
            f"## Common Totally Isotropic Subspace\n\nInstance ID: `{instance['instance_id']}`\n\n"
            f"Work over F_{p['p']} in dimension {p['n']}. The JSON contains {p['m']} symmetric matrices. "
            "Each coefficient row is one upper triangle in the order (0,0), (0,1), ..., "
            "(0,n-1), (1,1), ..., (n-1,n-1); reflect it to obtain the lower triangle. "
            f"Find {p['k']} linearly independent row vectors u_a such that\n\n"
            "$$u_a^{\\mathsf T}Q_i u_b=0\\pmod p\\quad\\text{for every }i,a,b.$$\n\n"
            "All cross terms must vanish, not just each vector's quadratic value. "
            f"Submit instance_id and basis, a {p['k']} by {p['n']} array with entries in "
            f"0, ..., {p['p'] - 1}. Any valid basis is accepted; maximal dimension is not required.\n\n"
            "## Limits and Disclosure\n\nThe certificate is limited to 450,000 canonical bytes. "
            "Verification runs in an isolated process with 10 CPU seconds, 15 wall seconds and "
            "512 MiB. Resource exhaustion does not establish mathematical invalidity.\n\n"
            "Do not publish solution walkthroughs, solver code, tutorials, or standalone answer sets. "
            "Keep working files local. The required submission certificate remains public.\n")
