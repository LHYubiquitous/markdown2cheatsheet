#!/usr/bin/env python3
"""Core conversion helpers shared by the CLI and GUI."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pandoc_support import MIN_PANDOC_VERSION, detect_pandoc_version, is_version_at_least
from postprocess import process
from runtime_paths import get_app_root
from template_presets import (
    DEFAULT_COLOR_TEMPLATE,
    DEFAULT_COLUMNS,
    DEFAULT_CJK_FONT,
    DEFAULT_CODE_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_LINE_HEIGHT,
    DEFAULT_LATIN_FONT,
    list_templates,
    resolve_template,
)

ROOT_DIR = get_app_root()
BASE_CSS = ROOT_DIR / "cheatsheet.css"


def ensure_pandoc() -> str:
    """Locate pandoc and raise a friendly error when missing or too old."""
    pandoc = shutil.which("pandoc")
    candidates: list[str | Path] = [pandoc] if pandoc else []

    if sys.platform.startswith("win"):
        username = Path.home().name
        candidates.extend(
            [
                Path(f"/c/Users/{username}/AppData/Local/Pandoc/pandoc.exe"),
                Path("/c/Program Files/Pandoc/pandoc.exe"),
            ]
        )

    for candidate in candidates:
        if not candidate:
            continue
        version = detect_pandoc_version(candidate)
        if not version:
            continue
        if not is_version_at_least(version):
            raise RuntimeError(
                f"pandoc {version} is below the required {MIN_PANDOC_VERSION}. "
                "Please update pandoc, restart markdown2cheatsheet, and try again."
            )
        return str(candidate)

    raise RuntimeError(
        f"pandoc {MIN_PANDOC_VERSION}+ is required but was not found. "
        "Install or update pandoc, restart markdown2cheatsheet, and try again."
    )


def locate_css(input_path: Path) -> Path:
    """Find the base cheatsheet stylesheet."""
    candidates = [
        input_path.parent / "cheatsheet.css",
        BASE_CSS,
        Path.cwd() / "cheatsheet.css",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            nested_candidate = candidate / "cheatsheet.css"
            if nested_candidate.exists():
                return nested_candidate.resolve()
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(
        "cheatsheet.css not found. Place it next to the markdown file or keep it in the project root."
    )


def render_override_css(columns: int, color_template: str) -> str:
    """Build an override stylesheet using default font selections."""
    variables = resolve_template(
        columns,
        color_template,
        DEFAULT_LATIN_FONT,
        DEFAULT_CJK_FONT,
        DEFAULT_CODE_FONT,
        DEFAULT_FONT_SIZE,
        DEFAULT_LINE_HEIGHT,
    )
    lines = [":root {"]
    for key, value in variables.items():
        lines.append(f"  {key}: {value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_override_css_with_fonts(
    columns: int,
    color_template: str,
    latin_font: str,
    cjk_font: str,
    code_font: str,
    font_size: str,
    line_height: str,
) -> str:
    """Build an override stylesheet from the selected presets."""
    variables = resolve_template(
        columns,
        color_template,
        latin_font,
        cjk_font,
        code_font,
        font_size,
        line_height,
    )
    lines = [":root {"]
    for key, value in variables.items():
        lines.append(f"  {key}: {value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def convert_markdown(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    columns: int = DEFAULT_COLUMNS,
    color_template: str = DEFAULT_COLOR_TEMPLATE,
    latin_font: str = DEFAULT_LATIN_FONT,
    cjk_font: str = DEFAULT_CJK_FONT,
    code_font: str = DEFAULT_CODE_FONT,
    font_size: str = DEFAULT_FONT_SIZE,
    line_height: str = DEFAULT_LINE_HEIGHT,
    title: str | None = None,
) -> Path:
    """Convert a markdown file into a standalone cheatsheet HTML file."""
    pandoc = ensure_pandoc()
    input_file = Path(input_path).expanduser().resolve()
    if not input_file.exists():
        raise FileNotFoundError(f"input markdown file not found: {input_file}")

    final_output = (
        Path(output_path).expanduser().resolve()
        if output_path
        else input_file.with_suffix(".html")
    )
    final_output.parent.mkdir(parents=True, exist_ok=True)

    css_file = locate_css(input_file)
    page_title = title or input_file.stem
    override_css = render_override_css_with_fonts(
        columns,
        color_template,
        latin_font,
        cjk_font,
        code_font,
        font_size,
        line_height,
    )

    with tempfile.TemporaryDirectory(prefix="md2cheatsheet_") as tmpdir:
        tmp_dir = Path(tmpdir)
        raw_html = tmp_dir / "raw.html"
        override_file = tmp_dir / "template-overrides.css"
        override_file.write_text(override_css, encoding="utf-8")

        command = [
            pandoc,
            str(input_file),
            "--from",
            "markdown+mark+smart+pipe_tables+fenced_code_blocks",
            "--to",
            "html5",
            "--standalone",
            "--embed-resources",
            "--css",
            str(css_file),
            "--css",
            str(override_file),
            "--metadata",
            f"title={page_title}",
            "--highlight-style",
            "pygments",
            "--output",
            str(raw_html),
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() or exc.stdout.strip() or "Pandoc conversion failed."
            raise RuntimeError(stderr) from exc

        html = raw_html.read_text(encoding="utf-8")
        final_output.write_text(process(html), encoding="utf-8")

    return final_output


__all__ = [
    "convert_markdown",
    "ensure_pandoc",
    "list_templates",
    "render_override_css",
    "render_override_css_with_fonts",
]
