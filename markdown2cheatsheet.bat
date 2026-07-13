@echo off
setlocal
cd /d "%~dp0"

set "LAUNCHER_NAME=markdown2cheatsheet.bat"
set "MIN_PANDOC_VERSION=3.10"
set "PYTHON_CMD="
set "PROMPT_REPLY="

call :ensure_python || goto :fail
call :ensure_pandoc || goto :fail

echo When you are finished, return to this window and press Ctrl+C to stop the local service.
call %PYTHON_CMD% gui_app.py
if errorlevel 1 goto :fail_runtime

echo.
echo markdown2cheatsheet has stopped. Press any key to close this window.
pause >nul
exit /b 0

:ensure_python
call :resolve_python
exit /b %errorlevel%

:resolve_python
python -V >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=python"
  exit /b 0
)

py -3 -V >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
  exit /b 0
)

echo Python is not installed.
where winget >nul 2>nul
if errorlevel 1 (
  echo Please install Python 3 from https://www.python.org/downloads/ and run %LAUNCHER_NAME% again.
  exit /b 1
)

call :confirm_yes "Install Python 3 with winget now? [y/N] "
if not errorlevel 1 goto :install_python
echo Python 3 is required.
exit /b 1

:install_python
winget install -e --id Python.Python.3.12
if errorlevel 1 (
  echo Python installation failed.
  exit /b 1
)

python -V >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=python"
  exit /b 0
)

py -3 -V >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
  exit /b 0
)

echo Python was installed, but the current terminal cannot find it yet.
echo Please close this window and run %LAUNCHER_NAME% again.
exit /b 1

:ensure_pandoc
where pandoc >nul 2>nul
if errorlevel 1 goto :pandoc_missing

set "PANDOC_VERSION="
for /f "usebackq delims=" %%V in (`call %PYTHON_CMD% -c "import re, subprocess; out = subprocess.run(['pandoc','--version'], capture_output=True, text=True).stdout.splitlines(); line = out[0] if out else ''; match = re.search(r'(\d+(?:\.\d+)+)', line); print(match.group(1) if match else '')"`) do set "PANDOC_VERSION=%%V"

if not defined PANDOC_VERSION (
  echo Pandoc is installed, but its version could not be detected.
  exit /b 1
)

call %PYTHON_CMD% -c "import sys; parse = lambda value: tuple(int(part) for part in value.split('.')); raise SystemExit(0 if parse(sys.argv[1]) >= parse(sys.argv[2]) else 1)" "%PANDOC_VERSION%" "%MIN_PANDOC_VERSION%"
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
