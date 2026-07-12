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
  echo "Python 3 is required. Please install it and run start.sh again."
  return 1
}

install_pandoc() {
  if command_exists apt-get; then
    if confirm_install "Pandoc is not installed. Install it with apt now?"; then
      sudo apt-get update && sudo apt-get install -y pandoc
      return $?
    fi
  elif command_exists dnf; then
    if confirm_install "Pandoc is not installed. Install it with dnf now?"; then
      sudo dnf install -y pandoc
      return $?
    fi
  elif command_exists pacman; then
    if confirm_install "Pandoc is not installed. Install it with pacman now?"; then
      sudo pacman -Sy --noconfirm pandoc-cli
      return $?
    fi
  fi
  echo "Pandoc is required. Please install it and run start.sh again."
  return 1
}

if ! command_exists python3; then
  install_python || exit 1
fi

if ! command_exists pandoc; then
  install_pandoc || exit 1
fi

python3 gui_app.py
