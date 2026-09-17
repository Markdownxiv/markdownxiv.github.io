# V3 local implementation and validation

Recorded on 2026-09-18 in Asia/Shanghai (2026-09-17 UTC), using Python 3.12.12 in an
isolated temporary virtual environment. This record describes actual local checks;
it does not claim that the reviewed code has been pushed or deployed.

## Completed checks

- `python -m unittest discover -s tests -v`: **123 tests passed**, 41.536 seconds.
  Original v1/v2 encoding, math and production fixtures remain valid. New coverage
  includes unbound author homepages, actual 1,000,000-byte boundaries, sealed PR
  commits, draft/ready timing, unsafe/unlisted files, proof-before-body fetching,
  forged validation caches, bounded PR recovery, participant fork/branch submission,
  ambiguous creation, owner submission, publication/close recovery, atomic bare-Git
  PR archive transactions and static 50/51-item category pages.
- All three actual offline CLI demos completed in separate temporary roots. The v3
  demo includes a static figure and an immutable second version, with archived but
  unpublished receipts. No development fixture was inserted into the production
  registry, and no remote PR or Issue was created by a demo.
- JSON Schemas passed schema validation. Actual v3 demo packages, epochs and public
  receipts validated using the registered schema URNs. Workflow YAML parsed and
  checkout references were checked to select trusted default-branch/archive commits.
- The production test archive is empty. The retained calibration/taxonomy remain
  present. A newly generated v3 production epoch is registered with no publication
  timestamp; direct admission checks correctly reject it as `epoch_unpublished`.
- `git diff --check` passed.

## Browser checks

Actual Chromium/Playwright checks covered 1440x1000, 390x844 and 1920x1080 viewports
using a separate 51-work development fixture. The homepage contained all 149 subject
links; subject filtering, category navigation, 50-plus-1 static pagination, author
links, abs/Markdown separation, full-index abstract matching, search pagination and
the header search form passed. No horizontal overflow or JavaScript errors occurred.

The illustrated development demo's actual PNG loaded with natural dimensions
640x240. A separate direct browser navigation confirmed a raw `.md` response with
`text/markdown` and exactly the original plain Markdown, without page chrome.
Desktop/mobile screenshots were inspected. The initial browser pass found that
the former `form-action 'none'` CSP blocked the new search form; it was changed to
`form-action 'self'` and the browser checks then passed.

Screenshots and browser data are temporary QA artifacts, not production manuscripts.

## Remaining deployment checks

The local verification did not change the remote Issues setting, publish Pages,
create public test PRs or run the new workflow on an actual non-collaborator's fork.
Those results must not be inferred from API fixtures or local Git remotes. Follow
[PR_DEPLOYMENT.md](PR_DEPLOYMENT.md) for the coordinated publication and Issues
shutdown after the PR replacement is ready. Retain the empty production archive
unless an actual submission or a clearly identified public test is authorized.
