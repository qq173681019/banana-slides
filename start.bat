@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

echo.
echo  ==========================================
echo   🍌 Banana Slides - 一键本地启动脚本
echo  ==========================================
echo.

REM -----------------------------------------------
REM 1. 检查并创建 .env 文件
REM -----------------------------------------------
if not exist ".env" (
    echo [1/4] 未检测到 .env 文件，正在从模板创建...
    copy ".env.example" ".env" >nul
    echo        .env 文件已创建！
    echo.
    echo  ⚠️  重要：请先编辑根目录下的 .env 文件，填入你的 API Key！
    echo        例如: GOOGLE_API_KEY=你的密钥  或  OPENAI_API_KEY=你的密钥
    echo.
    echo  用记事本打开 .env 文件...
    start notepad ".env"
    echo.
    echo  配置完毕后，请重新运行本脚本（按任意键退出）。
    pause >nul
    exit /b 0
) else (
    echo [1/4] 检测到 .env 文件 ✓
)

REM -----------------------------------------------
REM 2. 读取端口配置（从 .env 中读取，默认 5000 / 3000）
REM    使用 PowerShell 解析，正确处理行内注释和空白
REM -----------------------------------------------
for /f "delims=" %%P in ('powershell -NoProfile -Command "& { $e = Get-Content '.env' | Where-Object { $_ -match '^BACKEND_PORT\s*=' -and $_ -notmatch '^\s*#' }; if ($e) { ($e -split '=',2)[1] -replace '#.*$','' -replace '\s','' } else { '5000' } }"') do set "BACKEND_PORT=%%P"
for /f "delims=" %%P in ('powershell -NoProfile -Command "& { $e = Get-Content '.env' | Where-Object { $_ -match '^FRONTEND_PORT\s*=' -and $_ -notmatch '^\s*#' }; if ($e) { ($e -split '=',2)[1] -replace '#.*$','' -replace '\s','' } else { '3000' } }"') do set "FRONTEND_PORT=%%P"

if "!BACKEND_PORT!"=="" set "BACKEND_PORT=5000"
if "!FRONTEND_PORT!"=="" set "FRONTEND_PORT=3000"

echo [2/4] 端口配置：后端=!BACKEND_PORT!  前端=!FRONTEND_PORT! ✓
echo.

REM -----------------------------------------------
REM 3. 检查必要工具
REM -----------------------------------------------
echo [3/4] 检查运行环境...

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ❌ 未检测到 Python！
    echo     请安装 Python 3.10+: https://www.python.org/downloads/
    echo     安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo        Python: !PY_VER! ✓

REM 检查 Node.js / npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ❌ 未检测到 Node.js / npm！
    echo     请安装 Node.js 18+: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version 2^>^&1') do set NODE_VER=%%v
echo        Node.js: !NODE_VER! ✓

REM 检查 uv（可选，但推荐）
set "USE_UV=0"
uv --version >nul 2>&1
if not errorlevel 1 (
    set "USE_UV=1"
    for /f "tokens=*" %%v in ('uv --version 2^>^&1') do set UV_VER=%%v
    echo        uv: !UV_VER! ✓ (推荐，用于管理 Python 依赖)
) else (
    echo        uv: 未安装（将使用 pip + venv）
)

echo.

REM -----------------------------------------------
REM 4. 在独立窗口中启动后端和前端
REM -----------------------------------------------
echo [4/4] 启动服务...
echo.

REM --- 启动后端 ---
echo  [启动] 正在启动后端服务（新窗口）...
start "Banana Slides 后端" "%~dp0start-backend.bat"

REM --- 等待后端就绪（轮询 /health 接口，最多等 60 秒）---
echo     等待后端就绪...
set /a WAIT_COUNT=0
:wait_backend
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:!BACKEND_PORT!/health' -UseBasicParsing -TimeoutSec 2).StatusCode } catch { 0 }" 2>nul | findstr /C:"200" >nul 2>&1
if not errorlevel 1 goto backend_ready
set /a WAIT_COUNT+=1
if !WAIT_COUNT! GEQ 30 goto backend_ready
timeout /t 2 /nobreak >nul
goto wait_backend
:backend_ready
if !WAIT_COUNT! GEQ 30 (
    echo.
    echo  [!!] 后端未在 60 秒内就绪，请检查「Banana Slides 后端」窗口中的错误信息。
    echo.
)

REM --- 启动前端 ---
echo  [启动] 正在启动前端服务（新窗口）...
start "Banana Slides 前端" "%~dp0start-frontend.bat"

REM --- 等待前端 Vite 就绪（轮询端口，最多等 60 秒）---
echo     等待前端就绪...
set /a WAIT_COUNT=0
:wait_frontend
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:!FRONTEND_PORT!' -UseBasicParsing -TimeoutSec 2).StatusCode } catch { 0 }" 2>nul | findstr /C:"200" >nul 2>&1
if not errorlevel 1 goto frontend_ready
set /a WAIT_COUNT+=1
if !WAIT_COUNT! GEQ 30 goto frontend_ready
timeout /t 2 /nobreak >nul
goto wait_frontend
:frontend_ready
if !WAIT_COUNT! GEQ 30 (
    echo.
    echo  [!!] 前端未在 60 秒内就绪，请检查「Banana Slides 前端」窗口中的错误信息。
    echo.
)

echo.
echo  ==========================================
echo   Banana Slides 已启动！
echo  ==========================================
echo.
echo   前端界面:  http://localhost:!FRONTEND_PORT!
echo   后端接口:  http://localhost:!BACKEND_PORT!
echo   健康检查:  http://localhost:!BACKEND_PORT!/health
echo.
echo   浏览器已由前端服务自动打开（若未自动打开，请手动访问上方地址）。
echo   如遇错误，请查看「后端服务」和「前端服务」两个黑色窗口中的报错信息。
echo.
echo   关闭前请先在各服务窗口按 Ctrl+C 停止服务，
echo   然后再关闭窗口，避免端口占用。
echo.
echo   如需停止所有服务，关闭后端和前端的黑色窗口即可。
echo.
echo   按任意键关闭此窗口（服务将继续在各自窗口中运行）...
pause >nul
