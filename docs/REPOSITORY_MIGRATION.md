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
