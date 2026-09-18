"""Scholarly Markdown structure and offline MathJax rendering of untrusted text."""
import html
import json
import multiprocessing
import os
import re
import resource
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

from .codec import sha
from .errors import require

RENDERER = Path(__file__).resolve().parents[2] / "renderer"
MAX_FORMULAS = 2000
MAX_FORMULA = 16000


def _plain(tokens):
    return "".join(" " if token.type in ("softbreak", "hardbreak") else
                   token.content if token.type in ("text", "code_inline", "math_inline", "image") else ""
                   for token in tokens or [])


def parse_document(text, image_urls=None):
    from markdown_it.token import Token
    from mdit_py_plugins.amsmath import amsmath_plugin
    from mdit_py_plugins.footnote import footnote_plugin
    from mdit_py_plugins.texmath import texmath_plugin
    from .site import markdown_parser

    md = markdown_parser(image_urls)
    md.use(texmath_plugin, delimiters="brackets")
    md.use(amsmath_plugin)
    md.use(footnote_plugin)
    formulas, headings, used = [], [], set()
    def math(tokens, index, options, env):
        token = tokens[index]
        expression = token.content.strip()
        display = token.type != "math_inline"
        if len(expression) > MAX_FORMULA or len(formulas) >= MAX_FORMULAS:
            return '<code class="math-fallback">' + html.escape(expression) + '</code>'
        if token.type == "math_block_eqno":
            # The bracket plugin's optional number is data inside a TeX tag.
            if re.fullmatch(r"[A-Za-z0-9 .()_-]{1,80}", token.info):
                expression += r"\tag{" + token.info + "}"
        index = len(formulas)
        formulas.append({"tex": expression, "display": display})
        return '<!--reader-math-' + str(index) + '-->'
    for kind in ("math_inline", "math_inline_double", "math_block", "math_block_label", "math_block_eqno", "amsmath"):
        md.renderer.rules[kind] = math
    tokens = md.parse(text, env := {})
    has_title = False
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            inline = tokens[index + 1]
            label = _plain(inline.children).strip()
            slug = re.sub(r"[^\w\s-]", "", unicodedata.normalize("NFKC", label).lower())
            slug = "section-" + (re.sub(r"[\s_-]+", "-", slug).strip("-")[:96] or "heading")
            anchor, count = slug, 1
            while anchor in used:
                count += 1
                anchor = slug + "-" + str(count)
            used.add(anchor)
            token.attrSet("id", anchor)
            level = int(token.tag[1])
            has_title |= level == 1
            if level <= 3:
                headings.append({"id": anchor, "title": label, "level": level})
            link = Token("html_inline", "", 0)
            link.content = ('<a class="heading-anchor" href="#' + html.escape(anchor, quote=True)
                            + '" aria-label="Link to this section" title="Link to this section">#</a>')
            inline.children.append(link)
        if token.type in ("th_open", "td_open") and token.attrGet("style"):
            alignment = token.attrGet("style")
            token.attrs.pop("style", None)
            if alignment in ("text-align:left", "text-align:center", "text-align:right"):
                token.attrSet("class", "align-" + alignment.split(":")[1])
    def table_open(*_):
        return '<div class="table-scroll" tabindex="0" role="region" aria-label="Table"><table>\n'
    md.renderer.rules["table_open"] = table_open
    md.renderer.rules["table_close"] = lambda *_: '</table></div>\n'
    md.renderer.rules["footnote_block_open"] = lambda *_: (
        '<section class="footnotes" aria-labelledby="reader-notes"><h2 id="reader-notes">Notes</h2><ol class="footnotes-list">')
    original_ref = md.renderer.rules["footnote_ref"]
    original_backref = md.renderer.rules["footnote_anchor"]
    md.renderer.rules["footnote_ref"] = lambda *args: original_ref(*args).replace('<a ', '<a role="doc-noteref" aria-label="Read footnote" ')
    md.renderer.rules["footnote_anchor"] = lambda *args: original_backref(*args).replace('<a ', '<a aria-label="Back to footnote reference" ')
    if env.get("footnotes", {}).get("list"):
        headings.append({"id": "reader-notes", "title": "Notes", "level": 2})
    return {"html": md.renderer.render(tokens, md.options, env), "headings": headings,
            "formulas": formulas, "has_title": has_title, "css": ""}


