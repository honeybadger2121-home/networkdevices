@echo off
REM Aruba AP 500 & 3Com Switch Manager - Windows Startup Script

echo Starting Aruba AP 500 & 3Com Switch Manager...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "start.py" (
    echo ERROR: Please run this script from the aruba-3com-manager directory
    pause
    exit /b 1
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing/updating dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo WARNING: Some dependencies might not have installed correctly
        echo.
    )
)

REM Start the application
echo.
echo Starting application...
python start.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with an error
    pause
)

echo.
echo Application stopped
pause