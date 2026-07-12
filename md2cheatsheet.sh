#!/bin/bash
# ============================================================
# md2cheatsheet.sh — Bash wrapper around the Python CLI
# Usage: bash md2cheatsheet.sh <input.md> [output.html] [options]
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "$SCRIPT_DIR/md2cheatsheet.py" "$@"
