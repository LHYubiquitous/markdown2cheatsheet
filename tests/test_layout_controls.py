import unittest
from pathlib import Path

from converter_core import render_override_css_with_fonts
from template_presets import list_templates, resolve_template


ROOT = Path(__file__).resolve().parents[1]


class LayoutControlTests(unittest.TestCase):
    def test_resolves_arbitrary_numeric_layout_controls(self):
        css = resolve_template(
            4,
            "navy",
            "arial",
            "microsoft-yahei",
            "system-code",
            "8.3",
            "1.17",
            page_orientation="portrait",
            page_margin=7.5,
            column_gap=4.5,
            table_scale=0.85,
            code_scale=0.9,
            image_width=42,
            block_spacing=1.25,
            column_rule=False,
        )

        self.assertEqual(css["--base-font-size"], "8.3pt")
        self.assertEqual(css["--body-line-height"], "1.17")
        self.assertEqual(css["--page-width"], "210mm")
        self.assertEqual(css["--page-margin"], "7.5mm")
        self.assertEqual(css["--column-gap"], "4.5mm")
        self.assertEqual(css["--column-rule-width"], "0pt")
        self.assertEqual(css["--image-width"], "42%")
        self.assertEqual(css["--block-gap"], "1.25pt")
        self.assertEqual(css["--table-font-size"], "6.4pt")
        self.assertEqual(css["--inline-code-font-size"], "5.7pt")

    def test_override_css_contains_print_page_settings(self):
        css = render_override_css_with_fonts(
            3,
            "yubiquitous",
            "arial",
            "microsoft-yahei",
            "system-code",
            "9.2",
            "1.25",
            page_orientation="portrait",
            page_margin=6.5,
        )

        self.assertIn("--base-font-size: 9.2pt;", css)
        self.assertIn("--page-margin: 6.5mm;", css)
        self.assertIn("@page {", css)
        self.assertIn("size: A4 portrait;", css)
        self.assertIn("margin: 6.5mm;", css)

    def test_control_metadata_exposes_numeric_ranges_and_defaults(self):
        templates = list_templates()
        controls = templates["controls"]

        self.assertEqual(controls["fontSize"]["default"], 8.0)
        self.assertEqual(controls["fontSize"]["step"], 0.1)
        self.assertEqual(controls["pageMargin"]["unit"], "mm")
        self.assertEqual(controls["imageWidth"]["max"], 100)
        self.assertEqual(templates["defaults"]["pageOrientation"], "landscape")
        self.assertTrue(templates["defaults"]["columnRule"])

    def test_rejects_out_of_range_or_unknown_layout_values(self):
        base = (3, "yubiquitous", "arial", "microsoft-yahei", "system-code", "8", "1.2")
        invalid = (
            {"font_size": 3.9},
            {"line_height": 2.1},
            {"page_orientation": "diagonal"},
            {"page_margin": -0.1},
            {"column_gap": 15.1},
            {"table_scale": 0.49},
            {"code_scale": 1.51},
            {"image_width": 101},
            {"block_spacing": 4.1},
        )

        for overrides in invalid:
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                kwargs = {
                    "font_size": base[5],
                    "line_height": base[6],
                    **overrides,
                }
                resolve_template(*base[:5], **kwargs)


class GuiControlMarkupTests(unittest.TestCase):
    def test_gui_uses_numeric_inputs_and_workflow_controls(self):
        html = (ROOT / "gui" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "gui" / "app.js").read_text(encoding="utf-8")

        for control_id in (
            "fontSize",
            "lineHeight",
            "pageMargin",
            "columnGap",
            "tableScale",
            "codeScale",
            "imageWidth",
            "blockSpacing",
        ):
            self.assertRegex(
                html,
                rf'<input[^>]+id="{control_id}"[^>]+type="number"|'
                rf'<input[^>]+type="number"[^>]+id="{control_id}"',
            )

        self.assertIn('id="pageOrientation"', html)
        self.assertIn('id="columnRule"', html)
        self.assertIn('id="autoPreview"', html)
        self.assertIn('id="resetBtn"', html)
        self.assertIn('id="fontSizePreset"', html)
        self.assertIn('value="">Quick sizes</option>', html)
        for preset in (4, 5, 6, 7, 8):
            self.assertIn(f'<option value="{preset}">{preset} pt</option>', html)
        self.assertIn('fontSizePreset.addEventListener("change"', script)
        self.assertIn("localStorage", script)
        self.assertIn("schedulePreview", script)

    def test_gui_copy_is_concise_and_palette_is_monochrome(self):
        html = (ROOT / "gui" / "index.html").read_text(encoding="utf-8")
        stylesheet = (ROOT / "gui" / "styles.css").read_text(encoding="utf-8")

        for removed_copy in (
            "Print workbench",
            "Current print recipe",
            "Markdown in, standalone HTML out",
            "Set the reading density",
            "Control printable geometry",
            "Print a fine rule",
            "650ms debounce",
        ):
            self.assertNotIn(removed_copy, html)

        self.assertIn("--charcoal: #303030", stylesheet)
        self.assertIn("--canvas: #e4e4e4", stylesheet)
        self.assertIn("--white: #fff", stylesheet)
        self.assertNotIn("--accent", stylesheet)
        self.assertNotIn("linear-gradient", stylesheet)
        self.assertNotIn("box-shadow", stylesheet)


if __name__ == "__main__":
    unittest.main()
