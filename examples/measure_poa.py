"""Explicit local performance experiment, never run by admission workflows or CI."""
import argparse
import platform
import time

from agent_preprints import poa
from agent_preprints.codec import sha, utcnow, write_json
from agent_preprints.pow import cpu_name
from reference_solvers import solve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["development", "production"], default="development")
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if not 1 <= args.samples <= 100:
        parser.error("samples must be 1–100")
    policy = poa.PRODUCTION_POLICY if args.profile == "production" else poa.DEV_POLICY
    timings = []
    for index in range(args.samples):
        seed = bytes.fromhex(sha(b"explicit-local-poa-cost-experiment-v1\0" + index.to_bytes(4, "big")))
        start = time.perf_counter_ns()
        problems = poa.sample(seed, policy)
        generated = time.perf_counter_ns()
        for problem in problems:
            solved_at = time.perf_counter_ns()
            answer = solve([problem])[0]
            verified_at = time.perf_counter_ns()
            poa.verify(problem, answer)
            done = time.perf_counter_ns()
            timings.append({"sample": str(index), "family": problem["family"], "seed": seed.hex(),
                            "sample_both_ns": str(generated - start), "solve_ns": str(verified_at - solved_at),
                            "verify_ns": str(done - verified_at)})
    result = {"measured_at": utcnow(), "cpu": cpu_name(), "python": platform.python_version(),
              "platform": platform.platform(), "threads": "1", "profile": args.profile,
              "policy": policy, "conditions": "Task environment, uncontrolled background load; no affinity; warm process. Algorithm costs only, no Agent discrimination experiment.",
              "timings": timings}
    write_json(args.out, result)
    print("Measured generation, reference solving and independent verification. Results: " + args.out)


if __name__ == "__main__":
    main()
