"""Conservative Markdown cleanup for common note-taking shorthand.

The converter accepts notes written for editors such as Obsidian, where block
elements are often recognized without the blank lines required by Pandoc's
default Markdown reader.  This module inserts only structural blank lines; it
does not rewrite prose, math, or fenced code.
"""

from __future__ import annotations

import re


_ATX_HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+|$)")
_BLOCKQUOTE = re.compile(r"^ {0,3}>")
_LIST_ITEM = re.compile(r"^(?P<indent>[ \t]*)(?:[-+*]|\d+[.)])[ \t]+")
_FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})")
_PIPE_ROW = re.compile(r"^ {0,3}\|?.*\|.*\|?[ \t]*$")
_PIPE_SEPARATOR = re.compile(
    r"^ {0,3}\|?[ \t]*:?-{3,}:?[ \t]*(?:\|[ \t]*:?-{3,}:?[ \t]*)+\|?[ \t]*$"
)
_RAW_BLOCK_START = re.compile(r"^ {0,3}<(pre|script|style)(?:\s|>)", re.IGNORECASE)
_RAW_BLOCK_END = {
    "pre": re.compile(r"</pre\s*>", re.IGNORECASE),
    "script": re.compile(r"</script\s*>", re.IGNORECASE),
    "style": re.compile(r"</style\s*>", re.IGNORECASE),
}
_MARKDOWN_INLINE_TOKEN = re.compile(r"`+|(?<!\\)\$\$|(?<!\\)\$")
_NESTED_TEXT_BOLD = re.compile(r"\\text\{\\textbf\{([^{}]*)\}\}")
_NOT_MID = re.compile(r"\\not\s*\\mid\b")
_COLLAPSED_ROW_COMMAND = re.compile(r"(?<!\\)\\{3}(?=[A-Za-z])")
_TRAILING_ARRAY_HLINE = re.compile(
    r"\\\\\s*\\hline\s*(?=\\end\{array\})"
)


def _rewrite_mathml_compatible_tex(tex: str) -> str:
    """Rewrite known Pandoc texmath incompatibilities without changing meaning."""
    tex = _NESTED_TEXT_BOLD.sub(r"\\text{\1}", tex)
    tex = _COLLAPSED_ROW_COMMAND.sub(lambda _: "\\\\" + " " + "\\", tex)
    tex = _TRAILING_ARRAY_HLINE.sub(
        lambda match: "\n" * match.group(0).count("\n"),
        tex,
    )
    return _NOT_MID.sub(r"\\nmid", tex)


def _normalize_latex_compatibility(
    lines: list[str], protected: list[bool]
) -> list[str]:
    """Apply compatibility rewrites to complete Markdown math regions."""
    output_parts: list[str] = []
    math_parts: list[str] = []
    math_delimiter: str | None = None
    code_delimiter: str | None = None

    for index, line in enumerate(lines):
        if protected[index]:
            if math_delimiter is not None:
                output_parts.append(_rewrite_mathml_compatible_tex("".join(math_parts)))
                math_parts.clear()
            output_parts.append(line)
            if index + 1 < len(lines):
                output_parts.append("\n")
            code_delimiter = None
            continue

        token_matches = list(_MARKDOWN_INLINE_TOKEN.finditer(line))
        cursor = 0
        for token_index, token_match in enumerate(token_matches):
            segment = line[cursor:token_match.start()]
            if math_delimiter is not None:
                math_parts.append(segment)
            else:
                output_parts.append(segment)

            token = token_match.group(0)

            if code_delimiter is not None:
                output_parts.append(token)
                if token == code_delimiter:
                    code_delimiter = None
            elif token.startswith("`"):
                if math_delimiter is None:
                    output_parts.append(token)
                    code_delimiter = token
                else:
                    math_parts.append(token)
            elif math_delimiter is None:
                should_open = token == "$$"
                if token == "$":
                    # Inline math cannot safely continue across a physical line.
                    # Require a closing dollar outside a later code span so
                    # ordinary prose such as ``Price is $5`` stays untouched.
                    future_code_delimiter: str | None = None
                    has_closing_dollar = False
                    for future_match in token_matches[token_index + 1:]:
                        future_token = future_match.group(0)
                        if future_code_delimiter is not None:
                            if future_token == future_code_delimiter:
                                future_code_delimiter = None
                        elif future_token.startswith("`"):
                            future_code_delimiter = future_token
                        elif future_token == "$":
                            has_closing_dollar = True
                            break
                    should_open = has_closing_dollar

                output_parts.append(token)
                if should_open:
                    math_delimiter = token
            elif token == math_delimiter:
                output_parts.append(
                    _rewrite_mathml_compatible_tex("".join(math_parts))
                )
                math_parts.clear()
                output_parts.append(token)
                math_delimiter = None
            else:
                math_parts.append(token)

            cursor = token_match.end()

        tail = line[cursor:]
        if math_delimiter is not None:
            math_parts.append(tail)
        else:
            output_parts.append(tail)
        if index + 1 < len(lines):
            if math_delimiter is not None:
                math_parts.append("\n")
            else:
                output_parts.append("\n")

    if math_parts:
        output_parts.append(_rewrite_mathml_compatible_tex("".join(math_parts)))

    output = "".join(output_parts).split("\n")
    if len(output) != len(lines):
        raise RuntimeError("LaTeX compatibility normalization changed line count")
    return output


