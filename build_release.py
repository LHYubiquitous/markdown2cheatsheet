#!/usr/bin/env python3
"""Build distributable GUI release packages."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import stat
from pathlib import Path

import PyInstaller.__main__

from version import get_filename_version, get_release_tag, get_version


ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
RELEASE_DIR = ROOT_DIR / "release"
PYINSTALLER_CONFIG_DIR = ROOT_DIR / ".pyinstaller"
SPEC_FILE = ROOT_DIR / "Markdown2CheatsheetGUI.spec"
APP_NAME = "Markdown2CheatsheetGUI"


def normalized_platform() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def normalized_arch() -> str:
    machine = platform.machine().lower()
    aliases = {
        "x86_64": "x64",
        "amd64": "x64",
        "aarch64": "arm64",
        "arm64": "arm64",
    }
    return aliases.get(machine, machine)


def release_basename() -> str:
    return f"markdown2cheatsheet-gui-{get_filename_version()}-{normalized_platform()}-{normalized_arch()}"


def add_data_argument(path: Path, target: str | None = None) -> str:
    destination = target if target is not None else path.name
    return f"{path}{os.pathsep}{destination}"


def build(clean: bool) -> None:
    os.environ["PYINSTALLER_CONFIG_DIR"] = str(PYINSTALLER_CONFIG_DIR)
    if clean:
        shutil.rmtree(DIST_DIR, ignore_errors=True)
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        shutil.rmtree(RELEASE_DIR, ignore_errors=True)
        shutil.rmtree(PYINSTALLER_CONFIG_DIR, ignore_errors=True)
        if SPEC_FILE.exists():
            SPEC_FILE.unlink()

    options = [
        str(ROOT_DIR / "gui_app.py"),
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        APP_NAME,
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(ROOT_DIR),
        "--add-data",
        add_data_argument(ROOT_DIR / "gui"),
        "--add-data",
        add_data_argument(ROOT_DIR / "examples"),
        "--add-data",
        add_data_argument(ROOT_DIR / "cheatsheet.css", "."),
    ]
    PyInstaller.__main__.run(options)


def write_text_file(path: Path, content: str, executable: bool = False) -> None:
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def macos_start_script() -> str:
    return """#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/Markdown2CheatsheetGUI"

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

confirm_install() {
  read -r -p "$1 [y/N] " reply
  case "$reply" in
    [yY]|[yY][eE][sS]) return 0 ;;
    *) return 1 ;;
  esac
}

if ! command_exists pandoc; then
  if command_exists brew; then
    if confirm_install "Pandoc is not installed. Install it with Homebrew now?"; then
      brew install pandoc || exit 1
    else
      echo "Pandoc is required. Please install it and run start.command again."
      exit 1
    fi
  else
    echo "Pandoc is required. Please install it and run start.command again."
    exit 1
  fi
fi

xattr -dr com.apple.quarantine "$APP_DIR" >/dev/null 2>&1 || true
xattr -dr com.apple.provenance "$APP_DIR" >/dev/null 2>&1 || true
chmod +x "$APP_DIR/Markdown2CheatsheetGUI" >/dev/null 2>&1 || true

cd "$APP_DIR" || exit 1
./Markdown2CheatsheetGUI
"""


def linux_start_script() -> str:
    return """#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/Markdown2CheatsheetGUI"

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

confirm_install() {
  read -r -p "$1 [y/N] " reply
  case "$reply" in
    [yY]|[yY][eE][sS]) return 0 ;;
    *) return 1 ;;
  esac
}

