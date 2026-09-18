"use strict";

const fs = require("node:fs");
const crypto = require("node:crypto");
const path = require("node:path");
const {mathjax} = require("@mathjax/src/js/mathjax.js");
const {TeX} = require("@mathjax/src/js/input/tex.js");
const {CHTML} = require("@mathjax/src/js/output/chtml.js");
const {liteAdaptor} = require("@mathjax/src/js/adaptors/liteAdaptor.js");
const {RegisterHTMLHandler} = require("@mathjax/src/js/handlers/html.js");
const {SafeHandler} = require("@mathjax/src/js/ui/safe/SafeHandler.js");
const {AssistiveMmlHandler} = require("@mathjax/src/js/a11y/assistive-mml.js");
require("@mathjax/src/js/input/tex/ams/AmsConfiguration.js");
require("@mathjax/src/js/input/tex/newcommand/NewcommandConfiguration.js");
require("@mathjax/src/js/input/tex/mathtools/MathtoolsConfiguration.js");
require("@mathjax/src/js/input/tex/boldsymbol/BoldsymbolConfiguration.js");
require("@mathjax/src/js/input/tex/tagformat/TagFormatConfiguration.js");

const escape = value => value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");

async function main() {
  const request = JSON.parse(fs.readFileSync(0, "utf8"));
  if (!Array.isArray(request.formulas) || request.formulas.length > 2000) throw Error("Formula limit");
  const adaptor = liteAdaptor();
  AssistiveMmlHandler(SafeHandler(RegisterHTMLHandler(adaptor)));
  const fontRoot = path.dirname(require.resolve("@mathjax/mathjax-newcm-font/cjs/chtml.js"));
  mathjax.asyncLoad = file => {
    const resolved = file.startsWith("@mathjax/mathjax-newcm-font/js/") ? require.resolve(file) : path.resolve(file);
    if (!resolved.startsWith(fontRoot + path.sep)) throw Error("Unsupported font extension");
    return Promise.resolve(require(resolved));
  };
  const tex = new TeX({
    packages: ["base", "ams", "newcommand", "mathtools", "boldsymbol", "tagformat"],
    inlineMath: [["\\(", "\\)"]], displayMath: [["\\[", "\\]"]],
    tags: "ams", useLabelIds: true, maxBuffer: 16 * 1024, maxMacros: 1000,
    tagformat: {id: label => "mjx-eqn-" + crypto.createHash("sha256").update(label).digest("hex").slice(0, 20)},
  });
  const chtml = new CHTML({fontURL: "../fonts/mathjax", adaptiveCSS: true, displayOverflow: "scroll"});
  const source = request.formulas.map((formula, index) => {
    if (typeof formula.tex !== "string" || formula.tex.length > 16000 || typeof formula.display !== "boolean") throw Error("Invalid formula");
    return `<div id="formula-${index}">${formula.display ? "\\[" : "\\("}${escape(formula.tex)}${formula.display ? "\\]" : "\\)"}</div>`;
  }).join("");
  const document = mathjax.document(source, {InputJax: tex, OutputJax: chtml,
    safeOptions: {allow: {URLs: "safe", classes: "none", cssIDs: "safe", styles: "none"}},
  });
  document.safe.filterMethods.filterURL = (_safe, url) => /^#mjx-eqn-[a-f0-9]{20}$/.test(url) ? url : null;
  await mathjax.handleRetriesFor(() => document.render());
  const formulas = adaptor.childNodes(adaptor.body(document.document)).filter(node => adaptor.kind(node) === "div");
  const styles = new Map();
  const allowedMathML = new Set(["math", "semantics", "annotation", "mrow", "mi", "mn", "mo", "mtext", "mspace",
    "msup", "msub", "msubsup", "mfrac", "msqrt", "mroot", "mover", "munder", "munderover", "mtable", "mtr",
    "mlabeledtr", "mtd", "menclose", "mstyle", "mpadded", "mphantom", "mmultiscripts", "mprescripts", "none", "mfenced"]);
  function clean(node) {
    const kind = adaptor.kind(node);
    if (kind === "#text") return;
    if (kind !== "div" && kind !== "a" && !/^mjx-[A-Za-z-]+$/.test(kind) && !allowedMathML.has(kind)) throw Error("Unexpected mathematical markup: " + kind);
    // The lite adaptor leaves some tagged-row heights unresolved; use intrinsic layout.
    if (/NaN|Infinity/.test(adaptor.getStyle(node, "height") || "")) adaptor.setStyle(node, "height", "auto");
    for (const {name, value} of adaptor.allAttributes(node)) {
      if (name === "style") {
        const key = "mjx-s-" + crypto.createHash("sha256").update(value).digest("hex").slice(0, 20);
        styles.set(key, value);
        adaptor.removeAttribute(node, name);
        adaptor.addClass(node, key);
      } else if (name.startsWith("on") || name === "src" || name === "data-latex" ||
                 (name === "href" && !/^#mjx-eqn-[a-f0-9]{20}$/.test(value))) {
        adaptor.removeAttribute(node, name);
      }
    }
    for (const child of adaptor.childNodes(node)) clean(child);
  }
  formulas.forEach(clean);
  const css = adaptor.textContent(chtml.styleSheet(document)) + "\n" +
    [...styles].map(([name, style]) => `.${name}{${style}}`).join("\n");
  const rendered = formulas.map(node => adaptor.innerHTML(node));
  if (Buffer.byteLength(JSON.stringify(rendered)) + Buffer.byteLength(css) > 24_000_000) throw Error("Output limit");
  process.stdout.write(JSON.stringify({formulas: rendered, css}));
}

main().catch(error => { process.stderr.write("MathJax render failed: " + error.message + "\n"); process.exitCode = 1; });
