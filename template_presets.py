#!/usr/bin/env python3
"""Template presets for markdown2cheatsheet."""

from __future__ import annotations

from copy import deepcopy


DEFAULT_COLOR_TEMPLATE = "yubiquitous"
DEFAULT_COLUMNS = 4
DEFAULT_LATIN_FONT = "arial"
DEFAULT_CJK_FONT = "microsoft-yahei"
DEFAULT_CODE_FONT = "system-code"
DEFAULT_FONT_SIZE = "6"
DEFAULT_LINE_HEIGHT = "1.0"


COLOR_TEMPLATES = {
    "yubiquitous": {
        "label": "Yubiquitous",
        "description": "The current original version of the project.",
        "css": {
            "--column-rule-color": "#ccc",
            "--text-color": "#111",
            "--body-bg": "#fff",
            "--h1-color": "#000",
            "--h2-color": "#09305a",
            "--h2-bg": "#cfe0f5",
            "--h2-border": "#072050",
            "--h3-color": "#1250a0",
            "--h4-color": "#1a6bbf",
            "--h5-color": "#2077cc",
            "--mark-bg": "#fffa698d",
            "--mark-color": "#8b0000",
            "--inline-code-bg": "#f0f0f0",
            "--inline-code-color": "#222",
            "--pre-bg": "#f6f8fa",
            "--pre-border": "#ddd",
            "--pre-border-left": "#ccc",
            "--table-head-bg": "#e8e8e8",
            "--table-head-color": "#111",
            "--table-border": "#ccc",
            "--table-stripe-bg": "#f7f9fc",
            "--blockquote-border": "#6d6d6d",
            "--blockquote-bg": "#f0f4ff",
            "--blockquote-color": "#333",
            "--hr-color": "#ccc",
            "--bullet-color": "#666",
            "--figcaption-color": "#666",
        },
    },
    "grayscale": {
        "label": "Grayscale",
        "description": "Pure black, white, and gray for clean printing.",
        "css": {
            "--column-rule-color": "#bcbcbc",
            "--text-color": "#111",
            "--body-bg": "#fff",
            "--h1-color": "#000",
            "--h2-color": "#111",
            "--h2-bg": "#efefef",
            "--h2-border": "#444",
            "--h3-color": "#333",
            "--h4-color": "#444",
            "--h5-color": "#555",
            "--mark-bg": "#e8e8e8",
            "--mark-color": "#000",
            "--inline-code-bg": "#f1f1f1",
            "--inline-code-color": "#222",
            "--pre-bg": "#f7f7f7",
            "--pre-border": "#d7d7d7",
            "--pre-border-left": "#aaaaaa",
            "--table-head-bg": "#ececec",
            "--table-head-color": "#111",
            "--table-border": "#c7c7c7",
            "--table-stripe-bg": "#fafafa",
            "--blockquote-border": "#777",
            "--blockquote-bg": "#f4f4f4",
            "--blockquote-color": "#222",
            "--hr-color": "#c7c7c7",
            "--bullet-color": "#555",
            "--figcaption-color": "#666",
        },
    },
    "forest": {
        "label": "Forest",
        "description": "Muted green palette for long study sessions.",
        "css": {
            "--column-rule-color": "#b8c6b2",
            "--text-color": "#152015",
            "--body-bg": "#fcfdf9",
            "--h1-color": "#1d2b1d",
            "--h2-color": "#1a4d2e",
            "--h2-bg": "#d9ead3",
            "--h2-border": "#2f6b3f",
            "--h3-color": "#2d6a4f",
            "--h4-color": "#3f8f63",
            "--h5-color": "#4a9f6c",
            "--mark-bg": "#f1f7af",
            "--mark-color": "#5a4a00",
            "--inline-code-bg": "#edf3ec",
            "--inline-code-color": "#223022",
            "--pre-bg": "#f4f8f1",
            "--pre-border": "#cfdbc8",
            "--pre-border-left": "#8aa57f",
            "--table-head-bg": "#e2eddf",
            "--table-head-color": "#1d2b1d",
            "--table-border": "#bcccb7",
            "--table-stripe-bg": "#f6faf4",
            "--blockquote-border": "#4f7c57",
            "--blockquote-bg": "#eef6ed",
            "--blockquote-color": "#27402b",
            "--hr-color": "#bcccb7",
            "--bullet-color": "#4f7c57",
            "--figcaption-color": "#5e6d5b",
        },
    },
    "sunset": {
        "label": "Sunset",
        "description": "Warm orange-red palette for emphasis-heavy notes.",
        "css": {
            "--column-rule-color": "#d4c0b2",
            "--text-color": "#241815",
            "--body-bg": "#fffaf7",
            "--h1-color": "#351b13",
            "--h2-color": "#7b2d26",
            "--h2-bg": "#f6d6c9",
            "--h2-border": "#9e3d2b",
            "--h3-color": "#b44b35",
            "--h4-color": "#c9673f",
            "--h5-color": "#d97946",
            "--mark-bg": "#ffe7a5",
            "--mark-color": "#7d3f00",
            "--inline-code-bg": "#f8ece6",
            "--inline-code-color": "#38241d",
            "--pre-bg": "#fff4ef",
            "--pre-border": "#e7cdbf",
            "--pre-border-left": "#d08a68",
            "--table-head-bg": "#fbe3d8",
            "--table-head-color": "#351b13",
            "--table-border": "#dcb9a5",
            "--table-stripe-bg": "#fff8f4",
            "--blockquote-border": "#c46f4c",
            "--blockquote-bg": "#fff0e8",
            "--blockquote-color": "#5f3121",
            "--hr-color": "#dcb9a5",
            "--bullet-color": "#b35c3e",
            "--figcaption-color": "#7c6358",
        },
    },
    "navy": {
        "label": "Navy",
        "description": "Deep blue palette for lecture summaries and formulas.",
        "css": {
            "--column-rule-color": "#bcc6d8",
            "--text-color": "#162033",
            "--body-bg": "#fbfcff",
            "--h1-color": "#111c32",
            "--h2-color": "#17365d",
            "--h2-bg": "#dde7f5",
            "--h2-border": "#1f4e79",
            "--h3-color": "#275f94",
            "--h4-color": "#3a76aa",
            "--h5-color": "#4a88ba",
            "--mark-bg": "#fff3a8",
            "--mark-color": "#5f4600",
            "--inline-code-bg": "#edf2f8",
            "--inline-code-color": "#1b2a40",
            "--pre-bg": "#f4f7fb",
            "--pre-border": "#d6e0ec",
            "--pre-border-left": "#8ca4bf",
            "--table-head-bg": "#e4ebf5",
            "--table-head-color": "#162033",
            "--table-border": "#c6d2e2",
            "--table-stripe-bg": "#f8fbff",
            "--blockquote-border": "#4b6a91",
            "--blockquote-bg": "#eef4fb",
            "--blockquote-color": "#243954",
            "--hr-color": "#c6d2e2",
            "--bullet-color": "#4b6a91",
            "--figcaption-color": "#5b6f86",
        },
    },
    "plum": {
        "label": "Plum",
        "description": "A restrained purple-gray palette for humanities notes.",
        "css": {
            "--column-rule-color": "#d1c8d9",
            "--text-color": "#261d2d",
            "--body-bg": "#fdfbfe",
            "--h1-color": "#2c2233",
            "--h2-color": "#5a3f6b",
            "--h2-bg": "#eadff1",
            "--h2-border": "#6d4c82",
            "--h3-color": "#7d5a96",
            "--h4-color": "#8f6ea6",
            "--h5-color": "#9e80b2",
            "--mark-bg": "#fff0a8",
            "--mark-color": "#644400",
            "--inline-code-bg": "#f4eff8",
            "--inline-code-color": "#35293d",
            "--pre-bg": "#faf7fc",
            "--pre-border": "#e3d9ea",
            "--pre-border-left": "#b39cc4",
            "--table-head-bg": "#eee5f4",
            "--table-head-color": "#261d2d",
            "--table-border": "#d5c7df",
            "--table-stripe-bg": "#fcf9fd",
            "--blockquote-border": "#84649b",
            "--blockquote-bg": "#f4eef8",
            "--blockquote-color": "#44314f",
            "--hr-color": "#d5c7df",
            "--bullet-color": "#7d5a96",
            "--figcaption-color": "#70627a",
        },
    },
}


