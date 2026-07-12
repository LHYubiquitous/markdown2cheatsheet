@echo off
setlocal
cd /d "%~dp0"

call :ensure_python || goto :fail
call :ensure_pandoc || goto :fail

python gui_app.py
if errorlevel 1 goto :fail
goto :end

:ensure_python
where python >nul 2>nul
if not errorlevel 1 exit /b 0

echo Python is not installed.
where winget >nul 2>nul
if errorlevel 1 (
  echo Please install Python 3 from https://www.python.org/downloads/ and run start.bat again.
  exit /b 1
)

set /p INSTALL_PYTHON=Install Python 3 with winget now? [y/N] 
if /i "%INSTALL_PYTHON%"=="y" goto :install_python
if /i "%INSTALL_PYTHON%"=="yes" goto :install_python
echo Python 3 is required.
exit /b 1

:install_python
winget install -e --id Python.Python.3.12
if errorlevel 1 (
  echo Python installation failed.
  exit /b 1
)

where python >nul 2>nul
if not errorlevel 1 exit /b 0

echo Python was installed, but the current terminal cannot find it yet.
echo Please close this window and run start.bat again.
exit /b 1

:ensure_pandoc
where pandoc >nul 2>nul
if not errorlevel 1 exit /b 0

echo Pandoc is not installed.
where winget >nul 2>nul
if errorlevel 1 (
  echo Please install Pandoc and run start.bat again.
  exit /b 1
)

set /p INSTALL_PANDOC=Install Pandoc with winget now? [y/N] 
if /i "%INSTALL_PANDOC%"=="y" goto :install_pandoc
if /i "%INSTALL_PANDOC%"=="yes" goto :install_pandoc
echo Pandoc is required.
exit /b 1

:install_pandoc
winget install -e --id JohnMacFarlane.Pandoc
if errorlevel 1 (
  echo Pandoc installation failed.
  exit /b 1
)

where pandoc >nul 2>nul
if not errorlevel 1 exit /b 0

echo Pandoc was installed, but the current terminal cannot find it yet.
echo Please close this window and run start.bat again.
exit /b 1

:fail
pause
exit /b 1

:end
pause
