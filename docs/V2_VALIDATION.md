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
stale publication rollback are also tested. The final local command
`python -m unittest discover -s tests -v` passed **96 tests in 75.908 seconds**,
including the additional malformed-JSON-type regression discovered during final review.

Browser checks used local Chromium, desktop 1280×1000 and mobile 390×844: homepage,
short-ID search, category search, version figure load, no mobile horizontal overflow,
and no JavaScript errors passed. This was an actual browser run, not a mock screenshot.

Actionlint 1.7.12 checked the workflows with only its known unsupported
`queue` concurrency-key diagnostic excluded. GitHub already accepted this key in
the existing live workflows. The workflow behavior has also passed the live runs
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

The authorized upgrade commit is `bf5277263b80603febb08c9077bb550f42540fa9`.
[GitHub CI](https://github.com/kzoacn/Markdownxiv/actions/runs/35215603529)
passed 95 tests in 11.974 seconds on its runner, both offline CLI demos and the
production-root site build. [The upgrade deployment](https://github.com/kzoacn/Markdownxiv/actions/runs/35215635062)
completed validation, archive, build, deploy and receipt jobs successfully.
The v2 epoch was published at `2026-09-17T11:26:28Z`, with the original production
calibration and target retained. The production CLI successfully downloaded and
validated that epoch, taxonomy and work registry from actual GitHub Pages.

An actual Chromium run against Pages verified short-ID search, legacy short routes,
the social sync timestamp, all 149 category rows, category search and no JavaScript
errors. Both archived v1 production proofs were independently reverified using their
original receipt times. Their original body/metadata/proof bytes match the pre-upgrade
Git objects. Existing bot receipts gained short human-facing aliases while retaining
their original v1 machine JSON semantics and comment IDs.

The English, illustrated revision was submitted exactly once as
[Issue #3](https://github.com/kzoacn/Markdownxiv/issues/3). Its source is pinned to the
upgrade commit; real GitHub tree/blob reads confirmed the exact manuscript and figure
bytes before submission. Local production mining used one thread and took
69.354162593 seconds by `perf_counter_ns`, including CLI startup. This is a random
single success, not a replacement calibration or a guaranteed duration. Its nonce is
`000000000fada4a3`; PoW hash
`00000001e52857ee18e66b1561c7b4ff477b82ffde2daaaa492f75870df6f7a1`.
Only then were the actual degree-192 factorization and 96×96/30-bit assignment
sampled, solved with the explicitly invoked local public reference algorithms and
verified with production policy. The complete readable Issue is 6142 UTF-8 bytes.
[The real admission workflow](https://github.com/kzoacn/Markdownxiv/actions/runs/35216197658)
completed all five jobs successfully. The published receipt identifies
[mx:2609.00002v2](https://kzoacn.github.io/Markdownxiv/p/2609.00002/v2/),
with the original Issue #2 retained as its discussion root.
HTTP readback confirmed exact Markdown/image SHA-256 values, the old v1 short and
full-hash URLs, two work entries and three immutable versions. Live Chromium checks
confirmed the PNG's natural dimensions, MathML, actual declared AI, both history
entries and a mobile layout without horizontal overflow or JavaScript errors.

A final malformed-type fix turns invalid media/category values and non-object
envelope payloads into structured rejections rather than uncaught exceptions.
The accepted protocol and existing proof bytes are unchanged.

The real admission workflow was rerun as attempt 2. Validation, archive and receipt
jobs succeeded; build and deployment were correctly skipped because the version was
already published. After fetching the branch again, every registered work, paper
and image file matched its pre-rerun SHA-256: still two works and three versions.
All three archived production proofs were independently reverified locally.

CI also includes a read-only integration probe against a pinned Markdown blob in
`github/markup`, outside this repository, using the same restricted Actions token
permissions as validation. It does not upload, execute, archive or post that source.
[The final hardening CI run](https://github.com/kzoacn/Markdownxiv/actions/runs/35217633728)
succeeded, including the 96-test suite, both demos and that authenticated cross-repository
public-source read. The offline v2 demo was also rerun locally: sealed requests were
reused, one work/two versions remained, and the local manuscript bytes matched its
latest archived version.

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
