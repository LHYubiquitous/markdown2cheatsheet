import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from converter_core import convert_markdown
from markdown_normalizer import normalize_markdown
from template_presets import (
    DEFAULT_COLUMNS,
    DEFAULT_FONT_SIZE,
    DEFAULT_LINE_HEIGHT,
    resolve_template,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "adversarial_markdown.md"


class HtmlNode:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []

    def text(self):
        value = "".join(
            child.text() if isinstance(child, HtmlNode) else child
            for child in self.children
        )
        return re.sub(r"\s+", " ", value).strip()

    def find_all(self, tag):
        found = []
        for child in self.children:
            if not isinstance(child, HtmlNode):
                continue
            if child.tag == tag:
                found.append(child)
            found.extend(child.find_all(tag))
        return found


class HtmlTreeParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = HtmlNode("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = HtmlNode(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


class MarkdownNormalizerTests(unittest.TestCase):
    def test_inserts_missing_block_boundaries_but_preserves_fenced_code(self):
        source = (
            "Paragraph\n"
            "- first\n"
            "- second\n"
            "After list\n"
            "### Heading\n"
            "Before table\n"
            "| A | B |\n"
            "| --- | --- |\n"
            "| 1 | 2 |\n"
            "After table\n"
            "```markdown\n"
            "Paragraph\n"
            "- literal list\n"
            "| not | a table |\n"
            "| --- | --- |\n"
            "```\n"
        )

        normalized = normalize_markdown(source)

        self.assertIn("Paragraph\n\n- first", normalized)
        self.assertIn("- second\n\nAfter list", normalized)
        self.assertIn("After list\n\n### Heading", normalized)
        self.assertIn("Before table\n\n| A | B |", normalized)
        self.assertIn("| 1 | 2 |\n\nAfter table", normalized)
        self.assertIn(
            "```markdown\nParagraph\n- literal list\n| not | a table |\n| --- | --- |\n```",
            normalized,
        )

    def test_is_idempotent(self):
        source = FIXTURE.read_text(encoding="utf-8")
        once = normalize_markdown(source)
        self.assertEqual(normalize_markdown(once), once)

    def test_adds_boundaries_around_four_space_indented_fence_in_list(self):
        source = (
            "3. Administrator setup\n"
            "    Run these commands:\n"
            "    ```zsh\n"
            "    export USER=admin\n"
            "    read -s PASSWORD\n"
            "    ```\n"
            "    Continue after code.\n"
        )

        normalized = normalize_markdown(source)

        self.assertIn("Run these commands:\n\n    ```zsh", normalized)
        self.assertIn("    ```\n\n    Continue after code.", normalized)
        self.assertIn("    export USER=admin", normalized)

    def test_repairs_known_pandoc_mathml_incompatibilities_only_inside_math(self):
        source = (
            r"$$\begin{array}{cc}\text{\textbf{Symbol}} & value\end{array}$$ "
            r"and $d\not\mid n$ but `d\not\mid n` stays code."
            "\n"
            r"Price is $5 and prose \not\mid remains literal."
        )

        normalized = normalize_markdown(source)

        self.assertIn(r"\text{Symbol}", normalized)
        self.assertIn(r"$d\nmid n$", normalized)
        self.assertIn(r"`d\not\mid n`", normalized)
        self.assertIn(r"Price is $5 and prose \not\mid remains literal.", normalized)


class ReadabilityDefaultTests(unittest.TestCase):
    def test_defaults_prioritise_readability(self):
        self.assertEqual(DEFAULT_COLUMNS, 3)
        self.assertEqual(DEFAULT_FONT_SIZE, "8")
        self.assertEqual(DEFAULT_LINE_HEIGHT, "1.2")

        css = resolve_template(
            DEFAULT_COLUMNS,
            "yubiquitous",
            "arial",
            "microsoft-yahei",
            "system-code",
            DEFAULT_FONT_SIZE,
            DEFAULT_LINE_HEIGHT,
        )
        self.assertEqual(css["--table-font-size"], "7.2pt")


class RobustRenderingIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        output = Path(cls.tempdir.name) / "adversarial.html"
        convert_markdown(FIXTURE, output)
        cls.html = output.read_text(encoding="utf-8")
        parser = HtmlTreeParser()
        parser.feed(cls.html)
        cls.document = parser.root

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def list_item(self, text):
        matches = [
            item for item in self.document.find_all("li") if text in item.text()
        ]
        self.assertTrue(matches, f"No list item contains {text!r}")
        return min(matches, key=lambda item: len(item.text()))

    def node_containing(self, tag, text):
        matches = [
            node for node in self.document.find_all(tag) if text in node.text()
        ]
        self.assertTrue(matches, f"No <{tag}> contains {text!r}")
        return min(matches, key=lambda node: len(node.text()))

    def math_tex(self):
        return [
            node.text()
            for node in self.document.find_all("annotation")
            if node.attrs.get("encoding") == "application/x-tex"
        ]

    @staticmethod
    def direct_list_types(item):
        return [
            child.tag
            for child in item.children
            if isinstance(child, HtmlNode) and child.tag in {"ul", "ol"}
        ]

    def test_output_is_fully_offline(self):
        self.assertNotIn("cdn.jsdelivr.net", self.html)
        self.assertNotIn("katex", self.html.lower())
        self.assertNotIn("data-cheatsheet-layout", self.html)
        self.assertNotRegex(self.html, r"<script[^>]+\bsrc\s*=")
        self.assertIn('id="md2cheatsheet-layout-fit"', self.html)
        self.assertIn("fitMathToColumns", self.html)
        self.assertIn("ensureMathViewport", self.html)
        self.assertIn("math.style.transform", self.html)
        self.assertIn("adaptTablesToColumns", self.html)
        self.assertNotIn('<span class="math ', self.html)

    def test_missing_blank_lines_keep_blocks_separate(self):
        self.assertRegex(
            self.html,
            r"</ul>\s*<p>Paragraph after bullets must not become part of the last item\.</p>",
        )
        self.assertRegex(
            self.html,
            r"</ol>\s*<p>Paragraph after numbers must not become part of the last item\.</p>",
        )
        self.assertRegex(
            self.html,
            r"</div>\s*<p>Paragraph after the table must remain a paragraph\.</p>",
        )

    def test_alternating_blank_and_no_blank_blocks_keep_boundaries(self):
        self.assertRegex(
            self.html,
            r"</ul>\s*<p>Paragraph immediately after that list without a blank line\.</p>",
        )
        prose = self.node_containing(
            "p", "Paragraph after that list with a blank line."
        )
        self.assertIn(
            "Paragraph immediately before a heading without a blank line.",
            prose.text(),
        )
        self.node_containing("h4", "Heading Reached Without a Blank Line")
        self.node_containing(
            "p", "Paragraph immediately after the heading without a blank line."
        )

    def test_unordered_markers_and_two_three_four_space_indents_nest(self):
        expected = {
            "dash parent": ["ul"],
            "dash child at two spaces": ["ul"],
            "star grandchild at four spaces": ["ul"],
            "star parent at root": ["ul"],
            "plus child at three spaces": ["ul"],
            "plus parent at root": ["ul"],
            "star child at four spaces": ["ul"],
        }
        for text, list_types in expected.items():
            with self.subTest(item=text):
                self.assertEqual(
                    self.direct_list_types(self.list_item(text)), list_types
                )

    def test_unordered_to_ordered_to_unordered_to_ordered_nesting(self):
        expected = {
            "outer unordered A": ["ol"],
            "ordered child A1 at two spaces": ["ul"],
            "unordered grandchild A1a": ["ol"],
            "outer unordered B": ["ol"],
            "ordered child B1 at three spaces": ["ul"],
            "unordered grandchild B1a": ["ol"],
        }
        for text, list_types in expected.items():
            with self.subTest(item=text):
                self.assertEqual(
                    self.direct_list_types(self.list_item(text)), list_types
                )

    def test_ordered_to_unordered_to_ordered_to_unordered_nesting(self):
        expected = {
            "outer ordered C": ["ul"],
            "unordered child C1": ["ol"],
            "ordered grandchild C1a": ["ul"],
        }
        for text, list_types in expected.items():
            with self.subTest(item=text):
                self.assertEqual(
                    self.direct_list_types(self.list_item(text)), list_types
                )

    def test_tab_indented_mixed_lists_nest(self):
        self.assertEqual(
            self.direct_list_types(self.list_item("outer ordered D")), ["ul"]
        )
        self.assertEqual(
            self.direct_list_types(
                self.list_item("tab-indented unordered child D1")
            ),
            ["ol"],
        )

    def test_continuation_lines_remain_in_their_list_item(self):
        sprint = self.list_item("Sprint summary")
        self.assertIn("Sprint 1 needed a focused one-week scope.", sprint.text())
        self.assertIn(
            "This second continuation line must stay in the same item.",
            sprint.text(),
        )
        self.assertEqual(self.direct_list_types(sprint), [])
        self.assertRegex(
            self.html,
            re.compile(
                r"This second continuation line must stay in the same\s+item\."
            ),
        )

    def test_task_list_checkboxes_are_preserved(self):
        checkboxes = [
            node
            for node in self.document.find_all("input")
            if node.attrs.get("type") == "checkbox"
        ]
        self.assertEqual(len(checkboxes), 2)
        self.assertEqual(sum("checked" in box.attrs for box in checkboxes), 1)

    def test_adjacent_backtick_and_tilde_fences_render_as_code(self):
        for language in ("python", "json", "zsh", "bash", "markdown"):
            with self.subTest(language=language):
                self.assertIn(f'class="sourceCode {language}"', self.html)
        self.assertNotIn("```zsh", self.html)
        self.assertNotIn("~~~json", self.html)

    def test_indented_fences_remain_attached_to_their_list_items(self):
        administrator = self.list_item("If you need an administrator")
        nested_bullet = self.list_item("Parent with a nested fence")
        self.assertTrue(administrator.find_all("pre"))
        self.assertTrue(nested_bullet.find_all("pre"))
        self.assertIn("Then restart the program.", administrator.text())
        self.assertIn("Text immediately after the nested fence.", nested_bullet.text())

    def test_markdown_looking_code_stays_literal(self):
        self.assertIn("this is literal code", self.html)
        self.assertIn("| not | a table |", self.html)
        self.assertIn("$$not math$$", self.html)

    def test_long_complex_english_chinese_and_mixed_paragraphs_survive(self):
        english = self.node_containing("p", "This deliberately long English sentence")
        chinese = self.node_containing("p", "这是一个故意写得很长")
        mixed = self.node_containing("p", "English中文mixed-without-spaces")
        self.assertIn("SupercalifragilisticLongIdentifier", english.text())
        self.assertIn("VeryLongMixedLanguageIdentifier", chinese.text())
        self.assertIn("继续中文thenEnglish", mixed.text())
        self.assertNotIn("�", self.html)

    def test_inline_math_parses_with_or_without_surrounding_spaces(self):
        tex = self.math_tex()
        expected = {
            r"E=mc^2",
            r"x^2+y^2=z^2",
            r"A\cap B=\varnothing",
            r"\Pr(X\geq k)\leq\frac{\mathbb{E}[X]}{k}",
            r"\mathbb{E}[X]=\sum_x x\Pr(X=x)",
            r"\alpha+\beta=\gamma",
            r"\lVert v\rVert_2=1",
            r"f\colon A\to B",
            r"P(A_1\cap A_2\cap A_3\cap A_4\cap A_5)=P(A_1)P(A_2\mid A_1)P(A_3\mid A_1\cap A_2)P(A_4\mid A_1\cap A_2\cap A_3)P(A_5\mid A_1\cap A_2\cap A_3\cap A_4)",
        }
        self.assertTrue(expected.issubset(set(tex)), expected.difference(tex))
        self.assertIn('class="math-inline-xlong"', self.html)
        self.assertIn("$5", self.node_containing("p", "escaped currency").text())
        self.assertIn("$not_math$", self.node_containing("code", "$not_math$").text())

    def test_display_math_without_blank_lines_remains_a_display_block(self):
        self.node_containing(
            "p", "Paragraph immediately before display math without a blank line."
        )
        self.node_containing(
            "p", "Paragraph immediately after display math without a blank line."
        )
        formula = self.node_containing(
            "annotation", r"\nabla\cdot\mathbf{E}=\frac{\rho}{\varepsilon_0}"
        )
        self.assertEqual(formula.parent.parent.attrs.get("display"), "block")

    def test_extended_latex_notation_converts_to_mathml(self):
        compact_tex = "".join(self.math_tex()).replace(" ", "").replace("\n", "")
        for notation in (
            r"\sqrt[3]{y+2}",
            r"\binom{n}{k}",
            r"\lim_{n\to\infty}",
            r"\prod_{j=1}^{m}",
            r"\int_{-\infty}^{\infty}",
            r"\oint_{\partial\Omega}",
            r"\begin{bmatrix}",
            r"\operatorname*{arg\,min}",
            r"\underbrace",
            r"\overbrace",
            r"\text{中文说明}",
            r"\text{信息熵/entropy}",
        ):
            with self.subTest(notation=notation):
                self.assertIn(notation.replace(" ", ""), compact_tex)
        for mathml_tag in ("mfrac", "msqrt", "mroot", "munderover", "mtable", "mover"):
            with self.subTest(mathml_tag=mathml_tag):
                self.assertTrue(self.document.find_all(mathml_tag))

    def test_collapsed_latex_row_commands_render_as_symbols(self):
        annotation = self.node_containing("annotation", r"\text{there exists}")
        math = annotation.parent.parent
        symbols = {
            node.text()
            for tag in ("mo", "mi")
            for node in math.find_all(tag)
        }
        self.assertTrue({"∃", "→", "∅"}.issubset(symbols))
        self.assertIn(r"d\nmid n", self.math_tex())

    def test_bilingual_table_with_inline_math_stays_structural(self):
        self.node_containing("th", "Topic 主题")
        self.node_containing("td", "Bayes 贝叶斯")
        self.node_containing("td", "ALongUnbrokenCellValue")
        self.assertIn(
            r"P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}", self.math_tex()
        )

    def test_tables_are_wrapped_and_mathml_is_static(self):
        self.assertEqual(self.html.count('<div class="table-wrapper">'), 3)
        self.assertGreaterEqual(self.html.count("<math"), 30)
        self.assertIn('<math display="block"', self.html)
        self.assertIn("<mtable", self.html)
        self.assertGreaterEqual(self.html.count('class="math-long"'), 2)

    def test_common_three_and_four_column_tables_stay_as_grids(self):
        self.assertIn(
            "const useCards = columnCount >= 5 && metrics.width < CARD_COLUMN_THRESHOLD;",
            self.html,
        )

    def test_generated_html_uses_native_list_markers_and_atomic_fragments(self):
        css = (ROOT / "cheatsheet.css").read_text(encoding="utf-8")

        self.assertNotRegex(css, r"ul\s*>\s*li::before")
        self.assertIn("li::marker", css)
        self.assertRegex(css, r"p\s*\{[^}]*overflow-wrap:\s*anywhere", re.DOTALL)
        self.assertRegex(
            css,
            r"\.content-wrapper\s*\{[^}]*text-align:\s*left",
            re.DOTALL,
        )
        self.assertRegex(
            css,
            r"p,\s*li,\s*blockquote,\s*th,\s*td\s*\{[^}]*text-align:\s*left",
            re.DOTALL,
        )
        self.assertNotRegex(css, r"text-align:\s*(?:justify|start)\b")
        self.assertRegex(
            css,
            r'math\[display="inline"\]\s*\{[^}]*display:\s*inline-block',
            re.DOTALL,
        )
        self.assertRegex(css, r"table\s*\{[^}]*table-layout:\s*fixed", re.DOTALL)
        self.assertRegex(
            css,
            r"\.table-wrapper\.table-cards\s+table,[^{]*\{[^}]*display:\s*block",
            re.DOTALL,
        )
        self.assertRegex(
            css,
            r"\.table-wrapper\.table-cards\s+td::before\s*\{[^}]*attr\(data-label\)",
            re.DOTALL,
        )
        self.assertRegex(
            css,
            r"math\.math-inline-xlong\s*\{[^}]*font-size:",
            re.DOTALL,
        )
        self.assertRegex(
            css,
            r"\.math-viewport-inline\s*\{[^}]*display:\s*inline-block",
            re.DOTALL,
        )
        self.assertRegex(
            css,
            r"\.math-viewport-block\s*\{[^}]*display:\s*block",
            re.DOTALL,
        )
        self.assertRegex(css, r"li\s*\{[^}]*break-inside:\s*avoid", re.DOTALL)
        self.assertRegex(
            css,
            r"\.table-wrapper\s*\{[^}]*break-inside:\s*avoid",
            re.DOTALL,
        )


if __name__ == "__main__":
    unittest.main()
