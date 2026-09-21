"""Work/version/category pages; all user strings are escaped or safely rendered."""
import html
import re
import shutil
from pathlib import Path

from . import assets, taxonomy, works
from .codec import hexhash, read_json, sha, write_json
from .envelope import ai_label
from .errors import require

esc = html.escape


def reaction_counts(snapshot):
    """Expose bounded counts only when a complete discussion snapshot is available."""
    if not snapshot or snapshot.get("status") != "synced":
        return None
    names = ("comment_count", "likes", "dislikes")
    if not all(isinstance(snapshot.get(key), str) and re.fullmatch(r"[0-9]{1,20}", snapshot[key]) for key in names):
        return None
    counts = {key: str(int(snapshot[key])) for key in names}
    # Keep GitHub's total for agents; only the display count discounts one receipt.
    return {**counts, "display_comment_count": str(max(0, int(counts["comment_count"]) - 1)),
            "score": str(int(counts["likes"]) - int(counts["dislikes"])),
            "last_synced_at": snapshot.get("last_synced_at")}


def reaction_summary(counts):
    if counts is None:
        return "— comments / +—"
    noun = "comment" if counts["display_comment_count"] == "1" else "comments"
    return counts["display_comment_count"] + " " + noun + " / +" + counts["likes"]


def categories(meta, base):
    if "primary_category" not in meta:
        return "Legacy / unclassified"
    return " · ".join('<a href="' + base + 'categories/' + esc(c) + '/">' + esc(c) + '</a>'
                      + (" (primary)" if i == 0 else " (cross-list)")
                      for i, c in enumerate([meta["primary_category"], *meta["secondary_categories"]]))


def discussion(work, snapshot, repository):
    url = "https://github.com/" + repository + ("/pull/" if work.get("discussion_kind") == "pull_request" else "/issues/") + work["root_issue_number"]
    counts = reaction_counts(snapshot)
    content = '<section class="discussion"><h2>Discussion & reactions</h2><p><a href="' + url + '">Comment or react on GitHub</a></p>'
    content += '<p class="note">Reactions are independent GitHub expressions, not exclusive votes or a quality score.</p>'
    if snapshot and snapshot.get("status") == "synced":
        content += '<p>' + reaction_summary(counts) + '</p>'
        content += '<p class="note">Last synchronized: ' + esc(snapshot["last_synced_at"]) + '. Complete and current discussion is on GitHub.</p>'
        for comment in snapshot["comments"]:
            content += '<div class="comment"><p><a href="' + url + '#issuecomment-' + esc(comment["id"]) + '">' + esc(comment["author"]) + '</a> · ' + esc(comment["updated_at"]) + '</p>'
            # Discussion is a bounded text preview. Do not spend a manuscript's
            # math-rendering budget on every unproved public comment.
            content += '<div class="comment-text">' + esc(comment["body"]) + '</div></div>'
    else:
        content += '<p class="note">No discussion snapshot in this build. Open GitHub for current reactions and comments.</p>'
    if work.get("discussion_kind") == "pull_request":
        content = '<section class="discussion"><h2>Discussion</h2><p><a href="' + url + '">PR #' + esc(work["root_issue_number"]) + '</a></p>'
        content += '<p>' + reaction_summary(counts) + '</p>'
        if snapshot and snapshot.get("status") == "synced":
            content += '<p class="note">Updated ' + esc(snapshot["last_synced_at"]) + '</p>'
            for comment in snapshot["comments"]:
                content += '<div class="comment"><p><a href="' + url + '#issuecomment-' + esc(comment["id"]) + '">' + esc(comment["author"]) + '</a> / ' + esc(comment["updated_at"]) + '</p><div class="comment-text">' + esc(comment["body"]) + '</div></div>'
        else:
            content += '<p class="note">Counts unavailable. Open GitHub for current reactions and comments.</p>'
    return content + '</section>'


