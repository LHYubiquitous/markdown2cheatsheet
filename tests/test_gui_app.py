import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gui_app import build_parser, resolve_source_directory, run_server


class SourceDirectoryResolutionTests(unittest.TestCase):
    def test_unique_nested_markdown_uses_its_original_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            source = root / "course" / "notes" / "sheet.md"
            source.parent.mkdir(parents=True)
            source.write_text("# Sheet", encoding="utf-8")

            directory, warning = resolve_source_directory("sheet.md", root)

            self.assertEqual(directory, source.parent)
            self.assertIsNone(warning)

    def test_duplicate_basename_is_reported_instead_of_guessing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            for folder in ("one", "two"):
                source = root / folder / "sheet.md"
                source.parent.mkdir()
                source.write_text("# Sheet", encoding="utf-8")

            directory, warning = resolve_source_directory("sheet.md", root)

            self.assertEqual(directory, root)
            self.assertIn("multiple", warning.lower())


class GuiStartupTests(unittest.TestCase):
    def test_default_port_is_ephemeral_to_avoid_reusing_a_stale_gui(self):
        self.assertEqual(build_parser().parse_args([]).port, 0)

    @patch("gui_app.create_server")
    @patch("gui_app.webbrowser.open")
    def test_browser_uses_the_port_bound_for_this_server(self, open_browser, create_server):
        server = MagicMock()
        server.server_port = 54321
        create_server.return_value = server

        run_server(port=0)

        open_browser.assert_called_once_with("http://127.0.0.1:54321")
        server.serve_forever.assert_called_once_with()
        server.server_close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
