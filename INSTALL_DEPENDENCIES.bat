@echo off
echo ========================================
echo  Installing Dependencies
echo ========================================
echo.

cd /d "%~dp0"

echo Installing required packages...
echo This may take a few minutes...
echo.

python -m pip install --upgrade pip
python -m pip install uvicorn fastapi python-dotenv

if exist "requirements.txt" (
    echo.
    echo Installing from requirements.txt...
    python -m pip install -r requirements.txt
) else (
    echo.
    echo requirements.txt not found, installing basic packages only...
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo You can now run: start_local_server.bat
echo.
pause






