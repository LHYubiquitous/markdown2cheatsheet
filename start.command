#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

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

install_python() {
  if command_exists brew; then
    if confirm_install "Python 3 is not installed. Install it with Homebrew now?"; then
      brew install python
      return $?
    fi
  fi
  echo "Python 3 is required. Please install it and run start.command again."
  return 1
}

install_pandoc() {
  if command_exists brew; then
    if confirm_install "Pandoc is not installed. Install it with Homebrew now?"; then
      brew install pandoc
      return $?
    fi
  fi
  echo "Pandoc is required. Please install it and run start.command again."
  return 1
}

if ! command_exists python3; then
  install_python || exit 1
fi

if ! command_exists pandoc; then
  install_pandoc || exit 1
fi

python3 gui_app.py
