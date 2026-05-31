#!/bin/bash
# ============================================================
# md2cheatsheet.sh — Markdown to high-density cheatsheet HTML
# Usage: bash md2cheatsheet.sh <input.md> [output.html]
# Requires: pandoc + python3
# ============================================================

set -e

if [ -z "$1" ]; then
  echo "Usage: bash md2cheatsheet.sh <input.md> [output.html]"
  exit 1
fi

INPUT="$1"
BASENAME="${INPUT%.md}"
OUTPUT="${2:-${BASENAME}.html}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TITLE="$(basename "$BASENAME")"

# Locate cheatsheet.css (input dir → script dir → cwd)
CSS_FILE=""
for candidate in "$(dirname "$INPUT")/cheatsheet.css" "$SCRIPT_DIR/cheatsheet.css" "./cheatsheet.css"; do
  if [ -f "$candidate" ]; then CSS_FILE="$candidate"; break; fi
done
if [ -z "$CSS_FILE" ]; then
  echo "Error: cheatsheet.css not found. Place it next to your notes or this script."
  exit 1
fi

# On Windows (Git Bash / MSYS2), pandoc is installed to AppData which is not
# in the default PATH. Probe the two common locations and add them if found.
case "$(uname -s)" in
  MINGW*|CYGWIN*|MSYS*)
    for _winpath in \
      "/c/Users/$USERNAME/AppData/Local/Pandoc" \
      "/c/Program Files/Pandoc"
    do
      if [ -f "$_winpath/pandoc.exe" ]; then
        export PATH="$PATH:$_winpath"
        break
      fi
    done
    ;;
esac

# Check pandoc
if ! command -v pandoc &>/dev/null; then
  echo "Error: pandoc is not installed."
  echo "  macOS:   brew install pandoc"
  echo "  Ubuntu:  sudo apt install pandoc"
  echo "  Windows: winget install JohnMacFarlane.Pandoc"
  exit 1
fi

echo "Converting: $INPUT -> $OUTPUT"
TMP=$(mktemp /tmp/cheatsheet_XXXXXX.html)

# Step 1: pandoc — Markdown to standalone HTML with embedded resources
pandoc "$INPUT" \
  --from markdown+mark+smart+pipe_tables+fenced_code_blocks \
  --to html5 \
  --standalone \
  --embed-resources \
  --css "$CSS_FILE" \
  --metadata title="$TITLE" \
  --highlight-style pygments \
  --output "$TMP"

# Step 2: post-processing (inject layout wrapper, fix tables, compress indentation)
python3 "$SCRIPT_DIR/postprocess.py" "$TMP" "$OUTPUT"

rm -f "$TMP"
echo "Done: $OUTPUT"
echo ""
echo "To print as PDF:"
echo "  1. Open $OUTPUT in a browser"
echo "  2. Press Ctrl+P (Mac: Cmd+P)"
echo "  3. Paper: A4, Orientation: Landscape, Margins: Minimum"
echo "  4. Uncheck 'Headers and footers'"
echo "  5. Save as PDF"
