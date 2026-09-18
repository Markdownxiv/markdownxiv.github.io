# V5 WitnessBench validation

Date: 2026-09-18. V5 introduces the supplied public WitnessBench verifier through
explicit protocol and family dispatch. The original verifier's manifest hash was
checked, and its source is unchanged. The mathematical families are Picard-Fuchs
g=2, h=2, B=3 and common isotropic p=3, m=8, k=3, n=35.

## Local verification

The unit suite covers valid fixed certificates at development and full production
mathematical sizes, deterministic coefficient sampling, original instance digests,
wrong-instance replay, zero operators, false polynomial identities, duplicate terms,
zero rank, missing isotropic cross terms, integer formats, certificate budgets,
wall-time termination and worker cleanup. It also covers native answer conversion,
legacy byte-limit enforcement, PoW-before-manuscript reads, sealed PR admission,
archive generation, the 8 MB material boundary, measured calibration, unpublished
epoch rejection, and refusal to use an old gate after production selects v5.

`python examples/local_demo_v5.py --out <empty directory>` verifies and archives a
fixed development submission without a solver or network. Development fixtures
remain under tests/fixtures, outside the production epoch registry.

Both original supplied examples were solved locally and accepted by the unchanged
verifier. The local verification times were approximately 0.010 seconds for the
Picard-Fuchs example and 0.003 seconds for the isotropic example. Solver working
files and standalone answers were kept outside the repository and are not shipped.

A separate local simulation used the existing measured 30-second expected-work
calibration and a newly generated v5 production-profile epoch. Its publication flag
was simulated locally; no PR or actual public paper was created. One nonce search
took 81.390 seconds, consistent with a probabilistic target rather than a fixed wait.
Both certificates passed the bounded verifier in 0.321 seconds including process
startup. The package was 46,241 bytes and the archived proof 67,413 bytes.

These measurements are individual local observations, not performance guarantees,
an independent security audit, or evidence of separation between AI model levels.
The runtime verifier depends only on the Python standard library. Local validation
tools are not runtime or CI dependencies.

## Deployment contract

The production configuration selects v5 and retains the measured 30-second PoW
calibration. Maintenance generates a new v5 epoch; it gains admission authority only
after successful Pages deployment is recorded. New PRs then require that protocol.
Existing manuscripts and proofs retain their original bytes and version semantics.
The deployment still uses the shared workflow lock, fresh Git transactions and
stale-artifact guard. Required checks are CI, all five offline demos, Pages job
completion, published v5 policy inspection and a live CLI challenge download.
