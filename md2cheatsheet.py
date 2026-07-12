#!/usr/bin/env python3
"""CLI entry point for markdown2cheatsheet."""

from __future__ import annotations

import argparse
import json
import sys

from converter_core import convert_markdown, list_templates
from template_presets import (
    COLOR_TEMPLATES,
    CJK_FONT_TEMPLATES,
    DEFAULT_COLOR_TEMPLATE,
    DEFAULT_COLUMNS,
    DEFAULT_CJK_FONT,
    DEFAULT_CODE_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_LINE_HEIGHT,
    DEFAULT_LATIN_FONT,
    CODE_FONT_TEMPLATES,
    FONT_SIZE_TEMPLATES,
    LATIN_FONT_TEMPLATES,
    LINE_HEIGHT_TEMPLATES,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Markdown into a print-ready cheatsheet HTML."
    )
    parser.add_argument("input", nargs="?", help="Input markdown file")
    parser.add_argument("output", nargs="?", help="Output HTML path")
    parser.add_argument(
        "--columns",
        type=int,
        choices=(2, 3, 4, 5, 6),
        default=DEFAULT_COLUMNS,
        help="Number of layout columns",
    )
    parser.add_argument(
        "--color-template",
        choices=tuple(COLOR_TEMPLATES.keys()),
        default=DEFAULT_COLOR_TEMPLATE,
        help="Color preset to apply",
    )
    parser.add_argument(
        "--latin-font",
        choices=tuple(LATIN_FONT_TEMPLATES.keys()),
        default=DEFAULT_LATIN_FONT,
        help="English/Latin body font",
    )
    parser.add_argument(
        "--cjk-font",
        choices=tuple(CJK_FONT_TEMPLATES.keys()),
        default=DEFAULT_CJK_FONT,
        help="Chinese body font",
    )
    parser.add_argument(
        "--code-font",
        choices=tuple(CODE_FONT_TEMPLATES.keys()),
        default=DEFAULT_CODE_FONT,
        help="Code font",
    )
    parser.add_argument(
        "--font-size",
        choices=tuple(FONT_SIZE_TEMPLATES.keys()),
        default=DEFAULT_FONT_SIZE,
        help="Overall font size preset",
    )
    parser.add_argument(
        "--line-height",
        choices=tuple(LINE_HEIGHT_TEMPLATES.keys()),
        default=DEFAULT_LINE_HEIGHT,
        help="Overall line-height preset",
    )
    parser.add_argument("--title", help="Override the generated page title")
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Print available columns, color templates, and font templates",
    )
    parser.add_argument(
        "--list-templates-json",
        action="store_true",
        help="Print available template metadata as JSON",
    )
    return parser


def print_templates(as_json: bool) -> None:
    data = list_templates()
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print("Columns:")
    print("  2, 3, 4, 5, 6")
    print("")
    print("Color templates:")
    for name, meta in data["colors"].items():
        print(f"  {name:<10} {meta['label']} - {meta['description']}")
    print("")
    print("Latin fonts:")
    for name, meta in data["latinFonts"].items():
        print(f"  {name:<18} {meta['label']} - {meta['description']}")
    print("")
    print("Chinese fonts:")
    for name, meta in data["cjkFonts"].items():
        print(f"  {name:<18} {meta['label']} - {meta['description']}")
    print("")
    print("Code fonts:")
    for name, meta in data["codeFonts"].items():
        print(f"  {name:<10} {meta['label']} - {meta['description']}")
    print("")
    print("Font sizes:")
    for name, meta in data["fontSizes"].items():
        print(f"  {name:<10} {meta['label']} - {meta['description']}")
    print("")
    print("Line heights:")
    for name, meta in data["lineHeights"].items():
        print(f"  {name:<10} {meta['label']} - {meta['description']}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_templates or args.list_templates_json:
        print_templates(as_json=args.list_templates_json)
        return 0

    if not args.input:
        parser.error("the following arguments are required: input")

    try:
        output = convert_markdown(
            args.input,
            args.output,
            columns=args.columns,
            color_template=args.color_template,
            latin_font=args.latin_font,
            cjk_font=args.cjk_font,
            code_font=args.code_font,
            font_size=args.font_size,
            line_height=args.line_height,
            title=args.title,
        )
    except Exception as exc:  # noqa: BLE001 - keep CLI messages friendly
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Done: {output}")
    print("")
    print("To print as PDF:")
    print("  1. Open the generated HTML in a browser")
    print("  2. Press Ctrl+P (Mac: Cmd+P)")
    print("  3. Paper: A4, Orientation: Landscape, Margins: Minimum")
    print("  4. Uncheck 'Headers and footers'")
    print("  5. Save as PDF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
