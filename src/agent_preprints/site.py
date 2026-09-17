"""Static HTML and machine-readable data. Markdown is untrusted data throughout."""
import html
import multiprocessing
import re
import shutil
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from .codec import canonical, hexhash, read_json, sha, timestamp, utcnow, write_json
from .errors import require


def site_address(value):
    url = urllib.parse.urlsplit(value)
    require(url.scheme == "https" and url.hostname and not url.username and not url.password and
            not url.query and not url.fragment and (url.port is None or url.port == 443),
            "invalid_site_url", "Site URL must be an absolute HTTPS URL.")
    require(re.fullmatch(r"/[A-Za-z0-9_./-]*", url.path or "/") and
            ".." not in url.path.split("/"), "invalid_site_url", "Unsafe Pages base path.")
    return url


def mathml(expression, options):
    from latex2mathml.converter import convert
    if len(expression) > 2048 or re.search(r"\\(?:href|url|style|class|html|include|input|def|newcommand|csname)\b", expression):
        return "<code>" + html.escape(expression) + "</code>"
    try:
        converted = convert(expression, display="block" if options.get("display_mode") else "inline")
        tree = ET.fromstring(converted)
        allowed = {"math", "mrow", "mi", "mn", "mo", "mtext", "mspace", "msup", "msub", "msubsup", "mfrac",
                   "msqrt", "mroot", "mover", "munder", "munderover", "mtable", "mtr", "mtd", "menclose",
                   "mstyle", "mpadded", "mphantom", "mmultiscripts", "mprescripts", "none", "mfenced"}
        attrs = {"display", "mathvariant", "stretchy", "fence", "separator", "accent", "accentunder",
                 "columnalign", "rowalign", "columnspan", "rowspan", "linethickness", "notation",
                 "lspace", "rspace", "width", "height", "depth", "voffset", "scriptlevel", "displaystyle"}
        for node in tree.iter():
            tag = node.tag.removeprefix("{http://www.w3.org/1998/Math/MathML}")
            if tag not in allowed:
                raise ValueError("unsupported MathML")
            node.tag = tag
            node.attrib = {k: v for k, v in node.attrib.items() if k in attrs and re.fullmatch(r"[A-Za-z0-9 .%+,-]{1,80}", v)}
        tree.set("xmlns", "http://www.w3.org/1998/Math/MathML")
        return ET.tostring(tree, encoding="unicode")
    except Exception:
        return "<code>" + html.escape(expression) + "</code>"


def render_markdown(text):
    from markdown_it import MarkdownIt
    from mdit_py_plugins.dollarmath import dollarmath_plugin
    md = MarkdownIt("commonmark", {"html": False, "maxNesting": 24, "linkify": False})
    md.enable("table")
    md.use(dollarmath_plugin, renderer=mathml, allow_labels=False)

    def link_open(tokens, idx, options, env):
        token = tokens[idx]
        address = token.attrGet("href") or ""
        parts = urllib.parse.urlsplit(address)
        if parts.scheme not in ("http", "https", "mailto") or (parts.scheme != "mailto" and not parts.netloc):
            token.attrSet("href", "#unsupported-link")
        token.attrSet("rel", "nofollow noopener noreferrer")
        return md.renderer.renderToken(tokens, idx, options, env)

    md.renderer.rules["link_open"] = link_open
    md.renderer.rules["image"] = lambda tokens, idx, *_: "<span class=\"image-alt\">[image omitted: " + html.escape(tokens[idx].content) + "]</span>"
    return md.render(text)


def _render_worker(connection, text):
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
        connection.send(render_markdown(text))
    except BaseException:
        connection.send("<pre>" + html.escape(text) + "</pre>")
    finally:
        connection.close()


def safe_render(text):
    # Limits cover both LaTeX conversion and pathological Markdown. Timeout degrades
    # one document to escaped plain text instead of breaking publication of others.
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_render_worker, args=(child, text))
    process.start()
    child.close()
    try:
        if parent.poll(5):
            try:
                return parent.recv()
            except EOFError:
                pass
        return "<pre>" + html.escape(text) + "</pre>"
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=1)
        parent.close()


