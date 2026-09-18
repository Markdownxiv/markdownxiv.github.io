"""Category catalog, abstract and reader pages, plus exact raw Markdown downloads."""
import html
import math
import shutil

from . import PROTOCOL_V4, PROTOCOL_V5, assets, taxonomy, works
from .codec import hexhash, read_json, sha, write_json
from .envelope import ai_label
from .errors import Rejection, require
from .github import user_identity
from .protocol_v3 import homepage
from .site_papers import discussion

PAGE_SIZE = 50
esc = html.escape


def author_html(names, links):
    result = []
    for i, name in enumerate(names):
        url = links[i] if i < len(links) else None
        try:
            homepage(url)
        except Rejection:
            url = None
        result.append('<a rel="nofollow noopener noreferrer" href="' + esc(url, quote=True) + '">' + esc(name) + '</a>' if url else esc(name))
    return ", ".join(result)


def rows(entries, base):
    parts = []
    for entry in entries:
        wid, version = entry["work_id"], entry["version"]
        links = '<a href="' + entry["url"] + '">abs</a> <span aria-hidden="true">|</span> <a href="' + entry["reader_url"] + '">md</a>'
        categories = [entry["primary_category"], *entry["secondary_categories"]]
        subjects = ', '.join('<a href="' + base + 'categories/' + esc(code) + '/">' + esc(code) + '</a>' for code in categories if code)
        revised = ' <span class="muted">(revised ' + esc(entry["revised_at"][:10]) + ')</span>' if entry["version"] != "1" else ""
        parts.append('<li class="paper-row" data-paper><div class="paper-id"><span>' + esc(wid + 'v' + version) + '</span><span class="paper-formats">' + links + '</span></div>'
                     + '<h2><a href="' + entry["url"] + '">' + esc(entry["title"]) + '</a></h2>'
                     + '<p class="authors">' + author_html(entry["authors"], entry["author_homepages"]) + '</p>'
                     + '<p class="paper-details"><time datetime="' + esc(entry["received_at"]) + '">' + esc(entry["received_at"][:10]) + '</time>' + revised + ' / ' + subjects + '</p></li>')
    return '<ol class="papers">' + ''.join(parts) + '</ol>'


def pagination(total, current, route, base):
    pages = max(1, math.ceil(total / PAGE_SIZE))
    def url(number):
        return base + route + ('/page/' + str(number) if number > 1 else '') + '/'
    start = (current - 1) * PAGE_SIZE + 1 if total else 0
    content = '<div class="list-tools"><span>' + str(start) + '-' + str(min(current * PAGE_SIZE, total)) + ' of ' + str(total) + '</span>'
    if pages > 1:
        content += '<nav class="pagination" aria-label="Pages">'
        if current > 1:
            content += '<a rel="prev" href="' + url(current - 1) + '">Previous</a>'
        choices = sorted({1, pages, *range(max(1, current - 2), min(pages, current + 2) + 1)})
        previous = 0
        for number in choices:
            if previous and number - previous > 1:
                content += '<span aria-hidden="true">...</span>'
            content += ('<span aria-current="page">' + str(number) + '</span>' if number == current
                        else '<a href="' + url(number) + '">' + str(number) + '</a>')
            previous = number
        if current < pages:
            content += '<a rel="next" href="' + url(current + 1) + '">Next</a>'
        content += '</nav>'
    return content + '</div>'


