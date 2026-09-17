# PR admission threat model

Trust the maintainers, default-branch implementation, measured calibration and epoch
registry, pinned taxonomy, GitHub numerical identities, GitHub event delivery and
TLS/API infrastructure. Calibration is an auditable measurement, not hardware
attestation. A malicious maintainer can change trusted policy; this system does not
protect against its own administrators. Historical details remain in
[THREAT_MODEL_V2.md](THREAT_MODEL_V2.md).

## Untrusted inputs

A participant can create forks and PRs, modify draft files, edit descriptions, push
new commits, forge Git author timestamps, provide malformed JSON/Markdown/images,
post comments, use multiple accounts, replay proofs and outsource all computation.
These capabilities never grant archive write permission or execution of submitted
programs. New production requests are v3 ready PRs, not Issues.

The workflow uses `pull_request_target` but always checks out trusted default-branch
code. It never checks out or merges the contributor branch. Regular code CI does
not run on submission branches. PR text is data in event/JSON files, never shell
source, workflow YAML or executable certificates. Git subprocess arguments are
fixed or validated trusted identifiers, with shell execution disabled.

Only one bounded added submission directory is eligible. Its exact changed-file
set must match the declared manuscript, canonical metadata, proof and image files.
Only public GitHub commit/tree/blob APIs are used, with exact object hashes, safe
paths, ordinary file modes, no redirects and bounded sizes/deadlines. Source data
cannot select a different network host. Oversized/truncated API results fail closed.

## Proofs, homepages and time

PoW binds repository and submitting account IDs, the published epoch, manuscript
bytes, author names, subject/AI metadata, image manifest and revision intent.
Author homepage URLs are deliberately excluded. They are safe HTTPS display links,
not verified identities. The sealed Git commit records their values; changing them
before sealing does not require another PoW. They still count toward material size.

The original ready event supplies immutable source commits. First durable processing
seals those references with observation time. Later pushes and edits cannot replace
the request. Recovery without an original persisted seal observes the current head
at the current time, never the PR's earlier creation or an author-controlled date.
This conservative policy can require resubmission after a long queue delay.

The two mathematical families retain their definitions and independent verifiers.
Public conventional algorithms solve them quickly. Neither these certificates nor
PoW establish author/Agent identity, originality, paper correctness, time elapsed,
exclusive account ownership, peer review or resistance to outsourced answers.

## Storage and presentation

Material size is at most 1,000,000 bytes per version including canonical metadata
and homepage display fields. The request proof and generated archived proof have
independent limits. Declared sizes are checked against actual bytes. Image count,
pixels, parser limits and isolated decoder resource limits still apply. Material is
never silently recompressed or rewritten. Invalid proofs are rejected before large
manuscript/image downloads.

Atomic journals, compare-and-swap revision checks and fresh fast-forward Git
transactions prevent partial acceptance and stale parent replacement. Non-fast-forward
retries revalidate against current archive state. No forced updates are used. Accepted
archives and their success receipts commit together; publication is only recorded
after confirmed Pages success. Stale deployment artifacts are rejected.

The site escapes author, title, abstract and discussion text. Homepages accept only
HTTPS URLs without credentials or control characters. Search builds DOM nodes with
textContent. CSP allows only same-origin assets, index requests and search forms.
Raw Markdown is a separate exact-byte text response. Discussion previews are bounded,
inert text and are not committed to Git. No browser token field or remote tracker
image is embedded. Following an author or discussion link is a reader action.

## Operational limits

PoW cannot prevent a PR from being opened or every Actions runner startup. Forks,
failed requests, receipt history, API calls and site rebuilds still consume resources.
The finite workflow queue can overflow; recovery is bounded and may be delayed.
GitHub permissions, branch rules, public-fork availability, scheduled-run delivery,
Pages quotas and service outages remain external dependencies. The 900 MB generated
site limit leaves operational headroom but does not provide unlimited archive scale.

PR acceptance closes the discussion PR rather than merging its branch. Closing or
commenting can fail independently and is retried; a comment does not substitute for
an actual archive commit or deployment. Local API fixtures and bare-Git tests do not
establish live behavior from a non-collaborator account with repository Issues disabled.
