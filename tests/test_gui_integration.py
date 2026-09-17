import base64
import json
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from urllib.error import HTTPError

from gui_app import create_server


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class GuiImageIntegrationTests(unittest.TestCase):
    def request_conversion(self, project_root, filename, markdown, expect_error=False):
        server = create_server("127.0.0.1", 0, project_root)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            payload = json.dumps(
                {
                    "filename": filename,
                    "outputName": "sheet.html",
                    "markdown": markdown,
                }
            ).encode("utf-8")
            request = urllib.request.Request(
                f"http://127.0.0.1:{server.server_port}/api/convert",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    result = json.load(response)
            except HTTPError as exc:
                if not expect_error:
                    raise
                result = json.load(exc)
                result["status"] = exc.code
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        return result

    def test_embeds_markdown_image_relative_to_original_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir).resolve()
            source = project_root / "notes" / "sheet.md"
            image = project_root / "assets" / "pixel.png"
            source.parent.mkdir()
            image.parent.mkdir()
            markdown = "# Sheet\n\n![pixel](../assets/pixel.png)\n"
            source.write_text(markdown, encoding="utf-8")
            image.write_bytes(ONE_PIXEL_PNG)

            result = self.request_conversion(project_root, source.name, markdown)

            self.assertIn('src="data:image/png;base64,', result["html"])
            self.assertNotIn("../assets/pixel.png", result["html"])

    def test_embeds_raw_html_image(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir).resolve()
            source = project_root / "sheet.md"
            image = project_root / "assets" / "pixel.png"
            image.parent.mkdir()
            markdown = '<img src="assets/pixel.png" width="10">\n'
            source.write_text(markdown, encoding="utf-8")
            image.write_bytes(ONE_PIXEL_PNG)

            result = self.request_conversion(project_root, source.name, markdown)

            self.assertIn('src="data:image/png;base64,', result["html"])
            self.assertNotIn("assets/pixel.png", result["html"])

    def test_rejects_image_that_escapes_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outer = Path(tmpdir).resolve()
            project_root = outer / "project"
            project_root.mkdir()
            source = project_root / "sheet.md"
            source.write_text("![secret](../secret.png)\n", encoding="utf-8")
            (outer / "secret.png").write_bytes(ONE_PIXEL_PNG)

            result = self.request_conversion(
                project_root,
                source.name,
                source.read_text(encoding="utf-8"),
                expect_error=True,
            )

            self.assertEqual(result["status"], 400)
            self.assertIn("outside the project root", result["error"])

    def test_rejects_symlink_image_that_escapes_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outer = Path(tmpdir).resolve()
            project_root = outer / "project"
            assets = project_root / "assets"
            assets.mkdir(parents=True)
            outside_image = outer / "secret.png"
            outside_image.write_bytes(ONE_PIXEL_PNG)
            (assets / "linked.png").symlink_to(outside_image)
            source = project_root / "sheet.md"
            source.write_text("![secret](assets/linked.png)\n", encoding="utf-8")

            result = self.request_conversion(
                project_root,
                source.name,
                source.read_text(encoding="utf-8"),
                expect_error=True,
            )

            self.assertEqual(result["status"], 400)
            self.assertIn("outside the project root", result["error"])

    def test_rejects_css_image_that_escapes_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outer = Path(tmpdir).resolve()
            project_root = outer / "project"
            project_root.mkdir()
            source = project_root / "sheet.md"
            source.write_text(
                "<style>body { background-image: url(../secret.png); }</style>\n",
                encoding="utf-8",
            )
            (outer / "secret.png").write_bytes(ONE_PIXEL_PNG)

            result = self.request_conversion(
                project_root,
                source.name,
                source.read_text(encoding="utf-8"),
                expect_error=True,
            )

            self.assertEqual(result["status"], 400)
            self.assertIn("outside the project root", result["error"])

    def test_rejects_video_poster_that_escapes_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outer = Path(tmpdir).resolve()
            project_root = outer / "project"
            project_root.mkdir()
            source = project_root / "sheet.md"
            source.write_text('<video poster="../secret.png"></video>\n', encoding="utf-8")
            (outer / "secret.png").write_bytes(ONE_PIXEL_PNG)

            result = self.request_conversion(
                project_root,
                source.name,
                source.read_text(encoding="utf-8"),
                expect_error=True,
            )

            self.assertEqual(result["status"], 400)
            self.assertIn("outside the project root", result["error"])

    def test_rejects_css_import_that_escapes_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outer = Path(tmpdir).resolve()
            project_root = outer / "project"
            project_root.mkdir()
            source = project_root / "sheet.md"
            source.write_text('<style>@import "../secret.css";</style>\n', encoding="utf-8")
            (outer / "secret.css").write_text("body { color: #123456; }", encoding="utf-8")

            result = self.request_conversion(
                project_root,
                source.name,
                source.read_text(encoding="utf-8"),
                expect_error=True,
            )

            self.assertEqual(result["status"], 400)
            self.assertIn("outside the project root", result["error"])

    def test_rejects_nested_css_image_that_escapes_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outer = Path(tmpdir).resolve()
            project_root = outer / "project"
            project_root.mkdir()
            source = project_root / "sheet.md"
            source.write_text(
                '<link rel="stylesheet" href="style.css">\n',
                encoding="utf-8",
            )
            (project_root / "style.css").write_text(
                "body { background-image: url(../secret.png); }",
                encoding="utf-8",
            )
            (outer / "secret.png").write_bytes(ONE_PIXEL_PNG)

            result = self.request_conversion(
                project_root,
                source.name,
                source.read_text(encoding="utf-8"),
                expect_error=True,
            )

            self.assertEqual(result["status"], 400)
            self.assertIn("outside the project root", result["error"])

    def test_rejects_nested_css_import_that_escapes_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outer = Path(tmpdir).resolve()
            project_root = outer / "project"
            project_root.mkdir()
            source = project_root / "sheet.md"
            source.write_text(
                '<link rel="stylesheet" href="style.css">\n',
                encoding="utf-8",
            )
            (project_root / "style.css").write_text(
                '@import "../secret.css";',
                encoding="utf-8",
            )
            (outer / "secret.css").write_text("body { color: #123456; }", encoding="utf-8")

            result = self.request_conversion(
                project_root,
                source.name,
                source.read_text(encoding="utf-8"),
                expect_error=True,
            )

            self.assertEqual(result["status"], 400)
            self.assertIn("outside the project root", result["error"])


if __name__ == "__main__":
    unittest.main()
