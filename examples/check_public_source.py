"""Read-only integration probe: the Actions token must read another public repo.

This reads one pinned Markdown blob as data. It never executes or archives it, and
does not create an Issue, reaction, comment, repository or permission change.
"""
import os
from agent_preprints.codec import canonical, sha
from agent_preprints.github import GitHub


def main():
    # A reviewed public GitHub source, independent of the Markdownxiv installation.
    source = {"kind": "github", "repository": "github/markup", "commit": "76e2682193828b98471b3a071edf4db0590ccacb", "path": "README.md"}
    body = GitHub(os.environ.get("GITHUB_TOKEN")).fetch_paper_v2(source)
    print(canonical({"status": "public_source_read_verified", "repository": source["repository"],
                     "commit": source["commit"], "bytes": str(len(body)), "sha256": sha(body)}).decode())


if __name__ == "__main__":
    main()
