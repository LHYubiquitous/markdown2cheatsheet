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

from pandoc_support import MIN_PANDOC_VERSION
from version import get_filename_version, get_release_tag, get_version


ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
RELEASE_DIR = ROOT_DIR / "release"
PYINSTALLER_CONFIG_DIR = ROOT_DIR / ".pyinstaller"
SPEC_FILE = ROOT_DIR / "Markdown2CheatsheetGUI.spec"
APP_NAME = "Markdown2CheatsheetGUI"
ICON_FILE = ROOT_DIR / "assets" / "markdown2cheatsheet.png"


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
        "--add-data",
        add_data_argument(ROOT_DIR / "assets"),
        "--icon",
        str(ICON_FILE),
    ]
    PyInstaller.__main__.run(options)


def write_text_file(path: Path, content: str, executable: bool = False) -> None:
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def macos_start_script() -> str:
    return f"""#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/Markdown2CheatsheetGUI"
LAUNCHER_NAME="markdown2cheatsheet.command"
MIN_PANDOC_VERSION="{MIN_PANDOC_VERSION}"

command_exists() {{
  command -v "$1" >/dev/null 2>&1
}}

confirm_install() {{
  read -r -p "$1 [y/N] " reply
  case "$reply" in
    [yY]|[yY][eE][sS]) return 0 ;;
    *) return 1 ;;
  esac
}}

compare_versions() {{
  awk -v current="$1" -v minimum="$2" '
  function split_version(value, output, count, i) {{
    count = split(value, output, ".")
    for (i = 1; i <= count; i++) output[i] += 0
    return count
  }}
  BEGIN {{
    current_count = split_version(current, a)
    minimum_count = split_version(minimum, b)
    max_count = current_count > minimum_count ? current_count : minimum_count
    for (i = 1; i <= max_count; i++) {{
      current_part = (i in a) ? a[i] : 0
      minimum_part = (i in b) ? b[i] : 0
      if (current_part > minimum_part) exit 0
      if (current_part < minimum_part) exit 1
    }}
    exit 0
  }}'
}}

pandoc_version() {{
  "$1" --version 2>/dev/null | awk 'NR == 1 {{ for (i = 1; i <= NF; i++) if ($i ~ /^[0-9]+(\\.[0-9]+)+$/) {{ print $i; exit }} }}'
}}

validate_pandoc_after_install() {{
  local verb="$1"
  if ! command_exists pandoc; then
    echo "Pandoc was $verb, but the current terminal cannot find it yet."
    echo "Please close this window and run $LAUNCHER_NAME again."
    return 0
  fi

  local installed_version
  installed_version="$(pandoc_version pandoc)"
  if [ -z "$installed_version" ]; then
    echo "Pandoc was $verb, but its version could not be detected."
    echo "Please close this window and run $LAUNCHER_NAME again."
    return 0
  fi

  if compare_versions "$installed_version" "$MIN_PANDOC_VERSION"; then
    echo "Pandoc $installed_version was $verb successfully."
    return 0
  fi

  echo "Pandoc $installed_version was $verb from your Linux package manager, but markdown2cheatsheet requires $MIN_PANDOC_VERSION or later."
  echo "Your distribution repository may not provide a new enough Pandoc package. Please install a newer Pandoc release manually, then run $LAUNCHER_NAME again."
  return 1
}}

install_or_update_pandoc() {{
  local action="$1"
  local prompt
  local verb

  if [ "$action" = "update" ]; then
    prompt="Pandoc is below the required version $MIN_PANDOC_VERSION. Update it with Homebrew now?"
    verb="updated"
  else
    prompt="Pandoc is not installed. Install it with Homebrew now?"
    verb="installed"
  fi

  if command_exists brew; then
    if confirm_install "$prompt"; then
      if [ "$action" = "update" ]; then
        brew upgrade pandoc
      else
        brew install pandoc
      fi
      local status=$?
      if [ $status -eq 0 ]; then
        echo "Pandoc was $verb successfully."
      fi
      return $status
    fi
  fi

  if [ "$action" = "update" ]; then
    echo "Pandoc $MIN_PANDOC_VERSION or later is required. Please update it and run $LAUNCHER_NAME again."
  else
    echo "Pandoc $MIN_PANDOC_VERSION or later is required. Please install it and run $LAUNCHER_NAME again."
  fi
  return 1
}}

ensure_pandoc() {{
  if ! command_exists pandoc; then
    install_or_update_pandoc "install" || return 1
    echo "Please close this window and run $LAUNCHER_NAME again so the new Pandoc version can be detected."
    return 1
  fi

  local detected_version
  detected_version="$(pandoc_version pandoc)"
  if [ -z "$detected_version" ]; then
    echo "Pandoc is installed, but its version could not be detected. Please check your Pandoc installation."
    return 1
  fi

  if ! compare_versions "$detected_version" "$MIN_PANDOC_VERSION"; then
    echo "Detected Pandoc $detected_version, but markdown2cheatsheet requires $MIN_PANDOC_VERSION or later."
    install_or_update_pandoc "update" || return 1
    echo "Please close this window and run $LAUNCHER_NAME again so the updated Pandoc version can be detected."
    return 1
  fi

  echo "Pandoc $detected_version detected. Starting markdown2cheatsheet..."
  return 0
}}

ensure_pandoc || exit 1

xattr -dr com.apple.quarantine "$APP_DIR" >/dev/null 2>&1 || true
xattr -dr com.apple.provenance "$APP_DIR" >/dev/null 2>&1 || true
chmod +x "$APP_DIR/Markdown2CheatsheetGUI" >/dev/null 2>&1 || true

cd "$APP_DIR" || exit 1
echo "When you are finished, return to this window and press Ctrl+C to stop the local service."
./Markdown2CheatsheetGUI
status=$?
echo
echo "markdown2cheatsheet has stopped. You can close this window now."
exit $status
"""


