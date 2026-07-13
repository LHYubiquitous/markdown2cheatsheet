# Development Guide

This document is for contributors and maintainers.

[User README](../README.md)
[User Guide](USAGE.md)

## Project Structure

```text
markdown2cheatsheet/
├── README.md
├── LICENSE
├── markdown2cheatsheet.command
├── markdown2cheatsheet.bat
├── markdown2cheatsheet.sh
├── build_release.py
├── assets/
│   └── markdown2cheatsheet.png
├── pandoc_support.py
├── version.py
├── .github/workflows/
│   └── build-release.yml
├── cheatsheet.css
├── converter_core.py
├── gui_app.py
├── md2cheatsheet.py
├── md2cheatsheet.sh
├── postprocess.py
├── template_presets.py
├── gui/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docs/
│   ├── DEVELOPMENT.md
│   ├── USAGE.md
│   ├── USAGE_CN.md
│   └── README_CN.md
└── examples/
    └── test_cheatsheet.md
```

## Local Development

Run the GUI locally:

```bash
python3 gui_app.py
```

Run the example conversion:

```bash
bash md2cheatsheet.sh examples/test_cheatsheet.md examples/test_cheatsheet.html
```

List current template metadata:

```bash
python3 md2cheatsheet.py --list-templates
```

## Release Build

Build a native GUI release on your current platform:

```bash
python3 -m pip install pyinstaller pillow
python3 build_release.py
```

Output location:

- app bundle/folder: `dist/`
- release directory and archive: `release/`

Naming rule:

- `markdown2cheatsheet-gui-v1.0.0-macos-arm64.zip`
- `markdown2cheatsheet-gui-v1.0.0-windows-x64.zip`
- `markdown2cheatsheet-gui-v1.0.0-linux-x64.zip`
- `markdown2cheatsheet-gui-v1.0.0-linux-arm64.zip`

Release startup:

- macOS: extract the zip and launch `markdown2cheatsheet.command`
- Windows: extract the zip and launch `markdown2cheatsheet.bat`
- Linux: extract the zip and launch `markdown2cheatsheet.sh`

## Versioning

- Version is resolved in [version.py](../version.py)
- If the current commit has an exact Git tag, that tag is used
- Otherwise the build falls back to a dev version with the short commit hash

Examples:

- tagged build: `v1.0.0`
- untagged build: `0.0.0-dev+abc1234`

## GitHub Actions

Workflow file:

- `.github/workflows/build-release.yml`

Behavior:

- `workflow_dispatch`: manual build
- `push` on tags matching `v*`: build all platforms and create a GitHub Release

Release artifacts:

- one `.zip` for macOS
- one `.zip` for Windows
- one `.zip` for Linux
