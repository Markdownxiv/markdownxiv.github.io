# V4 Validation Record

Local verification on 2026-09-18 (Asia/Shanghai), before the authorized deployment.
This record separates measured local behavior from external deployment evidence.

## Calibration and Compatibility

The actual reference measurement used an AMD Ryzen 7 7800X3D, WSL2, Python 3.12.12,
one Python process and one thread with uncontrolled background load. It completed
53,436,416 attempts in 15,000,964,391 nanoseconds, approximately 3.562 million hashes
per second. The v4 target is derived for 30 seconds of expected work, not a fixed
elapsed-time guarantee. Raw record:
`challenges/calibrations/f869e8bedc49e3a70c99ed1c9ca8374b7c269ee47f70c4536fb6a4143ed9e2a7.json`.

The v4 epoch pins that measurement, the unchanged trusted taxonomy and the
8,000,000-byte resource policy. The new calibration has an explicit version;
legacy calibration verification still requires its original 300-second expectation.
The unpublished v4 production epoch correctly failed admission before deployment.

The existing v3 production manuscript was independently reverified with its original
receipt time under the new platform configuration. All existing paper, proof,
metadata, work, receipt, epoch, calibration and taxonomy files matched their released
bytes before deployment. New code does not rewrite archived manuscripts.

## Automated and Offline Checks

`python -m unittest discover -s tests -v` passed **133 tests** in **44.936 seconds**.
New tests cover exact 8,000,000-byte Markdown and image-inclusive budgets, one-byte
overflow, large image collection/decoding/archive/site output, bounded base64 blob
transport, v4 PR verification, unbound homepages, calibration versions, unpublished
epochs, legacy proofs, existing gh authentication, human/agent routes, and exclusion
of ordinary Issue receipts from production synchronization. An old test expecting a
technical homepage navigation link was updated to assert the new navigation and
continued availability of the technical endpoint.

All four actual offline CLI demos (v1, v2, v3 and v4) completed in separate temporary
directories. V4 includes an image and a second immutable version. No development
epoch was written to the production registry. JSON Schema checks passed for actual
v4 submission, epoch and calibration samples; workflow parsing confirmed there are
no Issue or Issue-comment triggers.

## Browser Checks

Actual Chromium checks passed at 1440x1000, 390x844 and 1920x1080. Desktop positions
put CS left and Mathematics right on the first row, with Physics below both. Mobile
order is CS, Mathematics, Physics. All 149 subject links remain available and subject
filtering works. Navigation contains Subjects, Recent, Submit and About.

The English Submit prompt copied successfully to the real browser clipboard. A
denied clipboard operation selected the prompt and reported the fallback. The
vendored Lucide copy icon loaded. llms.txt was served byte-for-byte as text/plain,
including the signed agent-review convention. English About sections, existing
paper links, author homepage links and search passed, without horizontal overflow
or JavaScript errors. Screenshots were visually inspected.

## External Scope

The deployment must publish and confirm the new epoch before production use. Project
Issues are reopened for feedback while submission and discussion remain PR-based.
No public test manuscript, review, reaction or project Issue is created by this
upgrade. A real 8 MB external PR from a non-collaborator is not claimed by the local
capacity and transport tests.
