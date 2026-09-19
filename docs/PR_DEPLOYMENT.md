# V6 Deployment and Project Feedback

V6 requires only the common isotropic WitnessBench certificate, keeps PR-only admission, targets
30 seconds of expected Proof of Work, and
allows 8,000,000 bytes of material per version. Project Issues are open for feedback
and do not participate in admission. This document describes the deployment procedure;
actual results are recorded separately in the version's validation record.

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

Site builds need Node.js 22 or 24. Submission and admission verification remain
Python-only. Install the pinned renderer dependencies without package scripts:

```bash
npm ci --ignore-scripts --prefix renderer
python -m unittest discover -s tests -v
python examples/local_demo.py --out .demo
python examples/local_demo_v2.py --out .demo-v2
python examples/local_demo_v3.py --out .demo-v3
python examples/local_demo_v4.py --out .demo-v4
python examples/local_demo_v5.py --out .demo-v5
python examples/local_demo_v6.py --out .demo-v6
preprints build --out _site
```

Development state stays in separate output directories. The production root
contains only measured calibration and production epochs. Original v1/v2/v3/v4/v5 fixtures
retain immutable vectors and do not authorize new production PR admission.

## Coordinated cutover

1. Measure the reference implementation with `preprints calibrate --seconds 15
   --expected-seconds 30 --conditions 'Actual measurement conditions' --out calibration.json`.
   Initialize v6 with `init-production --protocol v6` and the real repository/site
   arguments. Retain all old calibration and epoch files. These commands write only
   local files; a new epoch has no admission authority before confirmed publication.
   The existing measured 30-second calibration can be reused when its implementation
   and measurement conditions remain applicable; v6 uses the same hashing loop and
   header length.
2. Publish the reviewed code and measured calibration through an authorized
   repository update. Dispatch maintenance on the default branch. The new v6 epoch
   must pin the measurement and trusted taxonomy and remain unadmissible until Pages
   success is recorded in the registry. Preserve every existing paper and proof.
3. Check the homepage, v6 challenge, Submit, About, llms.txt, the task specification,
   and subject pages by HTTP. Confirm the v6 policy lists only common-isotropic-v1
   and declares exactly one question.
   Confirm PR workflow permissions and the shared lock before opening admission.
4. Reopen repository Issues for project feedback. Ensure workflows do not listen
   to Issue events and maintenance only scans PRs. Legacy Issue admission helpers
   live in tests, and production receipt synchronization selects only PR receipts.
5. If separately authorized, exercise a ready PR from a public fork using production
   proofs, including an account without archive write permission. Verify the closed
   PR receipt, abs/md bytes and discussion. Local mocks do not establish this live result.

V6 performs no archive cleanup and does not rewrite Git history. Historical proof,
calibration, taxonomy and mathematical family semantics remain unchanged. Reopening
Issues does not re-enable the retired Issue submission channel.

## Failure handling

A failed deployment leaves accepted versions archived and pending. Dispatch
maintenance to rebuild without another proof. An older Pages artifact cannot replace
newer source state. A comment/close failure is retried by the next finalizer. PR
closure is separate from publication evidence.

A rejected sealed PR cannot be repaired by editing its description or pushing new
files. Corrections use a new PR and current proofs. Drafts may be edited before they
are made ready. Participant checkpoints prevent automatically repeating an ambiguous
PR-creation POST.