LATIN_FONT_TEMPLATES = {
    "arial": {
        "label": "Arial",
        "description": "Default practical sans-serif choice.",
        "stack": "'Arial', 'Helvetica Neue', Helvetica",
        "em_stack": "'Arial', 'Helvetica Neue', Helvetica",
        "generic": "sans-serif",
    },
    "times-new-roman": {
        "label": "Times New Roman",
        "description": "Classic serif option for denser print reading.",
        "stack": "'Times New Roman', Times, Georgia",
        "em_stack": "'Times New Roman', Times, Georgia",
        "generic": "serif",
    },
    "helvetica": {
        "label": "Helvetica",
        "description": "Neutral sans-serif stack centered on Helvetica.",
        "stack": "'Helvetica Neue', Helvetica, Arial",
        "em_stack": "'Helvetica Neue', Helvetica, Arial",
        "generic": "sans-serif",
    },
    "segoe-ui": {
        "label": "Segoe UI",
        "description": "Windows-friendly sans-serif option.",
        "stack": "'Segoe UI', Arial",
        "em_stack": "'Segoe UI', Arial",
        "generic": "sans-serif",
    },
    "verdana": {
        "label": "Verdana",
        "description": "Wide sans-serif option with strong legibility.",
        "stack": "Verdana, Arial",
        "em_stack": "Verdana, Arial",
        "generic": "sans-serif",
    },
}


