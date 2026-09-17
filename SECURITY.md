# Security model

Treat the repository's default-branch code, production configuration, published
epoch/calibration registry, workflows, GitHub event delivery, GitHub APIs and
maintainers as trusted. Treat every Issue field, referenced paper byte, certificate
and client claim as untrusted data. The protocol and security details are in
[docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) and [docs/PROTOCOL.md](docs/PROTOCOL.md).

Do not run submitted scripts, merge submission PRs, load executable certificates,
put Issue text in shell/workflow expressions that execute, or give submitters
repository write access. Do not add a production `--dev` override or enable
admission before publishing an actual measured calibration and epoch.

For a security issue, contact the repository maintainers privately where possible.
Use GitHub private vulnerability reporting if the repository has it enabled. Do
not create a public Issue containing credentials or an active exploit against a
live archive. This project does not provision an external reporting service.

All admitted content, submitted answers and normal Issue bodies are public. Users
must not submit secrets. Neither PoW nor mathematical certificates authenticate
authorship or establish the safety/correctness of a paper. Code dependencies and
Actions are pinned; update them deliberately with tests and review.
