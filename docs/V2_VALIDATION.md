# V2 implementation and validation record

This record distinguishes local checks, real GitHub operations and untested limits.
The original v1 deployment evidence is in VALIDATION.md. No v1 archived body,
metadata, proof, calibration or epoch has been rewritten for this upgrade.

## Local verification (2026-09-17)

The actual v1 and v2 CLI demos completed challenge generation, preparation, local
low-difficulty PoW, PoW-derived questions, real certificates, verification, archive
and static build. The v2 demo also includes a figure and a second immutable version.
Development receipts correctly remain publication-pending.

The regression suite covers original math/protocol/production vectors plus v2
metadata bindings, eight taxonomy groups/aliases, strict envelopes, image tampering,
unsafe paths/symlinks, invalid/animated/oversized images, exact 2 MiB Markdown,
owner checks, stale parents, metadata-only revisions, rollback, idempotent replay,
concurrent ID allocation, interrupted journal recovery and legacy migration.
Local bare-Git tests include competing writers and a stale revision rejected after
a non-fast-forward retry. Binary artifact tampering/path traversal/symlinks and
stale publication rollback are also tested. The final executed count is recorded
below after the deployment validation run. The full local command
`python -m unittest discover -s tests -v` passed **95 tests in 61.120 seconds**.

Browser checks used local Chromium, desktop 1280×1000 and mobile 390×844: homepage,
short-ID search, category search, version figure load, no mobile horizontal overflow,
and no JavaScript errors passed. This was an actual browser run, not a mock screenshot.

Actionlint 1.7.12 checked the workflows with only its known unsupported
`queue` concurrency-key diagnostic excluded. GitHub already accepted this key in
the existing live workflows. New workflow behavior still requires the live runs
recorded below.

## Actual local capacity measurement

[Raw measurement](measurements/v2-local-resources.json), WSL2/Python 3.12.3:

| Operation | Measured time |
| --- | ---: |
| Verify 2 MiB Markdown + five 2 MiB PNGs | 3.076 s |
| Archive that 12 MiB version | 3.263 s |
| Build its static site | 3.042 s |
| Decode a separate 20 million pixel PNG | 0.632 s |

The generated site contained 23,403,791 bytes; the readable Issue was 2,558 bytes
because files were referenced by a pinned source. Reported process/child peak RSS
was 135,772 KiB. This is synthetic local data with valid ancillary PNG padding,
not a GitHub download/runner measurement or a PoW calibration. The original
production target remains tied to its separately published measured calibration.

## Live verification

Pending the authorized upgrade deployment and fresh production-proof revision.
This section will be updated only after the actual Actions results and HTTP/CLI
readback are observed.

## Remaining external checks

No non-collaborator GitHub credential is available in this session, so the complete
source-upload/submission path from an account without archive write access has not
been exercised live. Unit tests and the public Git tree/blob API path enforce the
same source restrictions without requiring participant write access.

No live GitHub Issue maximum-length boundary test, maximum 12 MiB network upload,
20-image network stress test, or reaction/comment edit/deletion experiment has been
performed. Exact service-side Issue character/byte limits are not claimed; this
project enforces its own 60,000-byte envelope. Social edits/deletions/failures are
covered with API fixtures. Real Pages quota exhaustion and large-archive rotation
latency remain operational limits, not demonstrated throughput claims.
