@echo off
chcp 65001 >nul 2>&1
title Banana Slides - Frontend Service
echo.
echo  ==========================================
echo   Banana Slides - Frontend Service
echo  ==========================================
echo.
echo  Starting, please wait...
echo.
cd /d "%~dp0frontend"
if not exist node_modules (
    npm install
    if errorlevel 1 (
        echo.
        echo  [ERROR] npm install failed.
        echo.
        pause >nul
        exit /b 1
    )
)
npm run dev
if errorlevel 1 (
    echo.
    echo  [ERROR] Frontend exited unexpectedly. Check the output above.
    echo.
)
echo  Press any key to close this window...
pause >nul
