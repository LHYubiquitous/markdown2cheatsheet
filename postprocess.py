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
    5. Wrap tables so the browser treats them as column-safe units.
    6. Classify MathML by source complexity for baseline size control.
    7. Inject an offline responsive helper that fits MathML to the actual
       browser column width and turns tables into labelled cards when columns
       are too narrow for a readable grid.
    8. Remove Pandoc's obsolete external html5shiv fallback so the generated
       document remains fully offline.
"""

import html as html_module
import re
import sys

_MATH = re.compile(r'<math\b(?P<attrs>[^>]*)>(?P<body>.*?)</math>', re.DOTALL | re.IGNORECASE)
_TEX_ANNOTATION = re.compile(
    r'<annotation\b[^>]*encoding="application/x-tex"[^>]*>(?P<tex>.*?)</annotation>',
    re.DOTALL | re.IGNORECASE,
)
_LEGACY_HTML5SHIV = re.compile(
    r'<!--\[if\s+lt\s+IE\s+9\]>.*?'
    r'<script\b[^>]*\bsrc=["\'][^"\']*html5shiv[^"\']*["\'][^>]*>'
    r'\s*</script>\s*<!\[endif\]-->\s*',
    re.DOTALL | re.IGNORECASE,
)

_RESPONSIVE_LAYOUT_SCRIPT = r'''<script id="md2cheatsheet-layout-fit">
(() => {
  "use strict";

  const ROOT_SELECTOR = ".content-wrapper";
  const CARD_COLUMN_THRESHOLD = 300;
  let scheduledFrame = 0;

  function columnMetrics(root) {
    const style = getComputedStyle(root);
    const count = Math.max(1, Number.parseInt(style.columnCount, 10) || 1);
    const gap = Number.parseFloat(style.columnGap) || 0;
    const width = (root.getBoundingClientRect().width - gap * (count - 1)) / count;
    return { count, gap, width };
  }

  function visibleCellText(cell) {
    const clone = cell.cloneNode(true);
    clone.querySelectorAll("annotation").forEach((node) => node.remove());
    return (clone.textContent || "").replace(/\s+/g, " ").trim();
  }

  function boundedShares(scores, minimum, maximum) {
    const total = scores.reduce((sum, score) => sum + score, 0) || 1;
    let shares = scores.map((score) => Math.min(maximum, Math.max(minimum, score / total)));
    const adjustedTotal = shares.reduce((sum, share) => sum + share, 0) || 1;
    shares = shares.map((share) => share / adjustedTotal);
    return shares;
  }

  function installWeightedColumns(table, columnCount) {
    table.querySelectorAll("colgroup[data-responsive-columns]").forEach((node) => node.remove());
    const scores = Array(columnCount).fill(3);
    table.querySelectorAll("tr").forEach((row) => {
      [...row.children].forEach((cell, index) => {
        if (index >= columnCount) return;
        const text = visibleCellText(cell);
        const longestToken = text.split(/\s+/).reduce((longest, token) => Math.max(longest, token.length), 0);
        const texLength = [...cell.querySelectorAll('annotation[encoding="application/x-tex"]')]
          .reduce((longest, annotation) => Math.max(longest, (annotation.textContent || "").length), 0);
        const demand = Math.min(100, Math.max(6, text.length, longestToken * 1.15, texLength * 0.8));
        scores[index] = Math.max(scores[index], Math.sqrt(demand));
      });
    });

    const minimum = columnCount <= 3 ? 0.16 : 0.1;
    const maximum = columnCount <= 2 ? 0.72 : 0.55;
    const shares = boundedShares(scores, minimum, maximum);
    const group = document.createElement("colgroup");
    group.dataset.responsiveColumns = "";
    shares.forEach((share) => {
      const column = document.createElement("col");
      column.style.width = `${(share * 100).toFixed(2)}%`;
      group.append(column);
    });
    table.prepend(group);
  }

  function adaptTablesToColumns(root, metrics) {
    root.querySelectorAll(".table-wrapper").forEach((wrapper) => {
      const table = wrapper.querySelector(":scope > table");
      if (!table) return;
      const headerCells = [...table.querySelectorAll("thead tr:first-child > th")];
      const firstRow = table.querySelector("tr");
      const columnCount = headerCells.length || firstRow?.children.length || 1;
      const labels = headerCells.map((cell, index) => visibleCellText(cell) || `Column ${index + 1}`);
      table.querySelectorAll("tbody tr").forEach((row) => {
        [...row.children].forEach((cell, index) => {
          cell.dataset.label = labels[index] || `Column ${index + 1}`;
        });
      });

      const useCards = columnCount >= 5 && metrics.width < CARD_COLUMN_THRESHOLD;
      wrapper.classList.toggle("table-cards", useCards);
      if (useCards) {
        table.querySelectorAll("colgroup[data-responsive-columns]").forEach((node) => node.remove());
      } else {
        installWeightedColumns(table, columnCount);
      }
    });
  }

  function ensureMathViewport(math) {
    const isBlock = math.getAttribute("display") === "block";
    let viewport = math.parentElement;
    if (!viewport?.classList.contains("math-viewport")) {
      viewport = document.createElement("span");
      viewport.className = "math-viewport";
      math.before(viewport);
      viewport.append(math);
    }
    viewport.classList.toggle("math-viewport-block", isBlock);
    viewport.classList.toggle("math-viewport-inline", !isBlock);
    return viewport;
  }

  function renderedMathBox(math) {
    const elements = [math, ...math.querySelectorAll("*:not(annotation):not(annotation *)")];
    const rectangles = elements
      .map((element) => element.getBoundingClientRect())
      .filter((rectangle) => rectangle.width || rectangle.height);
    if (!rectangles.length) return { width: 0, height: 0 };
    const left = Math.min(...rectangles.map((rectangle) => rectangle.left));
    const right = Math.max(...rectangles.map((rectangle) => rectangle.right));
    const top = Math.min(...rectangles.map((rectangle) => rectangle.top));
    const bottom = Math.max(...rectangles.map((rectangle) => rectangle.bottom));
    return { width: right - left, height: bottom - top };
  }

  function availableMathWidth(math, metrics) {
    const cell = math.closest("th, td");
    if (!cell) return Math.max(24, metrics.width - 2);
    const style = getComputedStyle(cell);
    return Math.max(
      24,
      cell.clientWidth - (Number.parseFloat(style.paddingLeft) || 0)
        - (Number.parseFloat(style.paddingRight) || 0) - 2,
    );
  }

  function fitMathToColumns(root, metrics) {
    const formulas = [...root.querySelectorAll("math")];
    formulas.forEach((math) => {
      const viewport = ensureMathViewport(math);
      viewport.style.removeProperty("width");
      viewport.style.removeProperty("height");
      viewport.classList.remove("math-viewport-fitted");
      math.style.removeProperty("font-size");
      math.style.removeProperty("transform");
      math.style.removeProperty("transform-origin");
      math.style.removeProperty("left");
      math.style.removeProperty("margin");
      math.style.removeProperty("position");
      math.classList.remove("math-fitted");
    });

    formulas.forEach((math) => {
      const viewport = ensureMathViewport(math);
      const available = availableMathWidth(math, metrics);
      const rendered = renderedMathBox(math);
      if (!(rendered.width > available + 0.75)) return;
      const scale = (available / rendered.width) * 0.98;
      const scaledWidth = rendered.width * scale;
      const scaledHeight = rendered.height * scale;
      math.style.transform = `scale(${scale.toFixed(6)})`;
      math.style.transformOrigin = "top left";
      viewport.style.height = `${scaledHeight.toFixed(3)}px`;
      if (math.getAttribute("display") === "block") {
        math.style.position = "relative";
        math.style.left = `${Math.max(0, (available - scaledWidth) / 2).toFixed(3)}px`;
        math.style.margin = "0";
      } else {
        viewport.style.width = `${scaledWidth.toFixed(3)}px`;
      }
      viewport.classList.add("math-viewport-fitted");
      math.classList.add("math-fitted");
    });
  }

  function applyResponsiveLayout() {
    const root = document.querySelector(ROOT_SELECTOR);
    if (!root) return;
    const metrics = columnMetrics(root);
    adaptTablesToColumns(root, metrics);
    fitMathToColumns(root, metrics);
  }

  function scheduleResponsiveLayout() {
    cancelAnimationFrame(scheduledFrame);
    scheduledFrame = requestAnimationFrame(() => {
      applyResponsiveLayout();
      scheduledFrame = requestAnimationFrame(applyResponsiveLayout);
    });
  }

  scheduleResponsiveLayout();
  window.addEventListener("load", scheduleResponsiveLayout, { once: true });
  window.addEventListener("resize", scheduleResponsiveLayout, { passive: true });
  window.addEventListener("beforeprint", () => {
    applyResponsiveLayout();
    applyResponsiveLayout();
  });
  window.addEventListener("afterprint", scheduleResponsiveLayout);
  if (document.fonts?.ready) document.fonts.ready.then(scheduleResponsiveLayout);
})();
</script>'''


def compress_indent(m: re.Match) -> str:
    """Halve groups of 4 leading spaces in a code line, preserving remainder."""
    prefix, spaces = m.group(1), m.group(2)
    n = len(spaces)
    return prefix + ' ' * ((n // 4) * 2 + (n % 4))


def classify_math(m: re.Match) -> str:
    """Add deterministic size classes without relying on browser scripts."""
    attrs = m.group('attrs')
    body = m.group('body')
    annotation = _TEX_ANNOTATION.search(body)
    if annotation is None:
        return m.group(0)

    tex = html_module.unescape(annotation.group('tex'))
    compact_length = len(re.sub(r'\s+', '', tex))
    is_display = bool(re.search(r'\bdisplay="block"', attrs, re.IGNORECASE))
    size_class = ''
    if is_display:
        if compact_length > 180:
            size_class = 'math-xlong'
        elif compact_length > 90:
            size_class = 'math-long'
        elif compact_length > 60:
            size_class = 'math-medium'
    elif compact_length > 120:
        size_class = 'math-inline-xlong'
    elif compact_length > 80:
        size_class = 'math-inline-long'
    elif compact_length > 45:
        size_class = 'math-inline-medium'

    if not size_class:
        return m.group(0)
    if re.search(r'\bclass="', attrs, re.IGNORECASE):
        attrs = re.sub(
            r'\bclass="([^"]*)"',
            lambda class_match: f'class="{class_match.group(1)} {size_class}"',
            attrs,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        attrs = f' class="{size_class}"' + attrs
    return f'<math{attrs}>{body}</math>'


def process(html: str) -> str:
    # Older Pandoc standalone templates inject a CDN-hosted IE8 shim.  Modern
    # browsers do not need it, and removing it keeps the output self-contained.
    html = _LEGACY_HTML5SHIV.sub('', html)

    # Remove pandoc-generated title block (filename shown as first h1)
    html = re.sub(r'<header[^>]*id="title-block-header"[^>]*>.*?</header>\s*', '', html, flags=re.DOTALL)

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

    # A wrapper gives the CSS fragmentation engine a stable unit to keep in
    # one column.  Rows remain individually protected as a fallback for tables
    # taller than a column.
    html = re.sub(
        r'(<table(?:\s[^>]*)?>.*?</table>)',
        r'<div class="table-wrapper">\1</div>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    html = _MATH.sub(classify_math, html)

    # Wrap body content in .content-wrapper for CSS multi-column layout.
    body_start = html.find('<body>')
    body_end = html.rfind('</body>')
    if body_start != -1 and body_end != -1:
        body_content = html[body_start + 6:body_end]
        new_body = (
            '<body>\n<div class="content-wrapper">\n'
            + body_content
            + '\n</div>\n'
            + _RESPONSIVE_LAYOUT_SCRIPT
            + '\n</body>'
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
