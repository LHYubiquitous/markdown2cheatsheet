#!/usr/bin/env python3
"""Lightweight local GUI for markdown2cheatsheet."""

from __future__ import annotations

import argparse
import json
import tempfile
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from converter_core import convert_markdown, list_templates
from runtime_paths import get_app_root
from template_presets import (
    DEFAULT_COLOR_TEMPLATE,
    DEFAULT_COLUMNS,
    DEFAULT_CJK_FONT,
    DEFAULT_CODE_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_LINE_HEIGHT,
    DEFAULT_LATIN_FONT,
)
from version import get_version

ROOT_DIR = get_app_root()
GUI_DIR = ROOT_DIR / "gui"
ASSETS_DIR = ROOT_DIR / "assets"
DEFAULT_EXAMPLE = ROOT_DIR / "examples" / "test_cheatsheet.md"


class GuiHandler(BaseHTTPRequestHandler):
    server_version = f"markdown2cheatsheet-gui/{get_version()}"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._serve_file("index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/app.js":
            self._serve_file("app.js", "application/javascript; charset=utf-8")
            return
        if parsed.path == "/styles.css":
            self._serve_file("styles.css", "text/css; charset=utf-8")
            return
        if parsed.path == "/favicon.png":
            self._serve_asset("markdown2cheatsheet.png", "image/png")
            return
        if parsed.path == "/api/templates":
            self._send_json(list_templates())
            return
        if parsed.path == "/api/default-markdown":
            self._send_json(self._default_markdown_payload())
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/convert":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        try:
            payload = self._read_json()
            markdown = payload.get("markdown", "")
            output_name = payload.get("outputName", "cheatsheet.html")
            columns = int(payload.get("columns", DEFAULT_COLUMNS))
            color_template = payload.get("colorTemplate", DEFAULT_COLOR_TEMPLATE)
            latin_font = payload.get("latinFont", DEFAULT_LATIN_FONT)
            cjk_font = payload.get("cjkFont", DEFAULT_CJK_FONT)
            code_font = payload.get("codeFont", DEFAULT_CODE_FONT)
            font_size = payload.get("fontSize", DEFAULT_FONT_SIZE)
            line_height = payload.get("lineHeight", DEFAULT_LINE_HEIGHT)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": f"Invalid request: {exc}"}, status=HTTPStatus.BAD_REQUEST)
            return

        if not markdown.strip():
            self._send_json(
                {"error": "Markdown content is empty."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        safe_name = Path(output_name).name or "cheatsheet.html"
        stem = Path(safe_name).stem or "cheatsheet"

        try:
            with tempfile.TemporaryDirectory(prefix="md2cheatsheet_gui_") as tmpdir:
                tmp_dir = Path(tmpdir)
                input_file = tmp_dir / "input.md"
                output_file = tmp_dir / f"{stem}.html"
                input_file.write_text(markdown, encoding="utf-8")
                result = convert_markdown(
                    input_file,
                    output_file,
                    columns=columns,
                    color_template=color_template,
                    latin_font=latin_font,
                    cjk_font=cjk_font,
                    code_font=code_font,
                    font_size=font_size,
                    line_height=line_height,
                )
                html = result.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self._send_json(
            {
                "html": html,
                "outputName": f"{stem}.html",
            }
        )

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _serve_file(self, filename: str, content_type: str) -> None:
        path = GUI_DIR / filename
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_asset(self, filename: str, content_type: str) -> None:
        path = ASSETS_DIR / filename
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _default_markdown_payload(self) -> dict:
        if not DEFAULT_EXAMPLE.exists():
            return {
                "filename": "cheatsheet",
                "markdown": "",
            }
        return {
            "filename": DEFAULT_EXAMPLE.stem,
            "markdown": DEFAULT_EXAMPLE.read_text(encoding="utf-8"),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the markdown2cheatsheet local GUI.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the local server")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind the local server")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the server without opening a browser automatically",
    )
    return parser


def run_server(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> None:
    server = ThreadingHTTPServer((host, port), GuiHandler)
    url = f"http://{host}:{port}"
    print(f"GUI running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    args = build_parser().parse_args()
    run_server(host=args.host, port=args.port, open_browser=not args.no_browser)
