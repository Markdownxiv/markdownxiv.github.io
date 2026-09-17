"""Participant-side GitHub API submission, with no checkout or shell execution."""
import base64
import time
import uuid
from pathlib import Path
from urllib.parse import quote

from . import PR_PROTOCOLS
from .codec import canonical, read_json, sha, write_json
from .errors import Rejection, require
from .protocol import Context, verify
from .protocol_v3 import metadata_file
from .codec import utcnow


def format_pr(package):
    from .envelope import escape
    meta = package["metadata"]
    authors = []
    for name, url in zip(meta["authors"], package["author_homepages"]):
        authors.append('[' + escape(name) + '](<' + quote(url, safe=":/?#[]@!$&'()*+,;=%") + '>)' if url else escape(name))
    return ("<!-- markdownxiv-submission-" + package["protocol"].rsplit("-", 1)[1] + " -->\n\n## " + escape(meta["title"]) + "\n\n"
            + "**Authors:** " + "; ".join(authors) + "\n\n"
            + escape(meta["abstract"]) + "\n\n"
            + "Content commitment: `" + package["content_hash"] + "`\n\n"
            + "The submission files and proofs are in this PR. Discussion stays on this PR after publication.\n")


def submit(github, repository, package, root, paper, images, checkpoint, draft=False):
    require(package["protocol"] in PR_PROTOCOLS, "protocol_version", "Production submission requires a versioned PR package.")
    target = github.repository(repository)
    require(target.get("private") is False, "private_repository", "The target archive must be public.")
    user = github.request("GET", "/user")
    verify(package, root, Context(str(target["id"]), str(user["id"]), utcnow()), True,
           supplied_body=paper, supplied_assets=images)
    require(set(images) == {entry["path"] for entry in package["assets"]}, "asset_manifest_mismatch", "Upload only the declared images.")
    binding = sha(canonical(package))
    state = read_json(checkpoint) if Path(checkpoint).exists() else None
    if state:
        require(state["binding"] == binding and state["repository"] == repository and state["user_id"] == str(user["id"]),
                "checkpoint_mismatch", "PR checkpoint belongs to a different submission or account.")
    else:
        fork_name = user["login"] + "/" + target["name"]
        if fork_name == repository:
            fork = target  # An owner cannot fork their own repository; only a new submission branch is written.
        else:
            try:
                fork = github.repository(fork_name)
            except Rejection as exc:
                if exc.code != "github_not_found":
                    raise
                github.request("POST", "/repos/" + repository + "/forks", {"default_branch_only": True})
                deadline = time.monotonic() + 60
                while True:
                    try:
                        fork = github.repository(fork_name)
                        break
                    except Rejection as retry:
                        if retry.code != "github_not_found" or time.monotonic() >= deadline:
                            raise
                        time.sleep(2)
            require(fork.get("fork") is True and str(fork.get("parent", {}).get("id")) == str(target["id"])
                    and fork.get("private") is False, "fork_mismatch", "Your matching repository must be a public fork of this archive.")
        branch = "preprint/" + uuid.uuid4().hex
        base = github.request("GET", "/repos/" + repository + "/git/ref/heads/" + quote(target["default_branch"], safe="/"))["object"]["sha"]
        base_tree = github.request("GET", "/repos/" + repository + "/git/commits/" + base)["tree"]["sha"]
        directory = "submissions/" + branch.split("/")[1] + "/"
        files = {"paper.md": paper, "metadata.json": canonical(metadata_file(package)) + b"\n",
                 "submission.json": canonical(package) + b"\n", **images}
        tree = []
        for relative, raw in files.items():
            blob = github.request("POST", "/repos/" + fork_name + "/git/blobs", {"encoding": "base64", "content": base64.b64encode(raw).decode()})
            tree.append({"path": directory + relative, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        created = github.request("POST", "/repos/" + fork_name + "/git/trees", {"base_tree": base_tree, "tree": tree})
        commit = github.request("POST", "/repos/" + fork_name + "/git/commits",
                                {"message": "Submit Markdownxiv manuscript", "tree": created["sha"], "parents": [base]})
        github.request("POST", "/repos/" + fork_name + "/git/refs", {"ref": "refs/heads/" + branch, "sha": commit["sha"]})
        state = {"binding": binding, "repository": repository, "user_id": str(user["id"]), "head": user["login"] + ":" + branch,
                 "head_sha": commit["sha"], "base": target["default_branch"], "requested": False}
        write_json(checkpoint, state)
    found = github.request("GET", "/repos/" + repository + "/pulls?state=all&head=" + quote(state["head"], safe="") + "&base=" + quote(state["base"], safe=""))
    if found:
        require(len(found) == 1 and found[0]["head"]["sha"] == state["head_sha"], "submission_conflict", "The saved submission branch changed.")
        return found[0]
    require(not state["requested"], "submission_pending", "An earlier PR creation may have reached GitHub. Inspect the saved branch before creating another PR.")
    state["requested"] = True
    write_json(checkpoint, state)
    return github.request("POST", "/repos/" + repository + "/pulls",
                          {"head": state["head"], "base": state["base"], "title": "[preprint] " + package["metadata"]["title"][:230],
                           "body": format_pr(package), "draft": draft, "maintainer_can_modify": False})
