#!/usr/bin/env python3
"""Version helpers shared by local builds and CI."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_VERSION = "0.0.0"


def _run_git_command(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def get_exact_tag() -> str | None:
    return _run_git_command(["describe", "--tags", "--exact-match"])


def get_short_commit() -> str | None:
    return _run_git_command(["rev-parse", "--short", "HEAD"])


def normalize_version(tag: str) -> str:
    return tag[1:] if tag.startswith("v") else tag


def get_version() -> str:
    env_version = os.getenv("MARKDOWN2CHEATSHEET_VERSION", "").strip()
    if env_version:
        return env_version

    exact_tag = get_exact_tag()
    if exact_tag:
        return normalize_version(exact_tag)

    short_commit = get_short_commit()
    if short_commit:
        return f"{DEFAULT_VERSION}-dev+{short_commit}"

    return f"{DEFAULT_VERSION}-dev"


def get_release_tag() -> str:
    exact_tag = get_exact_tag()
    if exact_tag:
        return exact_tag
    return f"v{get_version()}"


def get_filename_version() -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", get_release_tag())