if ! command_exists pandoc; then
  if command_exists apt-get; then
    if confirm_install "Pandoc is not installed. Install it with apt now?"; then
      sudo apt-get update && sudo apt-get install -y pandoc || exit 1
    else
      echo "Pandoc is required. Please install it and run start.sh again."
      exit 1
    fi
  elif command_exists dnf; then
    if confirm_install "Pandoc is not installed. Install it with dnf now?"; then
      sudo dnf install -y pandoc || exit 1
    else
      echo "Pandoc is required. Please install it and run start.sh again."
      exit 1
    fi
  elif command_exists pacman; then
    if confirm_install "Pandoc is not installed. Install it with pacman now?"; then
      sudo pacman -Sy --noconfirm pandoc-cli || exit 1
    else
      echo "Pandoc is required. Please install it and run start.sh again."
      exit 1
    fi
  else
    echo "Pandoc is required. Please install it and run start.sh again."
    exit 1
  fi
fi

chmod +x "$APP_DIR/Markdown2CheatsheetGUI" >/dev/null 2>&1 || true

cd "$APP_DIR" || exit 1
./Markdown2CheatsheetGUI
"""


def windows_start_script() -> str:
    return """@echo off
cd /d "%~dp0"

where pandoc >nul 2>nul
if errorlevel 1 (
  echo Pandoc is not installed.
  where winget >nul 2>nul
  if errorlevel 1 (
    echo Please install Pandoc and run start.bat again.
    pause
    exit /b 1
  )
  set /p INSTALL_PANDOC=Install Pandoc with winget now? [y/N] 
  if /i "%INSTALL_PANDOC%"=="y" (
    winget install -e --id JohnMacFarlane.Pandoc
  ) else if /i "%INSTALL_PANDOC%"=="yes" (
    winget install -e --id JohnMacFarlane.Pandoc
  ) else (
    echo Pandoc is required.
    pause
    exit /b 1
  )
)

start "" "%~dp0Markdown2CheatsheetGUI\\Markdown2CheatsheetGUI.exe"
"""


def release_readme() -> str:
    platform_name = normalized_platform()
    version = get_release_tag()
    if platform_name == "macos":
        start_name = "start.command"
        extra = (
            "If macOS shows a security warning the first time, right-click "
            "`start.command` and choose Open."
        )
    elif platform_name == "windows":
        start_name = "start.bat"
        extra = "If Windows SmartScreen appears, choose More info and then Run anyway."
    else:
        start_name = "start.sh"
        extra = "If needed, run `chmod +x start.sh` once and then double-click or run it."

    return "\n".join(
        [
            "Markdown2Cheatsheet GUI",
            "",
            f"Version: {version}",
            "",
            f"Start: {start_name}",
            "",
            "Usage:",
            "1. Extract this archive fully.",
            f"2. Launch `{start_name}`.",
            "3. Your browser will open the local GUI automatically.",
            "",
            extra,
            "",
            "GitHub:",
            "https://github.com/LHYubiquitous/markdown2cheatsheet.git",
            "",
        ]
    )


def stage_release_directory() -> Path:
    release_root = RELEASE_DIR / release_basename()
    if release_root.exists():
        shutil.rmtree(release_root)
    release_root.mkdir(parents=True, exist_ok=True)

    bundled_dir = DIST_DIR / APP_NAME
    shutil.copytree(bundled_dir, release_root / APP_NAME)

    platform_name = normalized_platform()
    if platform_name == "macos":
        write_text_file(release_root / "start.command", macos_start_script(), executable=True)
    elif platform_name == "windows":
        write_text_file(release_root / "start.bat", windows_start_script())
    else:
        write_text_file(release_root / "start.sh", linux_start_script(), executable=True)

    write_text_file(release_root / "README.txt", release_readme())
    return release_root


def package_release() -> Path:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    release_root = stage_release_directory()
    archive = shutil.make_archive(str(release_root), "zip", root_dir=release_root.parent, base_dir=release_root.name)
    return Path(archive)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a packaged GUI release.")
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Keep existing build/dist folders before building",
    )
    args = parser.parse_args()
    build(clean=not args.no_clean)
    archive_path = package_release()
    print(f"Version: {get_version()} ({get_release_tag()})")
    print(f"Built app bundle in: {DIST_DIR}")
    print(f"Built release directory: {RELEASE_DIR / release_basename()}")
    print(f"Built release archive: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
