@echo off
echo ========================================
echo  Job Application Bot - Local Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

echo Starting server...
echo.
echo The dashboard will be available at:
echo   http://localhost:8000/dashboard
echo.
echo Press CTRL+C to stop the server
echo.
echo ========================================
echo.

REM Try to start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

REM If uvicorn fails, show error
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to start server
    echo ========================================
    echo.
    echo Possible issues:
    echo 1. uvicorn not installed - Run: pip install uvicorn fastapi
    echo 2. Dependencies missing - Run: pip install -r requirements.txt
    echo 3. Check the error message above
    echo.
    pause
)