def linux_start_script() -> str:
    return f"""#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/Markdown2CheatsheetGUI"
LAUNCHER_NAME="markdown2cheatsheet.sh"
MIN_PANDOC_VERSION="{MIN_PANDOC_VERSION}"

command_exists() {{
  command -v "$1" >/dev/null 2>&1
}}

confirm_install() {{
  read -r -p "$1 [y/N] " reply
  case "$reply" in
    [yY]|[yY][eE][sS]) return 0 ;;
    *) return 1 ;;
  esac
}}

compare_versions() {{
  awk -v current="$1" -v minimum="$2" '
  function split_version(value, output, count, i) {{
    count = split(value, output, ".")
    for (i = 1; i <= count; i++) output[i] += 0
    return count
  }}
  BEGIN {{
    current_count = split_version(current, a)
    minimum_count = split_version(minimum, b)
    max_count = current_count > minimum_count ? current_count : minimum_count
    for (i = 1; i <= max_count; i++) {{
      current_part = (i in a) ? a[i] : 0
      minimum_part = (i in b) ? b[i] : 0
      if (current_part > minimum_part) exit 0
      if (current_part < minimum_part) exit 1
    }}
    exit 0
  }}'
}}

pandoc_version() {{
  "$1" --version 2>/dev/null | awk 'NR == 1 {{ for (i = 1; i <= NF; i++) if ($i ~ /^[0-9]+(\\.[0-9]+)+$/) {{ print $i; exit }} }}'
}}

install_or_update_pandoc() {{
  local action="$1"
  local prompt
  local verb

  if [ "$action" = "update" ]; then
    prompt="Pandoc is below the required version $MIN_PANDOC_VERSION. Update it now?"
    verb="updated"
  else
    prompt="Pandoc is not installed. Install it now?"
    verb="installed"
  fi

  if command_exists apt-get; then
    if confirm_install "$prompt"; then
      sudo apt-get update && sudo apt-get install -y pandoc
      local status=$?
      if [ $status -ne 0 ]; then
        return $status
      fi
      validate_pandoc_after_install "$verb"
      return $?
    fi
  elif command_exists dnf; then
    if confirm_install "$prompt"; then
      sudo dnf install -y pandoc
      local status=$?
      if [ $status -ne 0 ]; then
        return $status
      fi
      validate_pandoc_after_install "$verb"
      return $?
    fi
  elif command_exists pacman; then
    if confirm_install "$prompt"; then
      sudo pacman -Sy --noconfirm pandoc-cli
      local status=$?
      if [ $status -ne 0 ]; then
        return $status
      fi
      validate_pandoc_after_install "$verb"
      return $?
    fi
  fi

  if [ "$action" = "update" ]; then
    echo "Pandoc $MIN_PANDOC_VERSION or later is required. Please update it and run $LAUNCHER_NAME again."
  else
    echo "Pandoc $MIN_PANDOC_VERSION or later is required. Please install it and run $LAUNCHER_NAME again."
  fi
  return 1
}}

ensure_pandoc() {{
  if ! command_exists pandoc; then
    install_or_update_pandoc "install" || return 1
    echo "Please close this window and run $LAUNCHER_NAME again so the new Pandoc version can be detected."
    return 1
  fi

  local detected_version
  detected_version="$(pandoc_version pandoc)"
  if [ -z "$detected_version" ]; then
    echo "Pandoc is installed, but its version could not be detected. Please check your Pandoc installation."
    return 1
  fi

  if ! compare_versions "$detected_version" "$MIN_PANDOC_VERSION"; then
    echo "Detected Pandoc $detected_version, but markdown2cheatsheet requires $MIN_PANDOC_VERSION or later."
    install_or_update_pandoc "update" || return 1
    echo "Please close this window and run $LAUNCHER_NAME again so the updated Pandoc version can be detected."
    return 1
  fi

  echo "Pandoc $detected_version detected. Starting markdown2cheatsheet..."
  return 0
}}

ensure_pandoc || exit 1

chmod +x "$APP_DIR/Markdown2CheatsheetGUI" >/dev/null 2>&1 || true

cd "$APP_DIR" || exit 1
echo "When you are finished, return to this window and press Ctrl+C to stop the local service."
./Markdown2CheatsheetGUI
status=$?
echo
echo "markdown2cheatsheet has stopped. You can close this window now."
exit $status
"""


