# PR-only deployment and cutover

The v3 implementation replaces production Issue admission with ready PR admission.
This document describes the rollout; it does not establish that remote settings,
workflows or Pages have already been changed.

## Trusted workflows

`accept.yml` uses `pull_request_target` for `opened` and `ready_for_review`, restricted
to `[preprint] ` titles, non-drafts and the default target branch. Every checkout
explicitly selects trusted archive code. Validation has contents/PR read access;
archive writing has contents write; the finalizer has contents and PR write for
receipts and closing published PRs. No job executes a contributor checkout.
Ordinary code CI runs on trusted default-branch pushes or dispatch. Third-party
Actions and Python dependencies remain pinned.

`maintain.yml` shares the workflow concurrency group, rotates the challenge, collects
at most five ready/retryable PR snapshots from at most two 100-item pages, revalidates
against fresh state, builds/deploys and synchronizes receipts. Sealed requests retain
their original head. Recovery without a seal uses current observation time. Push
conflicts rerun against a fresh worktree, never force-push.

PR conversation comments and reactions use GitHub's shared issue-comment/reaction
APIs with pull-request permission; this is not an Issue admission channel. Disabling
repository Issues does not disable PR conversations. The first submission PR remains
the discussion root across revision PRs.

## Local checks

```bash
python -m unittest discover -s tests -v
python examples/local_demo.py --out .demo
python examples/local_demo_v2.py --out .demo-v2
python examples/local_demo_v3.py --out .demo-v3
preprints build --out _site
```

Development state stays in separate output directories. The production root
contains only measured calibration and production epochs. Original v1/v2 fixtures
retain immutable vectors and do not authorize new production PR admission.

## Coordinated cutover

1. Publish the reviewed trusted implementation, owner-authorized test-archive reset
   and configuration through an explicitly authorized repository update.
2. Dispatch maintenance on the default branch. A v3 epoch uses the retained valid
   measurement and trusted taxonomy. It remains unadmissible until Pages success
   is recorded in the production registry.
3. Check the new homepage, v3 challenge, subject pages and machine endpoints by HTTP.
   Confirm PR workflow permissions and the shared lock before opening admission.
4. Disable repository Issues once the PR replacement is deployed and ready, as
   requested by the owner. Local tests and builds do not change GitHub settings.
5. Exercise a ready PR from a public fork using production proofs, including an
   account without archive write permission. Verify the closed PR receipt, abs/md
   bytes and discussion with Issues disabled. Public test submissions require explicit
   authorization; local mocks do not establish this live result.

The approved cleanup removes former test manuscripts, images, works, receipts and
publication state from the current tree. Git history is not rewritten. Calibration,
taxonomy, mathematical code and protocol vectors are retained.

## Failure handling

A failed deployment leaves accepted versions archived and pending. Dispatch
maintenance to rebuild without another proof. An older Pages artifact cannot replace
newer source state. A comment/close failure is retried by the next finalizer. PR
closure is separate from publication evidence.

A rejected sealed PR cannot be repaired by editing its description or pushing new
files. Corrections use a new PR and current proofs. Drafts may be edited before they
are made ready. Participant checkpoints prevent automatically repeating an ambiguous
PR-creation POST.
