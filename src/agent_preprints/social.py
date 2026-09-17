"""Bounded read-only GitHub discussion snapshots, for build artifacts only."""
import argparse
import math
import os
import time
from pathlib import Path

from .codec import read_json, timestamp, utcnow, write_json
from .errors import Rejection
from .github import GitHub, wall_timeout
from .works import all_works


def sync(root, github, now=None, limit=20, previous=None):
    """A UTC-hour rotating window polls reactions even without Issue updated_at changes.

    No comment bodies are committed to Git. A fresh artifact contains only this poll's
    data. API errors leave the GitHub discussion link available and never block build.
    Optional previous counts are not comment caches and are not needed by production.
    """
    now = now or utcnow()
    works = all_works(root)
    repository = read_json(Path(root) / "config" / "production.json")["repository"]
    cursor = ((int(timestamp(now).timestamp()) // 3600) * limit) % len(works) if works else 0
    chosen = (works[cursor:] + works[:cursor])[:limit]
    records = []
    deadline = time.monotonic() + 90
    for work in chosen:
        if time.monotonic() >= deadline:
            break
        item = {"work_id": work["work_id"], "last_synced_at": None, "status": "unavailable", "comments": []}
        try:
            with wall_timeout(min(12, max(.001, deadline - time.monotonic()))):
                issue = github.issue(repository, work["root_issue_number"])
                reactions = issue.get("reactions", {})
                item.update({"likes": str(max(0, int(reactions.get("+1", 0)))), "dislikes": str(max(0, int(reactions.get("-1", 0)))),
                             "comment_count": str(max(0, int(issue.get("comments", 0))))})
                count = int(item["comment_count"])
                comments = github.comments(repository, work["root_issue_number"], max(1, math.ceil(count / 100))) if count else []
                # GitHub's latest page includes deletions/edits. Never retain old bodies
                # when a later successful poll returns fewer or different comments.
                for comment in comments[-20:]:
                    if comment.get("user", {}).get("type") == "Bot":
                        continue
                    cid = str(comment["id"])
                    if not cid.isdecimal():
                        continue
                    item["comments"].append({"id": cid, "author": str(comment.get("user", {}).get("login", "deleted"))[:80],
                                             "body": str(comment.get("body") or "")[:2000],
                                             "updated_at": str(comment.get("updated_at", ""))[:30]})
                item["comments"] = item["comments"][-5:]
                item.update({"status": "synced", "last_synced_at": now})
        except (Rejection, OSError, ValueError, TypeError, KeyError):
            item["comments"] = []
        records.append(item)
    return {"schema": "markdownxiv-social-v1", "generated_at": now, "cursor": str(cursor), "works": records}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default=".work/social.json")
    args = parser.parse_args()
    github = GitHub(os.environ.get("GITHUB_TOKEN"))
    write_json(args.out, sync(args.root, github))


if __name__ == "__main__":
    main()