def _parse_worker(connection, text, image_urls):
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
        connection.send(parse_document(text, image_urls))
    except BaseException:
        connection.send(None)
    finally:
        connection.close()


def _node_limits():
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 * 1024 * 1024, 2 * 1024 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (28_000_000, 28_000_000))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def typeset(formulas):
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        subprocess.run(["node", "--jitless", "--no-expose-wasm", "--max-old-space-size=256", str(RENDERER / "mathjax.cjs")],
                                input=json.dumps({"formulas": formulas}, ensure_ascii=True).encode(),
                                stdout=output, stderr=errors, timeout=25, check=True, preexec_fn=_node_limits,
                                env={"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"})
        output.seek(0)
        rendered = json.loads(output.read(28_000_001))
    if len(rendered["formulas"]) != len(formulas):
        raise ValueError("MathJax formula count mismatch")
    return rendered


def render_reader(text, image_urls=None):
    fallback = {"html": '<pre class="render-fallback">' + html.escape(text) + '</pre>',
                "headings": [], "formulas": [], "has_title": False, "css": ""}
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_parse_worker, args=(child, text, image_urls))
    process.start()
    child.close()
    try:
        if not parent.poll(10):
            return fallback
        try:
            document = parent.recv()
        except EOFError:
            return fallback
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=1)
        if process.is_alive():
            process.kill()
            process.join()
        process.close()
        parent.close()
    if document is None:
        return fallback
    formulas = document.pop("formulas")
    if not formulas:
        return document
    try:
        rendered = typeset(formulas)
        document["css"] = rendered["css"]
        replacements = rendered["formulas"]
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        replacements = ['<code class="math-fallback">' + html.escape(f["tex"]) + '</code>' for f in formulas]
    def replace(match):
        index = int(match.group(1))
        formula = formulas[index]
        if formula["display"]:
            return '<div class="display-math" tabindex="0" role="group" aria-label="Equation">' + replacements[index] + '</div>'
        return '<span class="inline-math">' + replacements[index] + '</span>'
    document["html"] = re.sub(r"<!--reader-math-([0-9]+)-->", replace, document["html"])
    return document


def install_assets(output):
    modules = RENDERER / "node_modules"
    font = modules / "@mathjax/mathjax-newcm-font/chtml/woff2"
    serif = modules / "@fontsource/source-serif-4"
    require(shutil.which("node") and font.is_dir() and serif.is_dir(), "renderer_unavailable",
            "Install Node.js 22+ and run npm ci --ignore-scripts --prefix renderer before building the site.")
    target = Path(output) / "assets"
    shutil.copytree(font, target / "fonts/mathjax", dirs_exist_ok=True)
    shutil.copytree(serif / "files", target / "fonts/serif", dirs_exist_ok=True,
                    ignore=lambda _directory, names: [name for name in names if not re.search(r"-(?:400|600)-(?:normal|italic)\.woff2?$", name)])
    css = "\n".join((serif / name).read_text().replace("./files/", "fonts/serif/")
                    for name in ("400.css", "400-italic.css", "600.css", "600-italic.css"))
    (target / "reader-fonts.css").write_text(css)
    shutil.copyfile(serif / "LICENSE", target / "fonts/serif/LICENSE.txt")
    shutil.copyfile(modules / "@mathjax/src/LICENSE", target / "fonts/mathjax/LICENSE-MATHJAX.txt")


def math_stylesheet(document, output, base):
    if not document["css"]:
        return None
    raw = document["css"].encode()
    name = sha(raw) + ".css"
    target = Path(output) / "assets/math" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(raw)
    return base + "assets/math/" + name


def contents(headings):
    selected = [heading for heading in headings if heading["level"] in (2, 3)]
    if not selected:
        return ""
    links = ''.join('<li class="toc-level-' + str(h["level"]) + '"><a href="#'
                    + html.escape(h["id"], quote=True) + '">' + html.escape(h["title"]) + '</a></li>' for h in selected)
    return ('<aside class="reader-outline"><details class="reader-toc" open><summary>Contents</summary>'
            '<nav aria-label="Table of contents"><ol>' + links + '</ol></nav></details></aside>')