CJK_FONT_TEMPLATES = {
    "microsoft-yahei": {
        "label": "微软雅黑",
        "description": "Default Chinese sans-serif option.",
        "stack": "'Microsoft YaHei', 'PingFang SC', 'Heiti SC'",
        "generic": "sans-serif",
    },
    "pingfang-sc": {
        "label": "苹方",
        "description": "Common macOS Chinese sans-serif option.",
        "stack": "'PingFang SC', 'Microsoft YaHei', 'Heiti SC'",
        "generic": "sans-serif",
    },
    "kaiti": {
        "label": "楷体",
        "description": "Traditional Chinese Kai style.",
        "stack": "'Kaiti SC', 'KaiTi', 'STKaiti'",
        "generic": "serif",
    },
    "simsun": {
        "label": "宋体",
        "description": "Traditional Song/Ming style option.",
        "stack": "'SimSun', 'Songti SC', 'STSong'",
        "generic": "serif",
    },
    "lxgw-wenkai": {
        "label": "LXGW WenKai",
        "description": "Open-source Chinese font option.",
        "stack": "'LXGW WenKai', 'Microsoft YaHei', 'PingFang SC'",
        "generic": "sans-serif",
    },
}


CODE_FONT_TEMPLATES = {
    "system-code": {
        "label": "System Default",
        "description": "Cross-platform built-in code fonts.",
        "stack": "Consolas, Menlo, Monaco, 'Courier New', monospace",
    },
    "consolas": {
        "label": "Consolas",
        "description": "Common Windows code font.",
        "stack": "Consolas, Menlo, Monaco, 'Courier New', monospace",
    },
    "menlo": {
        "label": "Menlo",
        "description": "Common macOS code font.",
        "stack": "Menlo, Monaco, Consolas, 'Courier New', monospace",
    },
    "hack": {
        "label": "Hack",
        "description": "Popular developer font with fallbacks.",
        "stack": "'Hack', Consolas, Menlo, Monaco, 'Courier New', monospace",
    },
    "jetbrains-mono": {
        "label": "JetBrains Mono",
        "description": "Popular developer font with wider glyph design.",
        "stack": "'JetBrains Mono', Consolas, Menlo, Monaco, 'Courier New', monospace",
    },
}


def _fmt_num(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:.1f}"


def _font_size_css(base_size: float) -> dict[str, str]:
    return {
        "--base-font-size": f"{_fmt_num(base_size)}pt",
        "--h1-font-size": f"{_fmt_num(base_size + 0.5)}pt",
        "--h2-font-size": f"{_fmt_num(base_size)}pt",
        "--h3-font-size": f"{_fmt_num(max(base_size - 0.5, 3.5))}pt",
        "--h4-font-size": f"{_fmt_num(max(base_size - 1.0, 3.5))}pt",
        "--h5-font-size": f"{_fmt_num(max(base_size - 1.0, 3.5))}pt",
        "--inline-code-font-size": f"{_fmt_num(max(base_size - 2.0, 3.0))}pt",
        "--pre-font-size": f"{_fmt_num(max(base_size - 2.2, 3.0))}pt",
        "--table-font-size": f"{_fmt_num(max(base_size - 1.2, 3.6))}pt",
        "--figcaption-font-size": f"{_fmt_num(max(base_size - 2.0, 3.0))}pt",
    }


