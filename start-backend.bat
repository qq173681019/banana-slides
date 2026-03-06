@echo off
chcp 65001 >nul 2>&1
title Banana Slides - Backend Service
echo.
echo  ==========================================
echo   Banana Slides - Backend Service
echo  ==========================================
echo.
echo  Starting, please wait...
echo.
cd /d "%~dp0backend"
uv --version >nul 2>&1
if not errorlevel 1 goto :use_uv

:use_pip
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo  [ERROR] Failed to create virtual environment.
        echo.
        pause >nul
        exit /b 1
    )
)
call venv\Scripts\activate.bat
pip install -q -e "%~dp0."
if errorlevel 1 (
    echo.
    echo  [ERROR] Failed to install dependencies.
    echo.
    pause >nul
    exit /b 1
)
python -m alembic upgrade head
if errorlevel 1 (
    echo.
    echo  [ERROR] Database migration failed.
    echo.
    pause >nul
    exit /b 1
)
python app.py
if errorlevel 1 (
    echo.
    echo  [ERROR] Backend exited unexpectedly. Check the output above.
    echo.
)
goto :done

:use_uv
uv run python -m alembic upgrade heads
if errorlevel 1 (
    echo.
    echo  [ERROR] Database migration failed.
    echo.
    pause >nul
    exit /b 1
)
uv run python app.py
if errorlevel 1 (
    echo.
    echo  [ERROR] Backend exited unexpectedly. Check the output above.
    echo.
)

:done
echo  Press any key to close this window...
pause >nul
