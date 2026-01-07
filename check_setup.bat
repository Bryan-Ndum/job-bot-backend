@echo off
echo ========================================
echo  Job Application Bot - Setup Check
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo [X] Python not found
    echo     Please install Python from https://www.python.org/
) else (
    echo [OK] Python is installed
)
echo.

echo Checking uvicorn...
python -m uvicorn --version >nul 2>&1
if errorlevel 1 (
    echo [X] uvicorn not installed
    echo     Install with: pip install uvicorn fastapi
) else (
    echo [OK] uvicorn is installed
)
echo.

echo Checking if app directory exists...
if exist "app\main.py" (
    echo [OK] app\main.py found
) else (
    echo [X] app\main.py not found
    echo     Make sure you're in the correct directory
)
echo.

echo Checking if frontend directory exists...
if exist "frontend\index.html" (
    echo [OK] frontend\index.html found
) else (
    echo [X] frontend\index.html not found
)
echo.

echo ========================================
echo Setup check complete!
echo ========================================
echo.
pause