def build_catalog(root, output, base, page, render, config, social=None):
    registry = works.all_works(root)
    versions = {v["content_hash"]: (w, v) for w in registry for v in w["versions"]}
    snapshots = {w["work_id"]: w for w in (social or {}).get("works", [])}
    records = {}
    for folder in sorted((root / "papers").glob("*")):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        pid = hexhash(folder.name)
        require(pid in versions, "unknown_work", "An archived version has no registered work.")
        for name in ("paper.md", "metadata.json", "proof.json"):
            require(not (folder / name).is_symlink(), "unsafe_archive", "Archive files cannot be symlinks.")
        record = read_json(folder / "metadata.json")
        submitter = user_identity(record["submitter_id"], record.get("submitter", {}).get("login"))
        record["submitter"] = submitter
        proof = read_json(folder / "proof.json")
        body = (folder / "paper.md").read_bytes()
        require(record["paper_id"] == pid and sha(body) == record["paper_sha256"], "archive_conflict", "Archived manuscript hash mismatch.")
        work, version = versions[pid]
        meta, wid, number = record["metadata"], work["work_id"][3:], version["version"]
        links = version.get("author_homepages", [])
        (output / "md").mkdir(exist_ok=True)
        (output / "md" / (wid + "v" + number + ".md")).write_bytes(body)
        latest = work["versions"][-1]["content_hash"] == pid
        if latest:
            (output / "md" / (wid + ".md")).write_bytes(body)
        entries = proof["package"].get("assets", [])
        limits = {"max_image": 8_000_000, "max_total": 8_000_000} if proof["protocol"] in (PROTOCOL_V4, PROTOCOL_V5) else {}
        assets.validate_manifest(entries, **limits)
        downloads, image_urls = [], {}
        for entry in entries:
            name = assets.filename(entry)
            source = root / "assets" / name
            require(source.is_file() and not source.is_symlink() and source.stat().st_size == int(entry["size"])
                    and sha(source.read_bytes()) == entry["sha256"], "archive_conflict", "Archived image hash mismatch.")
            (output / "media").mkdir(exist_ok=True)
            if not (output / "media" / name).exists():
                shutil.copyfile(source, output / "media" / name)
            image_urls[entry["path"]] = base + 'media/' + name
            downloads.append('<a href="' + image_urls[entry["path"]] + '">' + esc(entry["path"]) + '</a>')
        version_id = wid + "v" + number
        abstract_url = base + "abs/" + version_id + "/"
        raw_url = base + "md/" + version_id + ".md"
        discussion_url = "https://github.com/" + config["repository"] + ("/pull/" if work.get("discussion_kind") == "pull_request" else "/issues/") + work["root_issue_number"]
        reader = ('<div class="reader"><div class="reader-heading"><p class="identifier">'
                  + esc(work["work_id"] + 'v' + number) + ' / ' + esc(version["received_at"][:10]) + '</p>'
                  + '<p class="authors">' + author_html(meta["authors"], links) + '</p>'
                  + '<nav class="reader-links" aria-label="Manuscript views"><a href="' + abstract_url + '">Abstract</a>'
                  + '<a href="' + raw_url + '">Raw Markdown</a><a href="' + esc(discussion_url, quote=True) + '">Discussion</a>'
                  + '<a href="' + base + 'md/' + wid + '/">Latest version</a></nav></div>'
                  + '<article class="manuscript">' + render(body.decode("utf-8"), image_urls) + '</article></div>')
        for route in ["md/" + version_id] + (["md/" + wid] if latest else []):
            page(route, meta["title"], reader)
        subjects = ', '.join('<a href="' + base + 'categories/' + esc(c) + '/">' + esc(c) + '</a>' for c in [meta.get("primary_category"), *meta.get("secondary_categories", [])] if c)
        submitted_by = esc('@' + submitter["login"] if submitter["login"] else 'GitHub user ' + submitter["github_id"])
        if submitter["profile_url"]:
            submitted_by = '<a href="' + esc(submitter["profile_url"], quote=True) + '">' + submitted_by + '</a>'
        history = '<ol class="versions">' + ''.join('<li><a href="' + base + 'abs/' + wid + 'v' + v["version"] + '/">v' + v["version"] + '</a> <time>' + esc(v["received_at"][:10]) + '</time><span>' + esc(v["change_summary"]) + '</span></li>' for v in reversed(work["versions"])) + '</ol>'
        content = ('<div class="breadcrumb"><a href="' + base + '">Subjects</a> / ' + subjects + '</div>'
                   + '<div class="abstract-heading"><p class="identifier">' + esc(work["work_id"] + 'v' + number) + '</p><h1>' + esc(meta["title"]) + '</h1>'
                   + '<p class="authors">' + author_html(meta["authors"], links) + '</p></div>'
                   + '<div class="abstract-layout"><section class="abstract-content"><h2>Abstract</h2><p class="abstract-text">' + esc(meta["abstract"]) + '</p>'
                   + '<dl class="metadata"><dt>Subjects</dt><dd>' + subjects + '</dd><dt>Submitted</dt><dd>' + esc(work["created_at"][:10]) + '</dd>'
                   + '<dt>Submitted by</dt><dd>' + submitted_by + '</dd>'
                   + '<dt>This version</dt><dd>' + esc(version["received_at"][:10]) + '</dd><dt>License</dt><dd>' + esc(meta["license"]) + '</dd>'
                   + '<dt>Language</dt><dd>' + esc(meta.get("language", "Unknown")) + '</dd><dt>Declared AI</dt><dd>' + esc(ai_label(meta)) + '</dd></dl>'
                   + '<h2>Submission History</h2>' + history + '</section><aside class="paper-access"><h2>Access</h2><ul>'
                   + '<li><a class="primary-link" href="' + base + 'md/' + version_id + '/">Read Markdown</a></li>'
                   + '<li><a href="' + raw_url + '">Raw Markdown</a></li>'
                   + '<li><a href="metadata.json">Metadata</a></li><li><a href="proof.json">Proof of Work &amp; certificates</a></li>'
                   + '<li><a href="' + base + 'abs/' + wid + '/">Latest version</a></li></ul>'
                   + ('<h3>Figures</h3><ul>' + ''.join('<li>' + d + '</li>' for d in downloads) + '</ul>' if downloads else '')
                   + '<p class="note">Not peer reviewed</p></aside></div>'
                   + discussion(work, snapshots.get(work["work_id"]), config["repository"]))
        for route in ["abs/" + wid + "v" + number] + (["abs/" + wid] if latest else []):
            page(route, meta["title"], content)
            shutil.copyfile(folder / "proof.json", output / route / "proof.json")
            shutil.copyfile(folder / "paper.md", output / route / "paper.md")
            write_json(output / route / "metadata.json", {**record, "author_homepages": links})
        records[pid] = record
    catalog_entries = []
    for work in registry:
        version = work["versions"][-1]
        pid, wid = version["content_hash"], work["work_id"]
        require(pid in records, "archive_conflict", "A work references a missing manuscript.")
        meta = records[pid]["metadata"]
        catalog_entries.append({"paper_id": pid, "content_hash": pid, "work_id": wid, "version": version["version"],
                                "title": meta["title"], "abstract": meta["abstract"], "authors": meta["authors"],
                                "submitter": records[pid]["submitter"],
                                "author_homepages": version.get("author_homepages", []), "received_at": work["created_at"],
                                "revised_at": version["received_at"], "primary_category": meta.get("primary_category"),
                                "secondary_categories": meta.get("secondary_categories", []), "tags": meta.get("tags", []),
                                "declared_ai": ai_label(meta), "url": base + "abs/" + wid[3:] + "/",
                                "markdown_url": base + "md/" + wid[3:] + ".md",
                                "reader_url": base + "md/" + wid[3:] + "/"})
        write_json(output / "works" / (wid[3:] + ".json"), work)
    catalog_entries.sort(key=lambda e: (e["received_at"], e["work_id"]), reverse=True)
    write_json(output / "index.json", {"papers": catalog_entries})
    write_json(output / "works/index.json", {"works": registry})
    if social is not None:
        write_json(output / "social.json", social)
    def listing(route, title, items):
        for number in range(1, max(1, math.ceil(len(items) / PAGE_SIZE)) + 1):
            tools = pagination(len(items), number, route, base)
            content = ('<div class="breadcrumb"><a href="' + base + '">Subjects</a></div>' if route != "recent" else '')
            content += '<h1>' + esc(title) + '</h1>'
            content += tools + (rows(items[(number - 1) * PAGE_SIZE:number * PAGE_SIZE], base) if items else '<p class="empty">No preprints in this subject yet.</p>') + tools
            page(route + ('/page/' + str(number) if number > 1 else ''), title, content)
    listing("recent", "Recent Submissions", catalog_entries)
    catalog = taxonomy.load(root, read_json(root / "taxonomy/latest.json")["taxonomy_hash"])
    groups = []
    priority = {"cs": 0, "math": 1, "physics": 2}
    for group in sorted(catalog["groups"], key=lambda group: (priority.get(group["code"], 3), group["name"])):
        subjects = []
        for category in (c for c in catalog["categories"] if c["group"] == group["code"]):
            code = category["code"]
            items = [e for e in catalog_entries if code in [e["primary_category"], *e["secondary_categories"]]]
            subjects.append('<li class="category-row"><a href="' + base + 'categories/' + code + '/"><span class="subject-code">' + esc(code) + '</span><span>' + esc(category["name"]) + '</span><span class="subject-count">' + str(len(items)) + '</span></a></li>')
            listing("categories/" + code, code + " - " + category["name"], items)
        groups.append('<section class="subject-group" data-subject-group="' + esc(group["code"]) + '"><h2>' + esc(group["name"]) + '</h2><ul>' + ''.join(subjects) + '</ul></section>')
    count_label = str(len(catalog_entries)) + (' preprint' if len(catalog_entries) == 1 else ' preprints')
    home = ('<div class="catalog-heading"><div><h1>Browse Subjects</h1><p class="muted">' + count_label + ' / ' + str(len(catalog["categories"])) + ' subjects</p></div></div>'
            + '<label class="sr-only" for="category-search">Filter subjects</label><input class="subject-filter" id="category-search" type="search" placeholder="Find a subject" autocomplete="off">'
            + '<div class="subject-directory">' + ''.join(groups) + '</div><p id="no-subjects" hidden>No matching subjects.</p>')
    page("", "Markdownxiv", home, True)
    page("categories", "Subjects", home, True)
    listing("categories/unclassified", "Unclassified", [e for e in catalog_entries if not e["primary_category"]])
    page("search", "Search", '<h1>Search</h1><div id="search-results" data-index="' + base + 'index.json" aria-live="polite"><p>Loading results...</p></div><noscript>Search requires JavaScript. <a href="' + base + 'recent/">Browse all papers</a>.</noscript>', True)
    shutil.copytree(root / "taxonomy", output / "taxonomy", dirs_exist_ok=True)
    return sorted(records)
