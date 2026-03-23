@echo off
title Banana Slides - Backend Service
echo.
echo  ==========================================
echo   Banana Slides - Backend Service
echo  ==========================================
echo.
echo  Starting, please wait...
echo.
cd /d "%~dp0backend"

REM Use pip instead of uv
echo [1/3] Creating virtual environment...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to create virtual environment.
        echo.
        pause
        exit /b 1
    )
)

echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r ..\requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies.
    echo.
    pause
    exit /b 1
)

echo [3/3] Running database migration...
python -m alembic upgrade head
if errorlevel 1 (
    echo.
    echo [ERROR] Database migration failed.
    echo.
    pause
    exit /b 1
)

echo.
echo [Starting] Flask application...
echo.
python app.py
if errorlevel 1 (
    echo.
    echo [ERROR] Backend exited unexpectedly.
    echo.
)

pause