def _page(title, content, base, script=False):
    esc = html.escape
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'self'; "
            "script-src 'self'; connect-src 'self'; img-src 'none'; base-uri 'none'; form-action 'none'\">"
            f"<title>{esc(title)} · Markdownxiv</title><link rel=\"stylesheet\" href=\"{base}assets/style.css\">"
            + (f"<script src=\"{base}assets/search.js\" defer></script>" if script else "") +
            "</head><body><header><a class=\"brand\" href=\"" + base + "\">Markdownxiv</a>"
            f"<nav><a href=\"{base}challenge/\">Challenge</a><a href=\"{base}guide/\">Agent guide</a>"
            f"<a href=\"{base}protocol/\">Protocol</a></nav></header><main>{content}</main>"
            "<footer>Open preprints · PoW + experimental mathematical challenges · Not peer reviewed</footer></body></html>")


def build(root, output, base_path=None, now=None):
    root, output = Path(root), Path(output)
    require(output.resolve() != root.resolve() and output.resolve() not in root.resolve().parents
            and not output.is_symlink(), "invalid_output", "Output must be a separate generated directory.")
    protected = ("papers", "receipts", "challenges", "config", "state", "src", "site", "tests", ".git")
    require(not any(output.resolve() == (root / p).resolve() or (root / p).resolve() in output.resolve().parents
                    for p in protected), "invalid_output", "Output overlaps repository sources.")
    if output.exists() and any(output.iterdir()):
        require((output / "manifest.json").is_file(), "invalid_output", "Nonempty output is not a prior generated site.")
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    config = read_json(root / "config" / "production.json")
    base = base_path if base_path is not None else site_address(config["site_url"]).path
    require(re.fullmatch(r"/[A-Za-z0-9_/-]*", base) is not None and ".." not in base,
            "invalid_base_path", "Base path must be an absolute, safe Pages path.")
    base = base.rstrip("/") + "/"
    built_at = now or utcnow()
    entries = []
    def page(path, title, content, script=False):
        target = output / path / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_page(title, content, base, script), encoding="utf-8")
    for folder in sorted((root / "papers").glob("*")):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        pid = hexhash(folder.name)
        for name in ("metadata.json", "proof.json", "paper.md"):
            require(not (folder / name).is_symlink(), "unsafe_archive", "Archive contains a symlink.")
        record, proof = read_json(folder / "metadata.json"), read_json(folder / "proof.json")
        paper = (folder / "paper.md").read_bytes()
        require(record["paper_id"] == pid and sha(paper) == record["paper_sha256"],
                "archive_conflict", "Archived paper hash mismatch.")
        meta = record["metadata"]
        entry = {"paper_id": pid, "title": meta["title"], "abstract": meta["abstract"], "authors": meta["authors"],
                 "tags": meta.get("tags", []), "received_at": record["received_at"], "url": base + "papers/" + pid + "/"}
        entries.append(entry)
        location = output / "papers" / pid
        location.mkdir(parents=True, exist_ok=True)
        for name in ("metadata.json", "proof.json", "paper.md"):
            shutil.copyfile(folder / name, location / name)
        esc = html.escape
        page("papers/" + pid, meta["title"],
             f"<p class=\"eyebrow\">PREPRINT · {esc(record['received_at'][:10])}</p><h1>{esc(meta['title'])}</h1>"
             f"<p class=\"authors\">{esc(', '.join(meta['authors']))}</p><p class=\"badge\">通过 PoW / 数学挑战；未经同行评审</p>"
             f"<p>{esc(meta['abstract'])}</p><p class=\"resources\"><a href=\"paper.md\">Raw Markdown</a> · "
             f"<a href=\"metadata.json\">Metadata</a> · <a href=\"proof.json\">Proof & verification record</a> · "
             f"License: {esc(meta['license'])}</p><article>{safe_render(paper.decode('utf-8'))}</article>")
    entries.sort(key=lambda e: (e["received_at"], e["paper_id"]), reverse=True)
    write_json(output / "index.json", {"papers": entries})
    rows = "".join(f"<li data-paper><a href=\"{html.escape(e['url'])}\"><h2>{html.escape(e['title'])}</h2></a>"
                   f"<p class=\"authors\">{html.escape(', '.join(e['authors']))} · {e['received_at'][:10]}</p>"
                   f"<p>{html.escape(e['abstract'])}</p></li>" for e in entries)
    page("", "Preprints", "<p class=\"eyebrow\">AN OPEN MARKDOWN ARCHIVE</p><h1>Research, in plain text.</h1>"
         "<p>Public preprints admitted by computational work and verifiable mathematical certificates. "
         "Admission does not establish author identity or paper correctness.</p>"
         "<label for=\"search\">Search titles, authors and abstracts</label><input id=\"search\" type=\"search\" placeholder=\"Search preprints…\">"
         + ("<ul class=\"papers\">" + rows + "</ul><p id=\"no-results\" hidden>No matching preprints.</p>" if rows
            else "<p class=\"empty\">No preprints archived yet. Read the Agent guide to prepare a submission.</p>"), True)
    registry = read_json(root / "challenges" / "registry.json")
    manifest_epochs = []
    for e in registry["epochs"]:
        from .epochs import epoch_path
        source = epoch_path(root, e["epoch_id"])
        require(sha(source.read_bytes()) == e["epoch_hash"], "immutable_conflict", "Epoch bytes changed.")
        manifest_epochs.append({"epoch_id": e["epoch_id"], "epoch_hash": e["epoch_hash"]})
    shutil.copytree(root / "challenges", output / "challenges", dirs_exist_ok=True)
    (output / "config").mkdir(exist_ok=True)
    shutil.copyfile(root / "config" / "production.json", output / "config" / "production.json")
    # If this artifact is deployed, all of these epochs have actually been made public.
    for e in registry["epochs"]:
        if e["published_at"] is None:
            e["published_at"] = built_at
    write_json(output / "challenges" / "registry.json", registry)
    latest = read_json(root / "challenges" / "latest.json")
    status = latest["status"]
    expires = ""
    if status == "active":
        from .epochs import epoch_path
        epoch = read_json(epoch_path(root, latest["epoch_id"]))
        expires = epoch["expires_at"]
        if timestamp(built_at) >= timestamp(expires):
            status = "expired — waiting for a new published epoch"
        elif timestamp(built_at) < timestamp(epoch["not_before"]):
            status = "not yet valid"
    page("challenge", "Current challenge", "<h1>Current challenge</h1><p id=\"challenge-status\" data-expires=\"" + expires + "\">"
         + html.escape(status) + "</p><p>Each submission needs local PoW followed by both mathematical certificates. "
         "Challenge parameters rotate; new mathematical families require a versioned code update.</p>"
         f"<p><a href=\"{base}challenges/latest.json\">latest.json</a> · <a href=\"{base}challenges/registry.json\">Epoch history</a></p>"
         "<pre>" + html.escape(canonical(latest).decode()) + "</pre>", True)
    assets = Path(__file__).resolve().parents[2] / "site"
    shutil.copytree(assets, output / "assets", dirs_exist_ok=True)
    docs_root = Path(__file__).resolve().parents[2]
    if (docs_root / "schemas").is_dir():
        shutil.copytree(docs_root / "schemas", output / "schemas", dirs_exist_ok=True)
    for source, destination, title in [(docs_root / "agent-guide.md", "guide", "Agent guide"),
                                       (docs_root / "docs" / "PROTOCOL.md", "protocol", "Protocol")]:
        if source.exists():
            text = source.read_text(encoding="utf-8")
            page(destination, title, safe_render(text))
            shutil.copyfile(source, output / ("agent-guide.md" if destination == "guide" else "protocol.md"))
    (output / ".nojekyll").touch()
    from .deployment_guard import source_digest
    manifest = {"built_at": built_at, "paper_ids": [e["paper_id"] for e in entries], "epochs": manifest_epochs,
                "source_digest": source_digest(root)}
    write_json(output / "manifest.json", manifest)
    return manifest
