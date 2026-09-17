# Deployment and recovery

No remote settings, permission changes, pushes, Issue submissions or Pages
deployments were performed while implementing this repository. During local
deployment preparation on 2026-09-17, a measured production calibration and an
unpublished epoch were initialized for repository ID `1374075838`. Admission
remains closed until successful Pages publication. The commands below are for a maintainer
to review and execute when they authorize publication. A local demo passing is
not evidence that GitHub permissions, branch rules or Pages deployment work.

## Local validation first

From the repository root on Linux/WSL, Python 3.11+:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements.lock
python -m pip install --no-deps --no-build-isolation -e .
python -m unittest discover -s tests -v
python examples/local_demo.py --out .demo
python -m http.server 8000 --directory .demo/_site
```

The demo needs no token and makes no network calls after dependency installation.
It uses a separate development root. For an empty production-site preview:

```bash
preprints build --out _site --base-path /
python -m http.server 8001 --directory _site
```

The real Pages build defaults to the subpath from `config/production.json`,
currently `/Markdownxiv/`. `--base-path /` is only for root-mounted local previews.
The builder uses repository docs/assets, so install this project from a checkout.
Native Windows is not a supported runtime for the POSIX locking/resource limits;
use WSL. GitHub jobs use standard `ubuntu-24.04` runners and Python 3.12.

## One-time repository settings

Use the existing public repository, or a dedicated public repository. Read its
actual identity and default branch before configuring locally:

```bash
gh api repos/kzoacn/Markdownxiv --jq '{id,full_name,private,default_branch}'
```

Settings to inspect/configure yourself:

1. The repository is **public**, with Issues and Actions enabled. No extra platform
   accounts, source-author collaborator invitations, labels or manual per-paper
   approval are required. A participant needs only their own GitHub authorization
   capable of creating an Issue in this public repository.
2. Under **Settings → Pages → Build and deployment**, choose **GitHub Actions**.
   The site URL in local config must match the actual Pages URL, including any
   project subpath. The v1 CLI downloads challenges from official `*.github.io`
   origins without redirects. Use the default Pages domain for this version;
   a custom domain that redirects the github.io URL is not supported by the CLI.
3. Allow the pinned official Actions and the job-declared token permissions.
   The default `GITHUB_TOKEN` policy may remain restricted where job overrides
   are permitted. Organization rules must actually allow the archive/finalizer
   `contents: write` and finalizer `issues: write`. There is no platform PAT.
4. The default branch must permit ordinary fast-forward commits from the
   workflow's `GITHUB_TOKEN`. Required PRs, required checks, signed-commit rules,
   locked branches or restrictive rulesets may block them. **The token is not
   assumed to bypass protection.** Choose compatible rules explicitly, or use a
   dedicated repository whose default branch supports this archive workflow.
   Do not disable existing protection merely by copying these instructions.
   Archive transactions never force push, modify rules, or automatically merge PRs.
5. The `github-pages` environment must allow this repository's **default branch**
   and have **no required reviewers or wait-for-human deployment gate**. The
   environment can enforce the branch restriction; a reviewer requirement would
   violate automatic acceptance/publication. Review existing environment rules
   before changing them. No code here changes the environment configuration.

Job permissions are explicit:

| Job | Token permissions |
| --- | --- |
| Validate/collect | contents: read, issues: read |
| Archive/rotate | contents: write, issues: read |
| Build | contents: read |
| Deploy + stale artifact guard | contents: read, pages: write, id-token: write |
| Finalize/upsert receipt | contents: write, issues: write |
| Test CI | contents: read |

Checkout uses `persist-credentials: false`. Git writes receive a temporary
HTTP authorization header via subprocess environment, never an Issue value,
shell-expanded token or committed credential file. Neither validation artifacts
nor paper files contain anything to execute in later jobs.

## Measure and initialize production locally

Pick the actual reference machine and state its conditions. The reference miner
uses **one thread** and the identical hot loop in `calibrate` and `mine`. Prefer
at least 10–30 seconds of measurement under stable load; shorter measurements
are supported but noisier. The benchmark records a real elapsed duration and count,
not a claimed five-minute mining run:

```bash
preprints calibrate --seconds 15 \
  --conditions 'Reference laptop on AC power, one thread, background workload documented by operator' \
  --out .work/production-calibration.json
