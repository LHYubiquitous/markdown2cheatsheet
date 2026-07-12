@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed.
  where winget >nul 2>nul
  if errorlevel 1 (
    echo Please install Python 3 from https://www.python.org/downloads/ and run start.bat again.
    pause
    exit /b 1
  )
  set /p INSTALL_PYTHON=Install Python 3 with winget now? [y/N] 
  if /i "%INSTALL_PYTHON%"=="y" (
    winget install -e --id Python.Python.3.12
  ) else if /i "%INSTALL_PYTHON%"=="yes" (
    winget install -e --id Python.Python.3.12
  ) else (
    echo Python 3 is required.
    pause
    exit /b 1
  )
)

where pandoc >nul 2>nul
if errorlevel 1 (
  echo Pandoc is not installed.
  where winget >nul 2>nul
  if errorlevel 1 (
    echo Please install Pandoc and run start.bat again.
    pause
    exit /b 1
  )
  set /p INSTALL_PANDOC=Install Pandoc with winget now? [y/N] 
  if /i "%INSTALL_PANDOC%"=="y" (
    winget install -e --id JohnMacFarlane.Pandoc
  ) else if /i "%INSTALL_PANDOC%"=="yes" (
    winget install -e --id JohnMacFarlane.Pandoc
  ) else (
    echo Pandoc is required.
    pause
    exit /b 1
  )
)

python gui_app.py
pause
