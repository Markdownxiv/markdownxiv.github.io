# Historical v1/v2 threat model and operational limits

## Trust boundary

Trust default-branch maintainers/code, committed production calibration and epoch
registries, GitHub's repository/user IDs, original Actions event payloads, TLS/API
responses and official action/artifact infrastructure. There is no protection
against a malicious maintainer changing trusted admission code or falsifying a
benchmark. A calibration record is an auditable measurement declaration, not a
hardware attestation. Repository administrators control the archive's policy.

An adversary may own many GitHub accounts and public repositories, open/edit/close
Issues, post comments, supply arbitrary JSON/Markdown, exploit timing, outsource
solving, optimize mining, replay requests and compete with concurrent submissions.
An adversary has no write permission to the archive, no arbitrary URL fetcher,
no execution slot for submitted programs and no client-selected difficulty.

## Binding, mathematical evidence, and gaming

PoW commits to exact paper bytes through SHA-256, exact allowed metadata, target
repository ID, submitting GitHub user ID and immutable epoch bytes (including
salt, target, policy and version). Domain separation, byte lengths, fixed nonce
width and integer endianness are specified. The verifier uses trusted server
configuration and event IDs, not a client assertion. Cross-repository/account
replay and post-mining text changes fail commitment checks. Hash collision
resistance and SHA-256's usual pseudorandom mining model are assumptions.

Every question seed comes from a valid PoW hash. There is no freely chosen seed
or post-PoW metadata knob. Finding another valid nonce can still yield an easier
problem; the design charges another successful PoW rather than claiming to
eliminate grinding. The two mathematical generators sample input objects directly,
without a secret answer or a public planted-solution shortcut. All certificates
are independently checked and disclosed, and conventional public algorithms can
solve both families quickly. No Agent identity, author quality, human exclusion,
Sybil resistance, original authorship, research correctness or anti-outsourcing
claim is justified. Exact-body deduplication is not plagiarism detection; changing
one byte can evade it after providing fresh bound proofs.

The reference 300-second target is an expectation for a specified implementation,
CPU/workload and thread count. Hardware, native implementations, ASICs/GPUs,
batching and random variance change observed cost. A valid proof cannot establish
that five minutes elapsed, that a CPU was used, or that the work had environmental
or economic value. All answers and content are public. Epoch rotation changes
public salts and parameters, not mathematical knowledge or family code by magic.

## Input and execution safety

Before body network access, the pipeline bounds/parses AP-JSON, checks a field
whitelist, trusted identities and an immutable published production epoch, then
checks PoW with one SHA-256. Integer/certificate/dimension/node/depth limits avoid
unbounded arithmetic or parsing. The mathematical verifier has a deadline as well
as finite operation sizes. Ordinary rendering happens in a separate process with
CPU/memory/wall-clock limits; timeout falls back to escaped text. Renderer failure
does not falsely accept a proof or stop publication of all other papers.

No `eval`, submitted executable proofs, LLM grading, dynamic code import, mutable
branch/tag ref, arbitrary HTTP URL, repository checkout of a submitter source,
symlink/submodule dereference or unrestricted redirect is available. Body fetching
uses only `api.github.com`, a public repo, a commit SHA, bounded nonrecursive tree
walks, and one ordinary blob with size/object/SHA-256 checks. A large tree, invalid
path or unavailable source is rejected. No paper images or attachments are fetched
at build time or rendered as remote trackers. Explicit outbound links are permitted;
following one is a reader's action, not part of server verification.

Markdown disables raw HTML. Templates remain text. Dangerous URI schemes are not
rendered as active links. LaTeX is converted into a whitelist of native MathML
elements/attributes; unsupported or oversized expressions become escaped code.
Page metadata is escaped, search uses `textContent`, and CSP disallows inline
scripts, images and external requests. No CDN math script or browser token field
exists. CSP is defense in depth: primary safety is rendering and escaping data.

Issue content enters Python through `GITHUB_EVENT_PATH` or a bounded JSON artifact,
never as shell program text or untrusted filesystem paths. Paper paths use full
hashes. The only subprocesses execute fixed trusted programs/arguments (Git and
local platform CLI), with `shell=False`. Git transaction write paths are limited to
paper/receipt/challenge/state data. Source repositories never become build inputs
other than the single already-hashed Markdown byte sequence.

## Time, state and repeated delivery

The original `opened` snapshot's body and time are checked together and sealed on
first processing. A later Issue edit cannot fill missing answers, change a paper,
or turn a rejected snapshot into a success. Recovery from a lost event checks the
first reliably observed complete body at **observation time**, never with the old
creation timestamp. Conservative recovery may require an honest user to resubmit
and perform a new proof when the original window was lost. Deleted Issues cannot
be recovered from the Issues listing, and missing credentials cannot be invented.

Archive commits contain a paper and its success receipt atomically. Local directory
rename and request seals handle interrupted work; fresh Git worktrees and ordinary
fast-forward pushes avoid stale checkout overwrites. Conflicts cause bounded
fresh-state revalidation. Same Issue identity returns the existing sealed result;
same raw body hash returns the existing paper even under a changed title. A crash
after successful remote push but before acknowledgment is safe on the next read.

Both business workflows share a concurrency group spanning all write/deploy jobs.
Finite queue capacity is handled by bounded cyclic Issue scanning, not an assumption
that all pending runs survive. A deploy guard compares an artifact source digest
against current trusted state, so rerunning a failed old deployment cannot knowingly
replace newer archive content. All archive automation uses this lock; maintainers
should also avoid unrelated manual Pages deployments and concurrent manual archive
edits. A human push during a deploy remains outside GitHub's workflow lock; the
next maintain rebuild reconciles it, and the manifest marks only actually included
papers published. Publication metadata is conservative if the deploy succeeds but
finalization fails: it stays pending until a successful retry.

Comments are upserted using stored IDs plus bot-only markers. If a POST succeeds
but its ID commit fails, a later marker scan usually finds it. The scan is capped
at 1000 comments, so a large comment flood can cause duplicate bot comments; it
still cannot create another paper. Validation retries are bounded/backed off and
permanent rejections are sealed. Rebuilding and comment synchronization do not
remine, re-solve or duplicate an already archived request.

## Availability, cost and free-service limits

PoW cannot prevent an invalid Issue from being created on GitHub or prevent all
runner startups. Invalid submissions still consume API/runner/storage resources
and create public sealed rejection records. Rejections skip the Pages rebuild,
but this remains a small-scale public gate, not a complete DoS defense. Per-file
and per-run limits do not create an unlimited total storage allowance. Full-site
rebuilds, Git history growth, receipt scans and eventual recovery are intentionally
simple and will limit scale. Under sustained abuse, maintainers may need to pause
admission or use GitHub's normal repository abuse controls.

The 100-entry Actions pending queue can overflow. API rate limits, token scope,
branch rules, environment restrictions, scheduled-workflow disablement, canceled
runs, artifact expiry, CDN propagation and GitHub outages can interrupt service.
No artificial success receipt hides a failed write/deploy. An unavailable comment
API can prevent a rejection receipt; maintenance attempts recovery later. The
scan processes only bounded pages/candidates per run, so deadlines may expire
before backlogged requests can be reliably observed.

“Free” means small-scale use within GitHub's current offerings and acceptable-use
terms. Submitters pay their own computation. There is no promise of infinite
throughput, permanent free infrastructure or GitHub approval for this use case.
This is a paper-archive gate, not a general remote job/compute service. See the
official [hosted runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners),
[Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits),
and [additional-product terms](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features).