```

CPU is detected where possible; use `--cpu 'exact reference model / environment'`
if autodetection is unavailable. Inspect the file and repeat if the conditions are
not representative. Copying the local development measurement is not an automatic
production decision. Maintainers attest to measurement conditions; there is no
cryptographic attestation of the hardware or benchmark honesty.

Initialize using the actual immutable repository ID, then create the first epoch:

```bash
PREPRINT_REPO_ID="$(gh api repos/kzoacn/Markdownxiv --jq '.id')"
preprints init-production --root . \
  --calibration .work/production-calibration.json \
  --repository kzoacn/Markdownxiv --repository-id "$PREPRINT_REPO_ID" \
  --site-url https://kzoacn.github.io/Markdownxiv/
preprints rotate --root .
preprints build --out _site
```

These commands only change local files. Production epochs are initially registered
with `published_at: null`; `preprints challenge` against that unpublished local
registry will correctly return `epoch_unpublished`. It becomes admissible only
after a successful Pages deployment is recorded by the workflow. Never manually
mark a real production epoch published merely to bypass this check. The published
calibration target is fixed for all clients, even much slower or faster clients.

Review the entire diff and your repository settings. Only after authorizing a
commit/push yourself, commit the implementation plus `config/`, `challenges/`
and initial archive/state directories, then push the default branch. Do not add
`.work/`, `.demo/`, `_site/`, tokens or a locally generated example paper. The
original task prompt may remain untracked; it is not needed by the application.
For a repository whose default branch is `main`, the explicit remote commands are:

```bash
# After reviewing and committing the intended files yourself:
git push origin main
gh workflow run maintain.yml --repo kzoacn/Markdownxiv --ref main
gh run list --repo kzoacn/Markdownxiv --workflow maintain.yml --limit 5
# Replace RUN_ID with the run just created:
gh run watch RUN_ID --repo kzoacn/Markdownxiv
```

Replace `main` if your actual default branch differs. `maintain` only permits the
default branch; it reads its fresh tip after acquiring the shared concurrency lock,
rotates idempotently, performs bounded recovery, builds, uploads and deploys Pages,
then records successful publication. No valid production calibration means a
published paused/empty site, not an easy submission target.

## What the two business workflows do

`accept.yml` handles **only `issues: opened`** with the fixed title prefix. Trusted
default-branch code reads the original event file. The read-only job creates a
bounded JSON cache; the archive job fetches the latest branch, independently checks
the sealed request/proofs again, and commits receipt and paper together. Rejected
requests still get sealed JSON receipts; they do not force a full Pages rebuild.
An accepted paper pending publication triggers explicit build/deploy jobs, followed
by a finalizer that also runs when build/deploy fails.

`maintain.yml` runs at **minute 17 of every UTC hour** plus `workflow_dispatch`.
It generates at most one new immutable epoch per UTC date, giving a nominal daily
rotation and exactly 48 hours of validity from generation. Hourly maintenance
also bounds the usual publication/recovery delay. The clock is not a delivery SLA:
GitHub can delay/drop scheduled runs, and inactive public repositories can have
scheduled workflows disabled. There is no hidden extension of old epochs.

Both workflows share one concurrency group with `queue: max` and no cancellation
of running work. The official maximum is **100 pending runs**; additional runs can
be canceled. Recovery therefore scans at most two 100-Issue pages and handles at
most 20 candidates per maintenance run, keeping a cyclic cursor. Closed Issues
are included; PRs and unrelated titles are ignored. At high volumes recovery can
take many runs and a legitimately on-time request may lose its original snapshot.
That fallback uses actual observation time, not the editable Issue's old date.

Git push conflicts cause at most three new worktrees/validations, no force push.
`GITHUB_TOKEN` commits are followed by build/deploy **in the same workflow** because
such pushes do not generally trigger another `push` workflow. Old build artifacts
cannot replace a newer source state: the deploy job checks a fresh source digest.

## Recovery commands and expected states

To recover a failed Pages deployment or missing receipt:

```bash
gh workflow run maintain.yml --repo kzoacn/Markdownxiv --ref main
preprints status --repository kzoacn/Markdownxiv --issue ISSUE_NUMBER --wait-seconds 600
```

Maintenance reconstructs the site from Git; it never requires resubmitting an
already archived body. A failed or skipped Pages job leaves `archived: true`,
`published: false`, and a null URL. A comment failure leaves its sync digest
unchanged, so another finalizer retries just the comment. Published flags refer
only to papers listed in a successful deployment artifact. The immutable archived
proof itself does not need to be rewritten on every deployment.

You can rerun all jobs on the original run to preserve its original opened event:

```bash
gh run rerun RUN_ID --repo kzoacn/Markdownxiv
```

Attempt-specific artifact names are passed through producer outputs, so rerunning
failed jobs does not invent a new name for an old producer artifact. If an artifact
has expired, rerun **all jobs** or use maintain. If a newer archive/config/code
state exists, the deploy guard returns `stale_deployment`; rebuild with maintain.
Successful sealed requests skip mathematical revalidation on normal reruns.
Temporary validation errors have exponential backoff and an eight-attempt automatic
limit. An original-run rerun can retry the sealed request after resolving the
underlying infrastructure problem; editing the Issue cannot replace it.

For `original_snapshot_unavailable`, the original complete body/event was not
available to recovery and the first observation fell outside the epoch window.
Ask the submitter to create a fresh Issue with current proofs; never combine an
edited body with historical `created_at`. If writes are blocked by rules or API
permissions, fix those settings explicitly first; a program unable to post comments
cannot deliver an Issue receipt until access is restored.

For a new reference calibration, rerun calibrate/init-production, commit the new
hashed calibration and config, and let the next UTC-date epoch pick it up. A
same-day existing epoch is immutable and will retain its previous target. Retain
old calibration/epoch files and verifier semantics for audit. To pause new
submissions, deliberately set config `enabled: false` and dispatch maintain;
accepted archive files remain intact.

## Real repository smoke test (not performed here)

Use a public test repository configured as above. Do not publish `examples/paper.md`
as though it were a real research contribution. After explicit authorization to
create public test content:

1. Run CI and initialize/publish a measured production challenge. Fetch the real
   Pages `challenges/latest.json`, matching raw epoch, registry, calibration,
   `agent-guide.md`, and empty `index.json`. Verify hashes locally.
2. Use the participant's numeric user ID and test repository ID to prepare a
   clearly labeled test paper. Mine **locally** with the real published target;
   generate both production instances; supply correct certificates; verify and
   submit one Issue using the participant's authorization.
3. Confirm the original request snapshot, paper/receipt atomic commit, successful
   Pages environment deployment, and a bot receipt with `published: true` plus
   a working project-subpath URL. Download the raw paper and compare SHA-256.
4. Rerun the original workflow and deliver the same body in another Issue with
   correctly bound proofs. Confirm one paper directory and canonical duplicate
   receipts. Edit the rejected request's body; confirm it remains sealed.
5. In this test repository only, deliberately arrange a deployment failure, then
   restore normal settings and dispatch maintain. Confirm pending publication
   transitions to published without another paper. Interrupt a queued run and
   confirm bounded recovery uses observation time. Exercise a genuine concurrent
   maintainer commit to observe fast-forward retry behavior.

These checks still require real GitHub credentials, repository settings, an actual
Issue and an actual Pages environment. Local API mocks/bare Git remotes do not
establish any of those outcomes.

## Official references and pinned Actions

Behavior was checked against GitHub's official documentation on 2026-09-17:
[workflow syntax/concurrency](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax),
[event semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows),
[token-trigger behavior](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow),
[secure workflow use](https://docs.github.com/en/actions/reference/security/secure-use),
[custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages),
[Issues REST API](https://docs.github.com/en/rest/issues/issues).

Tags were resolved to actual complete commit SHAs through the official repository
Git refs API; the relevant pinned `action.yml` files were also read:

| Action | Release | Verified commit |
| --- | --- | --- |
| actions/checkout | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| actions/setup-python | v7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| actions/upload-artifact | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| actions/download-artifact | v8.0.1 | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` |
| actions/upload-pages-artifact | v5.0.0 | `fc324d3547104276b827a68afc52ff2a11cc49c9` |
| actions/deploy-pages | v5.0.1 | `368f82528645a54fb793d4d04e342629a3f51346` |

The Pages upload composite itself pins its upload action to a complete commit.
The selected actions use Node 24 and standard current GitHub-hosted runners;
there is no self-hosted runner or untrusted PR deployment. Review pins deliberately
when upgrading. CI in this delivery has not run on a real GitHub runner.