def _protected_lines(lines: list[str]) -> tuple[list[bool], set[int], set[int]]:
    """Mark YAML, fenced code, and raw code-like HTML as untouchable."""
    protected = [False] * len(lines)
    fence_starts: set[int] = set()
    fence_ends: set[int] = set()

    index = 0
    if lines and lines[0].strip() == "---":
        protected[0] = True
        index = 1
        while index < len(lines):
            protected[index] = True
            if lines[index].strip() in {"---", "..."}:
                index += 1
                break
            index += 1

    active_fence: tuple[str, int] | None = None
    raw_tag: str | None = None
    for line_number in range(index, len(lines)):
        line = lines[line_number]
        if raw_tag is not None:
            protected[line_number] = True
            if _RAW_BLOCK_END[raw_tag].search(line):
                raw_tag = None
            continue

        if active_fence is not None:
            protected[line_number] = True
            marker, minimum_length = active_fence
            if re.match(rf"^[ \t]*{re.escape(marker)}{{{minimum_length},}}[ \t]*$", line):
                fence_ends.add(line_number)
                active_fence = None
            continue

        raw_match = _RAW_BLOCK_START.match(line)
        if raw_match:
            raw_tag = raw_match.group(1).lower()
            protected[line_number] = True
            if _RAW_BLOCK_END[raw_tag].search(line):
                raw_tag = None
            continue

        fence_match = _FENCE.match(line)
        if fence_match:
            fence = fence_match.group("fence")
            active_fence = (fence[0], len(fence))
            protected[line_number] = True
            fence_starts.add(line_number)

    return protected, fence_starts, fence_ends


def _table_ranges(lines: list[str], protected: list[bool]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    index = 0
    while index + 1 < len(lines):
        if (
            not protected[index]
            and not protected[index + 1]
            and _PIPE_ROW.match(lines[index])
            and _PIPE_SEPARATOR.match(lines[index + 1])
        ):
            end = index + 1
            while (
                end + 1 < len(lines)
                and not protected[end + 1]
                and lines[end + 1].strip()
                and _PIPE_ROW.match(lines[end + 1])
            ):
                end += 1
            ranges.append((index, end))
            index = end + 1
            continue
        index += 1
    return ranges


def _needs_blank_before(lines: list[str], index: int) -> bool:
    return index > 0 and bool(lines[index - 1].strip())


def normalize_markdown(markdown: str) -> str:
    """Insert missing blank lines around recognizable Markdown blocks.

    The operation is idempotent.  Fenced code, YAML front matter, and raw
    ``pre``/``script``/``style`` blocks are preserved byte-for-byte apart from
    normalizing line endings to ``\n``.
    """
    if not markdown:
        return markdown

    had_trailing_newline = markdown.endswith(("\n", "\r"))
    lines = markdown.splitlines()
    protected, fence_starts, fence_ends = _protected_lines(lines)
    lines = _normalize_latex_compatibility(lines, protected)
    tables = _table_ranges(lines, protected)
    table_starts = {start for start, _ in tables}
    table_ends = {end for _, end in tables}
    insert_before: set[int] = set()

    in_list = False
    in_blockquote = False
    for index, line in enumerate(lines):
        if protected[index]:
            in_list = False
            in_blockquote = False
            continue

        stripped = line.strip()
        if not stripped:
            in_list = False
            in_blockquote = False
            continue

        list_match = _LIST_ITEM.match(line)
        is_top_level_list_item = bool(
            list_match and len(list_match.group("indent").expandtabs(4)) <= 3
        )

        if in_list and not list_match and not line.startswith(("  ", "\t")):
            insert_before.add(index)
            in_list = False

        is_blockquote = bool(_BLOCKQUOTE.match(line))
        if in_blockquote and not is_blockquote:
            insert_before.add(index)
            in_blockquote = False
        if is_blockquote:
            in_blockquote = True

        if is_top_level_list_item:
            if _needs_blank_before(lines, index):
                previous = _LIST_ITEM.match(lines[index - 1])
                if previous is None:
                    insert_before.add(index)
            in_list = True

        if (
            _ATX_HEADING.match(line)
            or (is_blockquote and not _BLOCKQUOTE.match(lines[index - 1] if index else ""))
            or index in table_starts
        ) and _needs_blank_before(lines, index):
            insert_before.add(index)

    for start in fence_starts:
        if _needs_blank_before(lines, start):
            insert_before.add(start)
    for end in fence_ends:
        if end + 1 < len(lines) and lines[end + 1].strip():
            insert_before.add(end + 1)
    for end in table_ends:
        if end + 1 < len(lines) and lines[end + 1].strip():
            insert_before.add(end + 1)

    output: list[str] = []
    for index, line in enumerate(lines):
        if index in insert_before and output and output[-1].strip():
            output.append("")
        output.append(line)

    normalized = "\n".join(output)
    if had_trailing_newline:
        normalized += "\n"
    return normalized


__all__ = ["normalize_markdown"]
