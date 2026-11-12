#!/usr/bin/env python3
"""Core conversion helpers shared by the CLI and GUI."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from urllib.request import url2pathname

from markdown_normalizer import normalize_markdown
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
    DEFAULT_PAGE_ORIENTATION,
    DEFAULT_PAGE_MARGIN,
    DEFAULT_COLUMN_GAP,
    DEFAULT_TABLE_SCALE,
    DEFAULT_CODE_SCALE,
    DEFAULT_IMAGE_WIDTH,
    DEFAULT_BLOCK_SPACING,
    DEFAULT_COLUMN_RULE,
    list_templates,
    resolve_template,
)

ROOT_DIR = get_app_root()
BASE_CSS = ROOT_DIR / "cheatsheet.css"
PANDOC_MARKDOWN_FORMAT = (
    "markdown+mark+smart+pipe_tables+fenced_code_blocks"
    "+lists_without_preceding_blankline"
)


_CSS_URL_PATTERN = re.compile(
    r"url\(\s*(?:(['\"])(.*?)\1|([^)'\"]+))\s*\)",
    flags=re.IGNORECASE,
)
_CSS_IMPORT_PATTERN = re.compile(
    r"@import\s+(?:\"([^\"]+)\"|'([^']+)')",
    flags=re.IGNORECASE,
)
_CSS_COMMENT_PATTERN = re.compile(r"/\*.*?\*/", flags=re.DOTALL)
_RESOURCE_ATTRIBUTES = {"data", "poster", "src"}
_RESOURCE_HREF_TAGS = {"image", "link", "use"}


def _css_resource_targets(css: str) -> list[tuple[str, bool]]:
    uncommented = _CSS_COMMENT_PATTERN.sub("", css)
    targets = [
        ((match.group(2) if match.group(1) else match.group(3)).strip(), False)
        for match in _CSS_URL_PATTERN.finditer(uncommented)
    ]
    targets.extend(
        ((match.group(1) or match.group(2)).strip(), True)
        for match in _CSS_IMPORT_PATTERN.finditer(uncommented)
    )
    return targets


def _srcset_targets(value: str) -> list[str]:
    if value.lstrip().lower().startswith("data:"):
        return []
    return [candidate.strip().split(maxsplit=1)[0] for candidate in value.split(",") if candidate.strip()]


class _EmbeddedResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[tuple[str, bool]] = []
        self._style_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()
        normalized_attrs = {
            name.lower(): value
            for name, value in attrs
            if value is not None
        }
        is_stylesheet_link = (
            normalized_tag == "link"
            and "stylesheet" in normalized_attrs.get("rel", "").lower().split()
        )
        if normalized_tag == "style":
            self._style_depth += 1
        for name, value in attrs:
            if not value:
                continue
            normalized_name = name.lower()
            if normalized_name in _RESOURCE_ATTRIBUTES or (
                normalized_name == "href" and normalized_tag in _RESOURCE_HREF_TAGS
            ):
                self.sources.append((value, is_stylesheet_link and normalized_name == "href"))
            elif normalized_name == "srcset":
                self.sources.extend((target, False) for target in _srcset_targets(value))
            elif normalized_name == "style":
                self.sources.extend(_css_resource_targets(value))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._style_depth:
            self.sources.extend(_css_resource_targets(data))


def _pandoc_resource_targets(pandoc: str, input_file: Path) -> list[tuple[str, bool]]:
    """Return resources Pandoc may embed from Markdown and raw HTML."""
    command = [
        pandoc,
        "--from",
        PANDOC_MARKDOWN_FORMAT,
        "--to",
        "json",
    ]
    markdown = normalize_markdown(input_file.read_text(encoding="utf-8"))
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            input=markdown,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() or exc.stdout.strip() or "Pandoc resource validation failed."
        raise RuntimeError(stderr) from exc

    document = json.loads(result.stdout)
    targets: list[tuple[str, bool]] = []

    def visit(node) -> None:
        if isinstance(node, list):
            for child in node:
                visit(child)
            return
        if not isinstance(node, dict):
            return

        node_type = node.get("t")
        content = node.get("c")
        if node_type == "Image" and isinstance(content, list) and len(content) >= 3:
            target = content[2]
            if isinstance(target, list) and target:
                targets.append((target[0], False))
        elif (
            node_type in {"RawInline", "RawBlock"}
            and isinstance(content, list)
            and len(content) >= 2
            and content[0] == "html"
        ):
            parser = _EmbeddedResourceParser()
            parser.feed(content[1])
            targets.extend(parser.sources)

        for child in node.values():
            visit(child)

    visit(document)
    return targets


def _local_resource_path(target: str) -> Path | None:
    """Translate a local resource target to a path and ignore remote/data URLs."""
    if not target or target.startswith(("#", "//")):
        return None

    direct_path = Path(unquote(target))
    if direct_path.is_absolute():
        return direct_path

    parsed = urlsplit(target)
    if parsed.scheme and parsed.scheme != "file":
        return None
    if parsed.scheme == "file":
        return Path(url2pathname(parsed.path))
    return Path(unquote(parsed.path))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_embedded_resources(
    pandoc: str,
    input_file: Path,
    resource_directories: list[Path],
    allowed_root: str | Path,
) -> None:
    """Reject local embedded resources outside the GUI's trusted root."""
    root = Path(allowed_root).expanduser().resolve()
    for directory in resource_directories:
        if not _is_within(directory, root):
            raise ValueError(f"Resource directory is outside the project root: {directory}")

    active_stylesheets: set[Path] = set()
    validated_stylesheets: set[Path] = set()

    def validate_target(
        target: str,
        search_directories: list[Path],
        is_stylesheet: bool,
    ) -> None:
        local_path = _local_resource_path(target)
        if local_path is None:
            return

        candidates = (
            [local_path.resolve()]
            if local_path.is_absolute()
            else [(directory / local_path).resolve() for directory in search_directories]
        )
        selected = next((candidate for candidate in candidates if candidate.exists()), None)
        if selected is not None and not _is_within(selected, root):
            raise ValueError(f"Embedded resource is outside the project root: {target}")
        if (
            selected is None
            or not (is_stylesheet or selected.suffix.lower() == ".css")
        ):
            return
        if selected in active_stylesheets:
            raise ValueError(f"Circular stylesheet import detected: {target}")
        if selected in validated_stylesheets:
            return

        active_stylesheets.add(selected)
        try:
            css = selected.read_text(encoding="utf-8", errors="replace")
        except OSError:
            active_stylesheets.remove(selected)
            return
        try:
            for dependency, dependency_is_stylesheet in _css_resource_targets(css):
                validate_target(dependency, [selected.parent], dependency_is_stylesheet)
        finally:
            active_stylesheets.remove(selected)
        validated_stylesheets.add(selected)

    for target, is_stylesheet in _pandoc_resource_targets(pandoc, input_file):
        validate_target(target, resource_directories, is_stylesheet)


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
    font_size: str | int | float,
    line_height: str | int | float,
    *,
    page_orientation: str = DEFAULT_PAGE_ORIENTATION,
    page_margin: str | int | float = DEFAULT_PAGE_MARGIN,
    column_gap: str | int | float = DEFAULT_COLUMN_GAP,
    table_scale: str | int | float = DEFAULT_TABLE_SCALE,
    code_scale: str | int | float = DEFAULT_CODE_SCALE,
    image_width: str | int | float = DEFAULT_IMAGE_WIDTH,
    block_spacing: str | int | float = DEFAULT_BLOCK_SPACING,
    column_rule: bool = DEFAULT_COLUMN_RULE,
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
        page_orientation=page_orientation,
        page_margin=page_margin,
        column_gap=column_gap,
        table_scale=table_scale,
        code_scale=code_scale,
        image_width=image_width,
        block_spacing=block_spacing,
        column_rule=column_rule,
    )
    lines = [":root {"]
    for key, value in variables.items():
        lines.append(f"  {key}: {value};")
    lines.append("}")
    lines.extend(
        [
            "",
            "@page {",
            f"  size: A4 {page_orientation};",
            f"  margin: {variables['--page-margin']};",
            "}",
        ]
    )
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
    font_size: str | int | float = DEFAULT_FONT_SIZE,
    line_height: str | int | float = DEFAULT_LINE_HEIGHT,
    page_orientation: str = DEFAULT_PAGE_ORIENTATION,
    page_margin: str | int | float = DEFAULT_PAGE_MARGIN,
    column_gap: str | int | float = DEFAULT_COLUMN_GAP,
    table_scale: str | int | float = DEFAULT_TABLE_SCALE,
    code_scale: str | int | float = DEFAULT_CODE_SCALE,
    image_width: str | int | float = DEFAULT_IMAGE_WIDTH,
    block_spacing: str | int | float = DEFAULT_BLOCK_SPACING,
    column_rule: bool = DEFAULT_COLUMN_RULE,
    title: str | None = None,
    resource_paths: Iterable[str | Path] | None = None,
    allowed_resource_root: str | Path | None = None,
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
        page_orientation=page_orientation,
        page_margin=page_margin,
        column_gap=column_gap,
        table_scale=table_scale,
        code_scale=code_scale,
        image_width=image_width,
        block_spacing=block_spacing,
        column_rule=column_rule,
    )
    configured_resources = list(resource_paths) if resource_paths is not None else [input_file.parent]
    resource_directories: list[Path] = []
    for directory in configured_resources:
        resolved = Path(directory).expanduser().resolve()
        if resolved not in resource_directories:
            resource_directories.append(resolved)

    if allowed_resource_root is not None:
        validate_embedded_resources(
            pandoc,
            input_file,
            resource_directories,
            allowed_resource_root,
        )

    with tempfile.TemporaryDirectory(prefix="md2cheatsheet_") as tmpdir:
        tmp_dir = Path(tmpdir)
        raw_html = tmp_dir / "raw.html"
        normalized_markdown = tmp_dir / "normalized.md"
        override_file = tmp_dir / "template-overrides.css"
        normalized_markdown.write_text(
            normalize_markdown(input_file.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        override_file.write_text(override_css, encoding="utf-8")

        command = [
            pandoc,
            str(normalized_markdown),
            "--from",
            PANDOC_MARKDOWN_FORMAT,
            "--to",
            "html5",
            "--standalone",
            "--embed-resources",
            "--mathml",
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
            "--resource-path",
            os.pathsep.join(str(directory) for directory in resource_directories),
        ]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
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
