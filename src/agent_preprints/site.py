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


def render_markdown(text, image_urls=None, link_base=None):
    from markdown_it import MarkdownIt
    from mdit_py_plugins.dollarmath import dollarmath_plugin
    md = MarkdownIt("commonmark", {"html": False, "maxNesting": 24, "linkify": False})
    md.enable("table")
    md.use(dollarmath_plugin, renderer=mathml, allow_labels=False)

    def link_open(tokens, idx, options, env):
        token = tokens[idx]
        address = token.attrGet("href") or ""
        parts = urllib.parse.urlsplit(address)
        if link_base and not parts.scheme and not parts.netloc and not address.startswith("/"):
            address = urllib.parse.urljoin(link_base, address)
            token.attrSet("href", address)
            parts = urllib.parse.urlsplit(address)
        local = not parts.scheme and not parts.netloc and re.fullmatch(r"[A-Za-z0-9_./#-]+", address) is not None
        if not local and (parts.scheme not in ("http", "https", "mailto") or (parts.scheme != "mailto" and not parts.netloc)):
            token.attrSet("href", "#unsupported-link")
        token.attrSet("rel", "nofollow noopener noreferrer")
        return md.renderer.renderToken(tokens, idx, options, env)

    md.renderer.rules["link_open"] = link_open
    def image(tokens, idx, *_):
        token = tokens[idx]
        address = (image_urls or {}).get(token.attrGet("src"))
        if address and re.fullmatch(r"/[A-Za-z0-9_/-]+/media/[0-9a-f]{64}\.(?:png|jpg|webp)|/media/[0-9a-f]{64}\.(?:png|jpg|webp)", address):
            return '<img loading="lazy" decoding="async" src="' + address + '" alt="' + html.escape(token.content, quote=True) + '">'
        return "<span class=\"image-alt\">[image omitted: " + html.escape(token.content) + "]</span>"
    md.renderer.rules["image"] = image
    return md.render(text)


def _render_worker(connection, text, image_urls, link_base):
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
        connection.send(render_markdown(text, image_urls, link_base))
    except BaseException:
        connection.send("<pre>" + html.escape(text) + "</pre>")
    finally:
        connection.close()


def safe_render(text, image_urls=None, link_base=None):
    # Limits cover both LaTeX conversion and pathological Markdown. Timeout degrades
    # one document to escaped plain text instead of breaking publication of others.
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_render_worker, args=(child, text, image_urls, link_base))
    process.start()
    child.close()
    try:
        if parent.poll(10):
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
            "script-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; form-action 'self'\">"
            f"<title>{esc(title)} · Markdownxiv</title><link rel=\"stylesheet\" href=\"{base}assets/style.css\">"
            + (f"<script src=\"{base}assets/search.js\" defer></script>" if script else "") +
            f'<link rel="icon" href="{base}assets/mark.svg" type="image/svg+xml"></head><body>'
            '<a class="skip-link" href="#content">Skip to content</a><header><div class="header-inner">'
            f'<a class="brand" href="{base}"><img src="{base}assets/mark.svg" width="38" height="38" alt="">Markdownxiv</a>'
            f'<form class="archive-search" role="search" action="{base}search/" method="get"><label class="sr-only" for="global-search">Search archive</label>'
            '<input id="global-search" name="q" type="search" placeholder="Search" required><button type="submit">Search</button></form></div>'
            f'<nav class="main-nav"><a href="{base}">Subjects</a><a href="{base}recent/">Recent</a><a href="{base}guide/">Submit / Agent guide</a>'
            f'<a href="{base}challenge/">Proof of Work</a><a href="{base}protocol/">Protocol</a></nav></header><main id="content">{content}</main>'
            '<footer><span>Markdownxiv</span><span>Open preprints / Not peer reviewed</span></footer></body></html>')


def build(root, output, base_path=None, now=None, social=None):
    root, output = Path(root), Path(output)
    require(output.resolve() != root.resolve() and output.resolve() not in root.resolve().parents
            and not output.is_symlink(), "invalid_output", "Output must be a separate generated directory.")
    protected = ("papers", "receipts", "challenges", "config", "state", "src", "site", "tests", ".git", "works", "assets", "taxonomy", "prompts")
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
    from . import PROTOCOL_V3
    if config.get("protocol") == PROTOCOL_V3:
        from .catalog import build_catalog
        paper_ids = build_catalog(root, output, base, page, config, social)
    else:
        from .site_papers import build_papers
        paper_ids = build_papers(root, output, base, page, safe_render, config, social)
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
    if (docs_root / "prompts").is_dir():
        shutil.copytree(docs_root / "prompts", output / "prompts", dirs_exist_ok=True)
    for source, destination, title in [(docs_root / "agent-guide.md", "guide", "Agent guide"),
                                       (docs_root / "docs" / "PROTOCOL.md", "protocol", "Protocol")]:
        if source.exists():
            text = source.read_text(encoding="utf-8")
            page(destination, title, safe_render(text, link_base=base))
            shutil.copyfile(source, output / ("agent-guide.md" if destination == "guide" else "protocol.md"))
    for source, target in (("PROTOCOL_V1.md", "protocol-v1.md"), ("PROTOCOL_V2.md", "protocol-v2.md"), ("AGENT_GUIDE_V1.md", "agent-guide-v1.md")):
        if (docs_root / "docs" / source).exists():
            shutil.copyfile(docs_root / "docs" / source, output / target)
    (output / ".nojekyll").touch()
    from .deployment_guard import source_digest
    manifest = {"built_at": built_at, "paper_ids": paper_ids, "epochs": manifest_epochs,
                "source_digest": source_digest(root)}
    write_json(output / "manifest.json", manifest)
    size = sum(p.stat().st_size for p in output.rglob("*") if p.is_file())
    require(size <= 900_000_000, "site_capacity", "Generated site exceeds the 900 MB operational budget; publication remains pending.")
    return manifest
