# Organization Repository Migration

The owner authorized moving the existing public repository from `kzoacn/Markdownxiv`
to `Markdownxiv/markdownxiv.github.io`, with Pages at `https://markdownxiv.github.io/`.
Use a native GitHub transfer and rename, not a code-only import into another identity.

## Identity and Data

The original numerical repository ID is `1374075838`. Proof of Work binds this ID,
not the owner/name string or Pages path. The ID must remain unchanged after transfer.
All manuscript, metadata, proof, image, work, epoch, calibration and taxonomy bytes
are retained. Existing PRs, comments and reactions move with the repository.

The pre-existing target initializer has repository ID `1375332559` and a single
README commit, `526ac64f7861cca5caf14ce56ed1086ad31c6fa4`. Rename it to
`Markdownxiv/markdownxiv-site-placeholder` and keep it private. Do not delete it or
replace its history. Freeing the target name permits transfer of the real repository.

Sealed request snapshots retain their original repository paths and receipt times.
Source reads resolve the recorded numerical repository ID through GitHub's API,
verify that ID and public visibility, then read the recorded commits under the
current repository name. No redirect following or snapshot rewriting is introduced.

Receipt URLs are mutable publication metadata. Only after a successful new-site
deployment does finalization update the work, version and discussion URLs from
trusted configuration. It reuses the existing bot comment ID and keeps the sealed
request, proof, work and paper IDs unchanged.

## Cutover

1. Back up Git refs, Pages/Actions/environment settings, PR 5 and its comments,
   immutable file hashes and receipt identities outside published source paths.
2. Verify the migration compatibility tests, full unittest suite and offline demo.
3. Disable acceptance and scheduled maintenance, wait for active runs to finish,
   and commit the new addresses with admission paused. Run CI on that exact commit.
4. Rename the private initializer, then transfer and rename the public repository.
   Verify the stable ID, Git history, PR/comment IDs and repository visibility.
5. Configure workflow-based Pages and its environment/branch permissions. Enable
   admission in the migrated configuration, run CI, and dispatch maintenance to
   build/deploy the new root-path site and reconcile receipts.
6. Verify the production challenge from the new origin, abs/reader/raw routes,
   navigation, agent instructions and PR discussion. Restore PR-only acceptance
   and maintenance. Project Issues remain enabled for project feedback.
7. Update local remotes to `git@github.com:Markdownxiv/markdownxiv.github.io.git`.
   Report any local filesystem restriction that prevents updating an existing clone.

GitHub redirects old Git/repository/PR URLs after a native transfer. Old GitHub Pages
URLs are not automatically redirected. Do not recreate `kzoacn/Markdownxiv`: doing
so would remove GitHub's old-repository redirect and confuse historical source paths.

## Verification

Tests exercise ID-based source reads after a rename, rejection of ID/visibility
changes, root-path site generation, post-deployment receipt link reconciliation,
comment reuse and preservation of immutable bytes. Actual migration/deployment
results are recorded after the corresponding actions complete.

## Completed Migration: 2026-09-18

The native transfer completed to `Markdownxiv/markdownxiv.github.io`. GitHub's
numeric repository lookup confirms ID `1374075838`, public visibility, the `main`
default branch, and enabled project Issues. PR 5 retains ID `4561187059`, its closed
state and head commit. Its existing bot comment retains ID `5718533569` and now links
to the new site and discussion address. No additional PR/comment was created.

The initializer is preserved at `Markdownxiv/markdownxiv-site-placeholder`, repository
ID `1375332559`, with original commit `526ac64f7861cca5caf14ce56ed1086ad31c6fa4`.
Its visibility was explicitly set to private and verified after the rename.

Migration preparation commit `374e3f1703658768e1a6608fa4079c3ad7196c1f` paused
admission while acceptance and maintenance were disabled. The preparation CI passed
140 tests. After transfer, commit `67014e31bd3f0f0c68009384ce348bea4ae3e45e`
enabled the migrated configuration. [Organization CI](https://github.com/Markdownxiv/markdownxiv.github.io/actions/runs/35306516077)
passed all 140 tests in 29.602 seconds, all four offline demos, the production build
and the read-only public-source probe.

[The new-site deployment](https://github.com/Markdownxiv/markdownxiv.github.io/actions/runs/35306841309)
completed all five jobs. Workflow-based Pages, HTTPS, the `github-pages` environment
and its `main` branch policy remained available after transfer. Acceptance and
maintenance were restored after successful deployment and readback.

Fifteen immutable archive/work/epoch/calibration/taxonomy files matched their pre-move
hashes. The original sealed PR source was re-read from GitHub using its numerical ID
and independently verified at its original receipt time, without changing the old
repository names in the sealed snapshot. The new CLI origin served and validated the
published v4 challenge with the existing 30-second measurement and 8 MB policy.

Live Chromium checks at 1440x1000 and 390x844 passed the category homepage, Submit
clipboard action, text/plain llms.txt, abs page, rendered Markdown, raw Markdown,
search and About links. No horizontal overflow or JavaScript errors occurred. The
raw manuscript SHA-256 remains
`c97cf8a07cf3788c09371b50089b26963cc470d7bbb207bbae6859fabad47adf`.
The old PR URL returned HTTP 301 to the new PR, and the old SSH Git URL still resolved.

Backups are local under `.work/migration/` and are not published. The release clone's
origin uses the new SSH URL. The workspace's original `.git` is mounted read-only;
updating its origin failed with `Read-only file system`. In a writable local terminal,
the remaining local configuration command is:

```bash
git remote set-url origin git@github.com:Markdownxiv/markdownxiv.github.io.git
```

No new manuscript, review, reaction, or project Issue was published during migration.
