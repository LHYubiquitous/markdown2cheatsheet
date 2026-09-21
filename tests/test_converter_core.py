import base64
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from converter_core import (
    _pandoc_resource_targets,
    convert_markdown,
    ensure_pandoc,
    validate_embedded_resources,
)


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class PandocEncodingTests(unittest.TestCase):
    def test_resource_scan_decodes_pandoc_json_as_utf8(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "sheet.md"
            source.write_text("# 中文笔记\n", encoding="utf-8")
            document = {"pandoc-api-version": [1, 23, 1], "meta": {}, "blocks": []}
            completed = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(document, ensure_ascii=False),
                stderr="",
            )

            with patch("converter_core.subprocess.run", return_value=completed) as run:
                self.assertEqual(_pandoc_resource_targets("pandoc", source), [])

            self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")

    def test_conversion_decodes_pandoc_output_as_utf8(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "sheet.md"
            output = root / "sheet.html"
            source.write_text("# 中文笔记\n", encoding="utf-8")

            def run_pandoc(command, **kwargs):
                raw_html = Path(command[command.index("--output") + 1])
                raw_html.write_text(
                    "<html><head></head><body><p>中文笔记</p></body></html>",
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            with (
                patch("converter_core.ensure_pandoc", return_value="pandoc"),
                patch("converter_core.subprocess.run", side_effect=run_pandoc) as run,
            ):
                convert_markdown(source, output)

            self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")
            self.assertIn("中文笔记", output.read_text(encoding="utf-8"))


class ConverterImageTests(unittest.TestCase):
    def test_embeds_image_relative_to_markdown_outside_current_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "notes"
            image_dir = source_dir / "assets"
            image_dir.mkdir(parents=True)
            source = source_dir / "sheet.md"
            output = root / "sheet.html"
            source.write_text("# Sheet\n\n![pixel](assets/pixel.png)\n", encoding="utf-8")
            (image_dir / "pixel.png").write_bytes(ONE_PIXEL_PNG)

            convert_markdown(source, output)

            html = output.read_text(encoding="utf-8")
            self.assertIn('src="data:image/png;base64,', html)
            self.assertNotIn("assets/pixel.png", html)

    def test_rejects_circular_stylesheet_import_before_conversion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            source = root / "sheet.md"
            source.write_text('<link rel="stylesheet" href="style.css">\n', encoding="utf-8")
            (root / "style.css").write_text('@import "other.css";', encoding="utf-8")
            (root / "other.css").write_text('@import "style.css";', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Circular stylesheet import"):
                validate_embedded_resources(ensure_pandoc(), source, [root], root)


if __name__ == "__main__":
    unittest.main()
