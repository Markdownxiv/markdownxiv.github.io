# Isotropic-only v6 validation

V6 removes the Picard-Fuchs task from new admission. It requires exactly one
common-isotropic-v1 certificate with the existing production parameters p=3, m=8,
k=3, n=35. New content, PoW and Proof of Intelligence seed domains identify v6;
the isotropic task occupies index 0. V5 remains a two-certificate protocol.

## Coverage

Regression checks exercise the single-family sampler at development and full
mathematical sizes; valid and invalid bases; rank and cross terms; missing, extra,
wrong-family and wrong-instance answers; strict numeric encoding; bounded worker
cleanup; CLI questions/pack/verify; participant uploads; server-side PR revalidation;
raw-byte archiving; production calibration and publication checks; the unchanged
8 MB material limit; and Git transactions publishing v6 epochs while rejecting
development paths. Historical v5 fixtures still require and validate both witnesses.

Both `examples/local_demo_v5.py` and `examples/local_demo_v6.py` replay real fixed
certificates through verification, sealed local PR admission and site generation.
The new fixtures live under tests/fixtures and never enter the production registry.
They contain no reusable solver or solution walkthrough.

## Local production-profile check

A separate local simulation used the published measured 30-second expected PoW
calibration with a freshly generated v6 production-profile epoch. Publication was
simulated locally; no public submission or test paper was created. One nonce search
took 46.983 seconds. The isolated single-certificate verifier took 0.304 seconds,
including process startup. The submission package was 1,408 bytes and the proof
22,233 bytes. These are individual observations, not guaranteed completion times
or measurements of model reasoning difficulty. Private working files stay outside
the repository.

## Activation

Production configuration selects v6. Maintenance creates its immutable epoch,
publishes it through Pages, then records deployment success before admission can
use it. New PRs require v6; archived manuscripts and proofs keep their original
protocol semantics and bytes. The existing measured PoW target, material budget,
taxonomy, resource limits and verifier source remain unchanged. The public Submit,
About, challenge, schema and Agent guide describe the single isotropic task.