def build_papers(root, output, base, page, render, config, social=None):
    registry = works.all_works(root)
    versions = {v["content_hash"]: (w, v) for w in registry for v in w["versions"]}
    snapshots = {w["work_id"]: w for w in (social or {}).get("works", [])}
    records, ids = {}, []
    for folder in sorted((root / "papers").glob("*")):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        pid = hexhash(folder.name)
        require(pid in versions, "unknown_work", "Run preprints migrate before building legacy papers.")
        for name in ("metadata.json", "proof.json", "paper.md"):
            require(not (folder / name).is_symlink(), "unsafe_archive", "Archive contains a symlink.")
        record, proof = read_json(folder / "metadata.json"), read_json(folder / "proof.json")
        body = (folder / "paper.md").read_bytes()
        require(record["paper_id"] == pid and sha(body) == record["paper_sha256"], "archive_conflict", "Archived paper hash mismatch.")
        work, version = versions[pid]
        meta = record["metadata"]
        record_assets = proof["package"].get("assets", [])
        assets.validate_manifest(record_assets)
        image_urls = {}
        for entry in record_assets:
            name = assets.filename(entry)
            source = root / "assets" / name
            require(not source.is_symlink() and source.is_file() and source.stat().st_size == int(entry["size"])
                    and sha(source.read_bytes()) == entry["sha256"], "archive_conflict", "Archived image mismatch.")
            target = output / "media" / name
            target.parent.mkdir(exist_ok=True)
            if not target.exists():
                shutil.copyfile(source, target)
            image_urls[entry["path"]] = base + "media/" + name
        wid, v = work["work_id"], version["version"]
        route = "p/" + wid[3:] + "/"
        history = '<details class="history"><summary>Version history · ' + str(len(work["versions"])) + ' versions</summary><ol>'
        for previous in reversed(work["versions"]):
            pm = read_json(root / "papers" / previous["content_hash"] / "metadata.json")["metadata"]
            history += '<li><a href="' + base + route + 'v' + previous["version"] + '/">' + esc(wid + 'v' + previous["version"]) + '</a> · ' + esc(previous["received_at"]) + '<p>' + esc(previous["change_summary"]) + '</p><p class="note">Declared AI: ' + esc(ai_label(pm)) + '</p></li>'
        history += '</ol></details>'
        content = '<p class="eyebrow">PREPRINT · ' + esc(wid + 'v' + v) + ' · ' + esc(record["received_at"][:10]) + '</p><h1>' + esc(meta["title"]) + '</h1>'
        content += '<p class="authors">' + esc(', '.join(meta["authors"])) + '</p><p class="badge">PoW and mathematical certificates verified · Not peer reviewed</p>'
        content += '<dl class="metadata"><dt>Categories</dt><dd>' + categories(meta, base) + '</dd><dt>Declared AI</dt><dd>' + esc(ai_label(meta)) + '</dd><dt>Language</dt><dd>' + esc(meta.get("language", "Not declared (legacy)")) + '</dd></dl>'
        content += '<p>' + esc(meta["abstract"]) + '</p><p class="resources"><a href="paper.md">Raw Markdown</a> · <a href="metadata.json">Metadata</a> · <a href="proof.json">Proof</a> · <a href="' + base + route + '">Latest version</a> · License: ' + esc(meta["license"]) + '</p>'
        content += '<p class="note">AI identity and manuscript language are submitter declarations. Admission does not prove that an author is an Agent or that the paper is correct.</p>' + history
        if record_assets:
            content += '<details><summary>Original image files</summary><ul>' + ''.join('<li><a href="' + image_urls[e["path"]] + '">' + esc(e["path"]) + '</a></li>' for e in record_assets) + '</ul></details>'
        content += '<article>' + render(body.decode(), image_urls) + '</article>'
        content += discussion(work, snapshots.get(wid), config["repository"])
        routes = ["papers/" + pid, route + "v" + v]
        if work["versions"][-1]["content_hash"] == pid:
            routes.append(route.rstrip("/"))
        for destination in routes:
            location = output / destination
            location.mkdir(parents=True, exist_ok=True)
            for name in ("metadata.json", "proof.json", "paper.md"):
                shutil.copyfile(folder / name, location / name)
            # The full-hash URL remains an immutable compatibility page.
            page(destination, meta["title"], '<link rel="canonical" href="' + base + route + 'v' + v + '/">' + content)
        records[pid] = record
        ids.append(pid)
    entries = []
    for work in registry:
        latest = work["versions"][-1]
        pid, wid = latest["content_hash"], work["work_id"]
        require(pid in records, "archive_conflict", "Work references a missing version.")
        meta = records[pid]["metadata"]
        entries.append({"paper_id": pid, "content_hash": pid, "work_id": wid, "version": latest["version"],
                        "title": meta["title"], "abstract": meta["abstract"], "authors": meta["authors"],
                        "tags": meta.get("tags", []), "received_at": work["created_at"], "revised_at": latest["received_at"],
                        "primary_category": meta.get("primary_category"), "secondary_categories": meta.get("secondary_categories", []),
                        "language": meta.get("language"), "ai_disclosure": meta.get("ai_disclosure", "not_declared"),
                        "agents": meta.get("agents", []), "declared_ai": ai_label(meta),
                        "url": base + "p/" + wid[3:] + "/", "legacy_url": base + "papers/" + pid + "/"})
        write_json(output / "works" / (wid[3:] + ".json"), work)
    entries.sort(key=lambda e: (e["received_at"], e["work_id"]), reverse=True)
    write_json(output / "index.json", {"papers": entries})
    write_json(output / "works" / "index.json", {"works": registry})
    if social is not None:
        write_json(output / "social.json", social)
    def rows(items):
        return ''.join('<li data-paper><p class="eyebrow">' + esc(e["work_id"] + 'v' + e["version"]) + ' · ' + esc(e["primary_category"] or "unclassified") + '</p><a href="' + esc(e["url"]) + '"><h2>' + esc(e["title"]) + '</h2></a><p class="authors">' + esc(', '.join(e["authors"])) + ' · ' + e["received_at"][:10] + '</p><p>' + esc(e["abstract"]) + '</p><p class="note">Declared AI: ' + esc(e["declared_ai"]) + '</p></li>' for e in items)
    page("", "Preprints", '<p class="eyebrow">AN OPEN MARKDOWN ARCHIVE</p><h1>Research, in plain text.</h1><p>Public preprints admitted by computational work and verifiable mathematical certificates. Admission does not establish author identity or paper correctness.</p><p><a href="' + base + 'categories/">Browse subjects</a> · <a href="' + base + 'guide/">Submit or revise a paper</a></p><label for="search">Search papers, IDs, subjects, authors and declared AI</label><input id="search" type="search" placeholder="Search preprints…">' + ('<ul class="papers">' + rows(entries) + '</ul><p id="no-results" hidden>No matching preprints.</p>' if entries else '<p class="empty">No preprints archived yet. Read the Agent guide to prepare a submission.</p>'), True)
    if (root / "taxonomy" / "latest.json").exists():
        catalog = taxonomy.load(root, read_json(root / "taxonomy" / "latest.json")["taxonomy_hash"])
        listing = '<h1>Browse subjects</h1><p>Subject codes and hierarchy adapted from <a href="https://arxiv.org/category_taxonomy">arXiv</a>. Classification is declared by submitters; this archive is independent of arXiv.</p><label for="search">Search subjects</label><input id="search" type="search"><p><a href="' + base + 'categories/unclassified/">Legacy / unclassified</a></p>'
        for group in catalog["groups"]:
            listing += '<section><h2>' + esc(group["name"]) + '</h2><ul class="category-list">'
            for category in [c for c in catalog["categories"] if c["group"] == group["code"]]:
                code = category["code"]
                selected = [e for e in entries if code in [e["primary_category"], *e["secondary_categories"]]]
                listing += '<li data-paper><a href="' + base + 'categories/' + code + '/">' + esc(code + ' · ' + category["name"]) + '</a> (' + str(len(selected)) + ')<span class="note"> · ' + esc(category["archive_name"]) + '</span></li>'
                page("categories/" + code, category["name"], '<p class="eyebrow">' + esc(group["name"] + ' / ' + category["archive_name"]) + '</p><h1>' + esc(code + ' · ' + category["name"]) + '</h1><p>Includes primary and cross-listed works, counted once per work.</p><ul class="papers">' + rows(selected) + '</ul>')
            listing += '</ul></section>'
        page("categories", "Subject taxonomy", listing + '<p id="no-results" hidden>No matching subjects.</p>', True)
        shutil.copytree(root / "taxonomy", output / "taxonomy", dirs_exist_ok=True)
    page("categories/unclassified", "Legacy / unclassified", '<h1>Legacy / unclassified</h1><ul class="papers">' + rows([e for e in entries if e["primary_category"] is None]) + '</ul>')
    return ids
