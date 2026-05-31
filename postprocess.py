#!/usr/bin/env python3
"""
postprocess.py — Post-process pandoc HTML output for cheatsheet layout.

Usage:
    python postprocess.py <input.html> <output.html>

Transformations applied:
    1. Strip leftover frontmatter paragraphs (created:/updated: fields).
    2. Remove pandoc-generated <colgroup> blocks whose inline col widths
       override CSS table-layout, forcing equal-width columns.
    3. Compress leading spaces in code lines: every 4 spaces -> 2 spaces.
       (CSS tab-size has no effect on space characters.)
    4. Wrap <body> content in <div class="content-wrapper"> required for
       the multi-column CSS layout.
"""

import re
import sys


def compress_indent(m: re.Match) -> str:
    """Halve groups of 4 leading spaces in a code line, preserving remainder."""
    prefix, spaces = m.group(1), m.group(2)
    n = len(spaces)
    return prefix + ' ' * ((n // 4) * 2 + (n % 4))


def process(html: str) -> str:
    # Remove frontmatter residue
    html = re.sub(r'<p>created:.*?</p>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<p>updated:.*?</p>\s*', '', html, flags=re.DOTALL)

    # Remove <colgroup> blocks injected by pandoc.
    # pandoc writes <col style="width: 33%"> which overrides CSS table-layout:auto.
    html = re.sub(r'<colgroup>.*?</colgroup>\s*', '', html, flags=re.DOTALL)

    # Compress leading spaces in syntax-highlighted code lines.
    # pandoc wraps each line in <span id="cbN-M"><a ...></a>CONTENT</span>.
    # The spaces immediately after </a> are the indentation.
    html = re.sub(
        r'(<span id="cb\d+-\d+"><a[^>]*></a>)([ ]+)',
        compress_indent,
        html,
    )

    # Wrap body content in .content-wrapper for CSS multi-column layout.
    body_start = html.find('<body>')
    body_end = html.rfind('</body>')
    if body_start != -1 and body_end != -1:
        body_content = html[body_start + 6:body_end]
        new_body = (
            '<body>\n<div class="content-wrapper">\n'
            + body_content
            + '\n</div>\n</body>'
        )
        html = html[:body_start] + new_body + html[body_end + 7:]

    return html


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: python {sys.argv[0]} <input.html> <output.html>')
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        html = f.read()

    html = process(html)

    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Done: {sys.argv[2]}')
