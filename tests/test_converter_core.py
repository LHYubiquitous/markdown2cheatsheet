import base64
import tempfile
import unittest
from pathlib import Path

from converter_core import convert_markdown, ensure_pandoc, validate_embedded_resources


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


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
