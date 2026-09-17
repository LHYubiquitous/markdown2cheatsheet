import tempfile
import unittest
from pathlib import Path

from gui_app import resolve_source_directory


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


if __name__ == "__main__":
    unittest.main()
