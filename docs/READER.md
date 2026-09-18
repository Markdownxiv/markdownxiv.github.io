# Human-readable manuscripts

The `md/YYMM.NNNNN[vN]/` routes are generated academic reading views. They retain
the manuscript text, including its title and byline; the toolbar provides the
version, abstract, raw source, discussion, latest version and printing. The raw
`.md` endpoints and archived proof bytes are not changed by reader upgrades.

## Markdown and mathematics

The reader uses Markdown-it CommonMark with tables and footnotes. Headings receive
stable, collision-free section IDs. Level-two and level-three headings form the
contents list. Footnotes have linked references and return links. Code blocks stay
literal, and table alignment is rendered with external CSS classes.

Math is explicitly delimited by `$...$`, `$$...$$`, `\(...\)` or `\[...\]`.
Standard AMS block environments are also accepted. MathJax 4.1.3 handles base TeX,
AMS, mathtools, bounded local macro definitions and bold symbols. Explicit tags and
labels work with `\tag`, `\label`, `\ref` and `\eqref` inside mathematics; references
can point forward. No mathematical meaning is guessed from ordinary prose.

MathJax emits static CHTML and assistive MathML at build time. Its generated styles
are externalized into a content-addressed CSS file, preserving a CSP without inline
styles or scripts. The site hosts New Computer Modern math fonts and Source Serif 4
text fonts. The browser does not load MathJax or third-party font services.

## Build and trust boundaries

Use Python 3.11+ and Node.js 22 or 24, then run:

```bash
npm ci --ignore-scripts --prefix renderer
preprints build --out _site
```

`renderer/package-lock.json` pins all renderer and font dependencies. CI and Pages
build jobs install them from the trusted checkout, with lifecycle scripts disabled.
The renderer files and lockfiles are included in the deployment source digest.
No Node installation is required to prepare or verify a submission.

Markdown parses in a separate process with an 8-second CPU limit and 512 MiB
address-space limit. MathJax reads a bounded JSON message on standard input, never
shell arguments or executable source from a manuscript. Its process has a 20-second
CPU limit, 25-second wall deadline, 256 MiB V8 heap limit, 2 GiB address-space limit,
and bounded output files. It inherits no GitHub credentials. Each document is
limited to 2,000 mathematical expressions of at most 16,000 characters each.

Only fixed TeX packages are registered. Dynamic loading is restricted to pinned
local font data; TeX cannot select a package, URL or filesystem path. MathJax's
safety filter disables user styles and classes and permits only generated internal
equation links. An additional output walk excludes non-mathematical active markup.
Manuscript HTML remains escaped and images must be verified archive assets.

A failed math batch leaves escaped TeX within the otherwise rendered document.
Oversized individual expressions also remain escaped. This never changes admission
or prevents access to the exact raw manuscript. Parser failures use a plain-text
fallback. Neither fallback claims successful mathematical typesetting.

## Reading and accessibility

Desktop has a sticky contents column; small screens have a collapsible contents
list. Native links and the entire static manuscript work without JavaScript.
Optional first-party JavaScript highlights the current section, collapses mobile
contents after navigation and enables the print button. Equations and tables scroll
locally on narrow screens. Print styles omit navigation and preserve the manuscript,
formulas and notes. Fonts and the Lucide print icon retain their upstream licenses.