def windows_start_script() -> str:
    return f"""@echo off
setlocal
cd /d "%~dp0"

set "LAUNCHER_NAME=markdown2cheatsheet.bat"
set "MIN_PANDOC_VERSION={MIN_PANDOC_VERSION}"
set "POWERSHELL_CMD="
set "PROMPT_REPLY="

call :ensure_powershell || goto :fail
call :ensure_pandoc || goto :fail

echo When you are finished, return to this window and press Ctrl+C to stop the local service.
"%~dp0Markdown2CheatsheetGUI\\Markdown2CheatsheetGUI.exe"
if errorlevel 1 goto :fail_runtime

echo.
echo markdown2cheatsheet has stopped. Press any key to close this window.
pause >nul
exit /b 0

:ensure_powershell
powershell -NoProfile -Command "exit 0" >nul 2>nul
if not errorlevel 1 (
  set "POWERSHELL_CMD=powershell -NoProfile"
  exit /b 0
)

pwsh -NoProfile -Command "exit 0" >nul 2>nul
if not errorlevel 1 (
  set "POWERSHELL_CMD=pwsh -NoProfile"
  exit /b 0
)

echo PowerShell is required to check the Pandoc version. Please install PowerShell and run %LAUNCHER_NAME% again.
exit /b 1

:ensure_pandoc
where pandoc >nul 2>nul
if errorlevel 1 goto :pandoc_missing

set "PANDOC_VERSION="
for /f "usebackq delims=" %%V in (`call %POWERSHELL_CMD% -Command "$line = pandoc --version | Select-Object -First 1; if ($line -match '([0-9]+(\\.[0-9]+)+)') {{ $matches[1] }}"`) do set "PANDOC_VERSION=%%V"

if not defined PANDOC_VERSION (
  echo Pandoc is installed, but its version could not be detected.
  exit /b 1
)

call %POWERSHELL_CMD% -Command "$current = [version]'%PANDOC_VERSION%'; $minimum = [version]'%MIN_PANDOC_VERSION%'; if ($current -ge $minimum) {{ exit 0 }} else {{ exit 1 }}"
if errorlevel 1 goto :pandoc_too_old

echo Pandoc %PANDOC_VERSION% detected. Starting markdown2cheatsheet...
exit /b 0

:pandoc_missing
echo Pandoc is not installed.
call :install_or_update_pandoc install || exit /b 1
echo Please close this window and run %LAUNCHER_NAME% again so the new Pandoc version can be detected.
exit /b 1

:pandoc_too_old
echo Detected Pandoc %PANDOC_VERSION%, but markdown2cheatsheet requires %MIN_PANDOC_VERSION% or later.
call :install_or_update_pandoc update || exit /b 1
echo Please close this window and run %LAUNCHER_NAME% again so the updated Pandoc version can be detected.
exit /b 1

:install_or_update_pandoc
where winget >nul 2>nul
if errorlevel 1 (
  if /i "%~1"=="update" (
    echo Please update Pandoc to %MIN_PANDOC_VERSION% or later and run %LAUNCHER_NAME% again.
  ) else (
    echo Please install Pandoc and run %LAUNCHER_NAME% again.
  )
  exit /b 1
)

if /i "%~1"=="update" (
  call :confirm_yes "Pandoc is below the required version %MIN_PANDOC_VERSION%. Update it with winget now? [y/N] "
  if errorlevel 1 (
    echo Pandoc %MIN_PANDOC_VERSION% or later is required.
    exit /b 1
  )
  winget upgrade -e --id JohnMacFarlane.Pandoc
) else (
  call :confirm_yes "Install Pandoc with winget now? [y/N] "
  if errorlevel 1 (
    echo Pandoc %MIN_PANDOC_VERSION% or later is required.
    exit /b 1
  )
  winget install -e --id JohnMacFarlane.Pandoc
)

if errorlevel 1 (
  echo Pandoc %~1 failed.
  exit /b 1
)

echo Pandoc %~1 completed successfully.
exit /b 0

:confirm_yes
set "PROMPT_REPLY="
set /p PROMPT_REPLY=%~1
if /i "%PROMPT_REPLY%"=="y" exit /b 0
if /i "%PROMPT_REPLY%"=="yes" exit /b 0
exit /b 1

:fail_runtime
echo.
echo markdown2cheatsheet has stopped with an error. Press any key to close this window.
pause >nul
exit /b 1

:fail
pause
exit /b 1
"""


def release_readme() -> str:
    platform_name = normalized_platform()
    version = get_release_tag()
    if platform_name == "macos":
        start_name = "markdown2cheatsheet.command"
        extra = (
            "If macOS shows a security warning the first time, right-click "
            "`markdown2cheatsheet.command` and choose Open."
        )
    elif platform_name == "windows":
        start_name = "markdown2cheatsheet.bat"
        extra = "If Windows SmartScreen appears, choose More info and then Run anyway."
    else:
        start_name = "markdown2cheatsheet.sh"
        extra = (
            "If needed, run `chmod +x markdown2cheatsheet.sh` once and then "
            "double-click or run it."
        )

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
        write_text_file(release_root / "markdown2cheatsheet.command", macos_start_script(), executable=True)
    elif platform_name == "windows":
        write_text_file(release_root / "markdown2cheatsheet.bat", windows_start_script())
    else:
        write_text_file(release_root / "markdown2cheatsheet.sh", linux_start_script(), executable=True)

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
