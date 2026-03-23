@echo off
chcp 65001 >nul 2>&1

echo.
echo  ==========================================
echo   Banana Slides - Quick Start
echo  ==========================================
echo.

echo Starting Backend Service...
start "Banana Slides Backend" cmd /k "cd /d "%~dp0" && start-backend.bat"

echo Starting Frontend Service...
start "Banana Slides Frontend" cmd /k "cd /d "%~dp0" && start-frontend.bat"

echo.
echo  ==========================================
echo   Banana Slides Started!
echo  ==========================================
echo.
echo   Frontend:  http://localhost:3461
echo   Backend:   http://localhost:5461
echo.
echo   Close the two windows to stop services.
echo.
pause
