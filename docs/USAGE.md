# markdown2cheatsheet User Guide

This guide is for end users. It explains how to start the app, how to handle security prompts, and how to troubleshoot common issues.

[Back to README](../README.md)

## 1. Before You Start

You need these two things:

- Pandoc `3.1.3` or later
- Python 3

If you are not sure whether Pandoc is installed, check it first:

```bash
pandoc --version
```

If the first line shows a version number and it is not lower than `3.1.3`, you are ready to continue.

## 2. Recommended Way To Start

The project includes double-click launchers:

- macOS: `markdown2cheatsheet.command`
- Windows: `markdown2cheatsheet.bat`
- Linux: `markdown2cheatsheet.sh`

The launcher checks Pandoc first:

- not installed: it prompts you to install it
- version too old: it prompts you to update it
- version is valid: it starts the local GUI

If Pandoc was just installed or updated, close the current launcher window and run the launcher again.

## 3. macOS Notes

### The first run is blocked by macOS

macOS may treat `.command` files as untrusted the first time. Usually there are two ways to handle this.

Option 1: open it from Finder with right-click

1. Find `markdown2cheatsheet.command` in Finder
2. Right-click it
3. Choose `Open`
4. Click `Open` again in the confirmation dialog

Option 2: allow it in Privacy & Security

1. Open `System Settings`
2. Go to `Privacy & Security`
3. Scroll to the security warning area
4. If you see a blocked item related to `markdown2cheatsheet.command`, click `Open Anyway` or the equivalent allow button
5. Return to the project folder and run it again

If the zip was downloaded from the internet, macOS may also block it because of quarantine metadata. In that case, try right-click `Open` first, then allow it in `Privacy & Security` if needed.

### Double-click does nothing or the window closes immediately

Common reasons:

- Pandoc is not installed
- Pandoc is lower than `3.1.3`
- Python 3 is not available
- macOS security has not allowed the launcher yet

Recommended steps:

1. Try right-click `Open` once
2. Check the Terminal window for the exact message
3. If it asks to install or update Pandoc, complete that first
4. After install or update, close the window and relaunch

### The browser does not open automatically

This usually does not mean startup failed. Open your browser manually and visit:

```text
http://127.0.0.1:8765
```

If the page opens, the local service is already running correctly.

## 4. Windows Notes

The first time you double-click `markdown2cheatsheet.bat`, Windows may show a SmartScreen warning.

The usual flow is:

1. Click `More info`
2. Choose `Run anyway`

If the launcher asks to install or update Pandoc and you agree, it will try to use `winget`.

If Pandoc finishes installing but is still not detected:

1. Close the current window
2. Run the launcher again
3. If needed, reopen your terminal or restart Windows and try again

## 5. Linux Notes

If double-clicking `markdown2cheatsheet.sh` does not run it, the most common cause is missing execute permission.

Grant execute permission first:

```bash
chmod +x markdown2cheatsheet.sh
```

Then run it again:

```bash
./markdown2cheatsheet.sh
```

If the system asks to install or update Pandoc, confirm the prompt and continue.

The Linux launcher supports these package managers:

- Ubuntu/Debian: `apt-get`
- Fedora: `dnf`
- Arch/Manjaro: `pacman`

Manual install commands:

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y python3 pandoc

# Fedora
sudo dnf install -y python3 pandoc

# Arch / Manjaro
sudo pacman -Sy --noconfirm python pandoc-cli
```

After installation, check the Pandoc version:

```bash
pandoc --version
```

Some distribution repositories may provide Pandoc versions older than `3.1.3`. If your distro package manager installs an older version, install a newer Pandoc release manually and then run `markdown2cheatsheet.sh` again.

## 6. Basic GUI Workflow

After startup succeeds, the browser opens the local page.

Typical workflow:

1. Import a Markdown file or paste Markdown directly
2. Set the output filename
3. Choose columns, color template, fonts, font size, and line height
4. Click `Generate`
5. Preview the result on the right
6. Click `Download HTML` to save the output

## 7. Export To PDF

After generating the HTML, you can export it to PDF:

1. Open the generated HTML in a browser
2. Press `Cmd+P` on macOS or `Ctrl+P` on Windows/Linux
3. Set paper size to `A4`
4. Set orientation to landscape
5. Set margins to minimum
6. Disable headers and footers
7. Save as PDF

## 8. Troubleshooting

### Pandoc is not installed

Check it first:

```bash
pandoc --version
```

If the command does not exist, install Pandoc first.

### Pandoc version is too old

This project requires Pandoc `3.1.3` or later.

Check your current version:

```bash
pandoc --version
```

If the version is too old, update Pandoc and then relaunch the launcher.

On Debian, Fedora, Arch, or Manjaro, the launcher tries the system package manager first. If that package manager still provides a version lower than `3.1.3`, use a newer Pandoc release from another source, then relaunch the launcher.

### It still fails after install or update

Try these steps in order:

1. Close the current launcher window
2. Run the launcher again
3. Reopen your terminal or file manager
4. If needed, restart the system and try again

### The port is already in use

The default local address is:

```text
http://127.0.0.1:8765
```

If another process is already using that port, the GUI may fail to start.

The simplest fix is:

1. Close any older markdown2cheatsheet process that is still running
2. Start it again

### The app says "cannot execute binary file" on Linux

This usually means the release archive does not match your CPU architecture. For example, a `linux-x64` archive will not run inside an ARM64 Ubuntu virtual machine.

Check your system architecture:

```bash
uname -m
```

Use the matching archive:

- `x86_64` or `amd64`: use `linux-x64`
- `aarch64` or `arm64`: use `linux-arm64`

### How to stop it when you are done

If you started it from a launcher, the local service usually keeps running in the Terminal window.

When you are done:

1. Go back to the Terminal window opened by the launcher
2. Press `Ctrl+C`
3. Wait for the stop message, then close the window

## 9. Manual Start

If you do not want to use the double-click launcher, you can start it manually:

```bash
python3 gui_app.py
```

Then open this in your browser:

```text
http://127.0.0.1:8765
```
