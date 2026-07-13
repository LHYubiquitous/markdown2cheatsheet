#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

LAUNCHER_NAME="markdown2cheatsheet.sh"
MIN_PANDOC_VERSION="3.10"

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

compare_versions() {
  python3 - "$1" "$2" <<'PY'
import sys

def parse(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))

raise SystemExit(0 if parse(sys.argv[1]) >= parse(sys.argv[2]) else 1)
PY
}

pandoc_version() {
  "$1" --version 2>/dev/null | python3 -c 'import re, sys; line = sys.stdin.readline().strip(); match = re.search(r"(\d+(?:\.\d+)+)", line); print(match.group(1) if match else "")'
}

install_python() {
  if command_exists apt-get; then
    if confirm_install "Python 3 is not installed. Install it with apt now?"; then
      sudo apt-get update && sudo apt-get install -y python3
      return $?
    fi
  elif command_exists dnf; then
    if confirm_install "Python 3 is not installed. Install it with dnf now?"; then
      sudo dnf install -y python3
      return $?
    fi
  elif command_exists pacman; then
    if confirm_install "Python 3 is not installed. Install it with pacman now?"; then
      sudo pacman -Sy --noconfirm python
      return $?
    fi
  fi
  echo "Python 3 is required. Please install it and run $LAUNCHER_NAME again."
  return 1
}

install_or_update_pandoc() {
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
      if [ $status -eq 0 ]; then
        echo "Pandoc was $verb successfully."
      fi
      return $status
    fi
  elif command_exists dnf; then
    if confirm_install "$prompt"; then
      sudo dnf install -y pandoc
      local status=$?
      if [ $status -eq 0 ]; then
        echo "Pandoc was $verb successfully."
      fi
      return $status
    fi
  elif command_exists pacman; then
    if confirm_install "$prompt"; then
      sudo pacman -Sy --noconfirm pandoc-cli
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
}

ensure_pandoc() {
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
}

if ! command_exists python3; then
  install_python || exit 1
fi

ensure_pandoc || exit 1

echo "When you are finished, return to this window and press Ctrl+C to stop the local service."
python3 gui_app.py
status=$?
echo
echo "markdown2cheatsheet has stopped. You can close this window now."
exit $status