FONT_SIZE_TEMPLATES = {
    key: {
        "label": key,
        "description": f"{key}pt base size.",
        "css": _font_size_css(size),
    }
    for key, size in (
        ("8", 8.0),
        ("7.5", 7.5),
        ("7", 7.0),
        ("6.5", 6.5),
        ("6", 6.0),
        ("5.5", 5.5),
        ("5", 5.0),
        ("4.5", 4.5),
        ("4", 4.0),
    )
}


LINE_HEIGHT_TEMPLATES = {
    key: {
        "label": key,
        "description": f"{key} line height.",
        "css": {
            "--body-line-height": key,
            "--code-line-height": code_key,
        },
    }
    for key, code_key in (
        ("0.9", "0.82"),
        ("0.95", "0.86"),
        ("1.0", "0.9"),
        ("1.05", "0.95"),
        ("1.1", "1.0"),
        ("1.15", "1.04"),
        ("1.2", "1.08"),
        ("1.25", "1.12"),
        ("1.3", "1.16"),
    )
}


def _meta(items: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        name: {
            "label": data["label"],
            "description": data["description"],
        }
        for name, data in items.items()
    }


def _compose_font_family(primary_stack: str, secondary_stack: str, generic: str) -> str:
    return f"{primary_stack}, {secondary_stack}, {generic}"


def list_templates() -> dict[str, dict[str, dict[str, str]]]:
    """Return metadata for display in CLI or UI."""
    return {
        "colors": _meta(COLOR_TEMPLATES),
        "latinFonts": _meta(LATIN_FONT_TEMPLATES),
        "cjkFonts": _meta(CJK_FONT_TEMPLATES),
        "codeFonts": _meta(CODE_FONT_TEMPLATES),
        "fontSizes": _meta(FONT_SIZE_TEMPLATES),
        "lineHeights": _meta(LINE_HEIGHT_TEMPLATES),
        "columns": {
            "values": [2, 3, 4, 5, 6],
            "default": DEFAULT_COLUMNS,
        },
        "defaults": {
            "color": DEFAULT_COLOR_TEMPLATE,
            "columns": DEFAULT_COLUMNS,
            "latinFont": DEFAULT_LATIN_FONT,
            "cjkFont": DEFAULT_CJK_FONT,
            "codeFont": DEFAULT_CODE_FONT,
            "fontSize": DEFAULT_FONT_SIZE,
            "lineHeight": DEFAULT_LINE_HEIGHT,
        },
    }


def resolve_template(
    columns: int,
    color_template: str,
    latin_font: str,
    cjk_font: str,
    code_font: str,
    font_size: str,
    line_height: str,
) -> dict[str, str]:
    """Resolve a complete CSS variable override map."""
    if columns not in (2, 3, 4, 5, 6):
        raise ValueError("columns must be one of: 2, 3, 4, 5, 6")
    if color_template not in COLOR_TEMPLATES:
        raise ValueError(f"unknown color template: {color_template}")
    if latin_font not in LATIN_FONT_TEMPLATES:
        raise ValueError(f"unknown latin font: {latin_font}")
    if cjk_font not in CJK_FONT_TEMPLATES:
        raise ValueError(f"unknown cjk font: {cjk_font}")
    if code_font not in CODE_FONT_TEMPLATES:
        raise ValueError(f"unknown code font: {code_font}")
    if font_size not in FONT_SIZE_TEMPLATES:
        raise ValueError(f"unknown font size: {font_size}")
    if line_height not in LINE_HEIGHT_TEMPLATES:
        raise ValueError(f"unknown line height: {line_height}")

    css = deepcopy(COLOR_TEMPLATES[color_template]["css"])
    latin = LATIN_FONT_TEMPLATES[latin_font]
    cjk = CJK_FONT_TEMPLATES[cjk_font]
    code = CODE_FONT_TEMPLATES[code_font]
    css.update(FONT_SIZE_TEMPLATES[font_size]["css"])
    css.update(LINE_HEIGHT_TEMPLATES[line_height]["css"])
    generic = cjk["generic"] if latin["generic"] != cjk["generic"] else latin["generic"]
    css["--body-font"] = _compose_font_family(latin["stack"], cjk["stack"], generic)
    css["--em-font"] = _compose_font_family(latin["em_stack"], cjk["stack"], generic)
    css["--code-font"] = code["stack"]
    css["--columns"] = str(columns)
    return css
