#!/usr/bin/env python3
"""Shared Pandoc version requirements and helpers."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

MIN_PANDOC_VERSION = "3.10"


def extract_version(raw_text: str) -> str | None:
    match = re.search(r"(\d+(?:\.\d+)+)", raw_text)
    return match.group(1) if match else None


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def is_version_at_least(version: str, minimum: str = MIN_PANDOC_VERSION) -> bool:
    return version_key(version) >= version_key(minimum)


def detect_pandoc_version(executable: str | Path) -> str | None:
    try:
        result = subprocess.run(
            [str(executable), "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    first_line = result.stdout.splitlines()[0] if result.stdout else ""
    return extract_version(first_line)


__all__ = [
    "MIN_PANDOC_VERSION",
    "detect_pandoc_version",
    "extract_version",
    "is_version_at_least",
    "version_key",
]
