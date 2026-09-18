import re
import subprocess
import unittest
from unittest.mock import patch

from agent_preprints.reader import contents, parse_document, render_reader, typeset


class ReaderRenderingTests(unittest.TestCase):
    def test_headings_footnotes_and_table_alignment_have_stable_safe_anchors(self):
        source = ("# Title\n\n## A & B\n\nText[^note].\n\n## A & B\n\n### Details\n\n"
                  "| Left | Right |\n| :--- | ---: |\n| a | b |\n\n[^note]: A footnote.\n")
        document = parse_document(source)
        self.assertEqual([h["id"] for h in document["headings"]],
                         ["section-title", "section-a-b", "section-a-b-2", "section-details", "reader-notes"])
        rendered = document["html"]
        self.assertIn('role="doc-noteref"', rendered)
        self.assertIn('aria-label="Back to footnote reference"', rendered)
        self.assertIn('href="#fn1"', rendered)
        self.assertIn('id="fn1"', rendered)
        self.assertIn('class="align-right"', rendered)
        self.assertNotIn('style=', rendered)
        self.assertIn('href="#section-a-b-2"', contents(document["headings"]))
        self.assertIn('A &amp; B', contents(document["headings"]))

    def test_markdown_parser_preserves_code_and_collects_common_math_delimiters(self):
        source = r"""# Mathematics

Inline $x^2$ and \(y^2\).

$$z^2$$

\[a=b\]

\begin{align}
a&=b\\
c&=d
\end{align}

```text
$not_math$ \(not_math\)
```
"""
        document = parse_document(source)
        self.assertEqual([f["display"] for f in document["formulas"]], [False, False, True, True, True])
        self.assertIn("$not_math$", document["html"])
        self.assertIn("\\(not_math\\)", document["html"])
        self.assertEqual(len(document["formulas"]), 5)

    def test_mathjax_pretypesets_equations_references_and_accessible_mathml(self):
        document = render_reader(r"""## Formula

Reference \(\eqref{eq:first}\).

$$\sum_{i=1}^n i=\frac{n(n+1)}2\tag{1}\label{eq:first}$$

\begin{align*}
a&=b+c\\
d&=e
\end{align*}
""")
        result = document["html"]
        self.assertEqual(result.count('<mjx-container '), 3)
        self.assertEqual(result.count('<mjx-assistive-mml '), 3)
        self.assertNotIn('math-fallback', result)
        self.assertNotIn('mjx-merror', result)
        self.assertNotRegex(result, r'\sstyle=')
        target = re.search(r'<mjx-mtd id="(mjx-eqn-[a-f0-9]+)"', result).group(1)
        self.assertIn('href="#' + target + '"', result)
        self.assertIn('../fonts/mathjax/', document["css"])
        self.assertNotIn('https:', document["css"])
        self.assertIn('.mjx-s-', document["css"])
        self.assertNotIn('NaN', document["css"])

    def test_untrusted_tex_html_urls_and_input_commands_never_become_active_content(self):
        source = r"""# <script>bad()</script>

![remote](https://tracker.example/image.png)

$\href{javascript:alert(1)}{x}$

$\require{https://tracker.example/package}$

$\style{background:url(https://tracker.example/x)}{y}$

<img src=x onerror=bad()>
"""
        document = render_reader(source)
        result = document["html"]
        self.assertNotIn('<script', result)
        self.assertNotIn('<img', result)
        self.assertNotIn('href="javascript:', result)
        self.assertNotIn('src="https:', result)
        self.assertNotIn('style=', result)
        self.assertNotIn('tracker.example', document["css"])
        self.assertIn('&lt;script&gt;', result)

    def test_typesetting_timeout_preserves_text_and_math_source(self):
        with patch("agent_preprints.reader.typeset", side_effect=subprocess.TimeoutExpired("node", 25)):
            document = render_reader("# A title\n\nStill readable.\n\n$x^2$\n")
        self.assertIn('Still readable.', document["html"])
        self.assertIn('<code class="math-fallback">x^2</code>', document["html"])
        self.assertEqual(document["css"], "")

    def test_excessive_math_remains_escaped_without_entering_the_node_worker(self):
        document = parse_document("$$" + "x" * 16001 + "$$\n")
        self.assertEqual(document["formulas"], [])
        self.assertIn('math-fallback', document["html"])

    def test_extended_font_data_is_loaded_only_from_the_pinned_package(self):
        result = typeset([{"tex": r"\oiiint+\mathfrak{A}+\mathbb{R}", "display": True}])
        self.assertIn('<mjx-container ', result["formulas"][0])
        self.assertNotIn('mjx-merror', result["formulas"][0])


if __name__ == "__main__":
    unittest.main()
