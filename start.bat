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
REM -----------------------------------------------
set "BACKEND_PORT=5000"
set "FRONTEND_PORT=3000"
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    set "line=%%A"
    if "!line:~0,1!" neq "#" (
        if "%%A"=="BACKEND_PORT"  set "BACKEND_PORT=%%B"
        if "%%A"=="FRONTEND_PORT" set "FRONTEND_PORT=%%B"
    )
)
REM 去掉空白
set "BACKEND_PORT=!BACKEND_PORT: =!"
set "FRONTEND_PORT=!FRONTEND_PORT: =!"

echo [2/4] 端口配置：后端=%BACKEND_PORT%  前端=%FRONTEND_PORT% ✓
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
echo  ► 正在启动后端服务（新窗口）...
if "%USE_UV%"=="1" (
    REM 使用 uv：在项目根目录运行，自动管理虚拟环境
    start "🍌 Banana Slides - 后端 (:%BACKEND_PORT%)" cmd /k "title 🍌 Banana Slides 后端服务 && echo. && echo  后端服务正在启动，请稍候... && echo  端口: %BACKEND_PORT% && echo. && cd /d "%~dp0backend" && uv run alembic upgrade head 2>nul & uv run python app.py"
) else (
    REM 使用 pip + venv 作为备用方案
    start "🍌 Banana Slides - 后端 (:%BACKEND_PORT%)" cmd /k "title 🍌 Banana Slides 后端服务 && echo. && echo  后端服务正在启动，请稍候... && echo  端口: %BACKEND_PORT% && echo. && cd /d "%~dp0backend" && (if not exist venv python -m venv venv) && call venv\Scripts\activate.bat && pip install -q -r requirements.txt 2>nul & python app.py"
)

REM 等待后端初始化（给 Flask 约 3 秒启动时间）
echo     等待后端初始化 (3 秒)...
timeout /t 3 /nobreak >nul

REM --- 启动前端 ---
echo  ► 正在启动前端服务（新窗口）...
start "🍌 Banana Slides - 前端 (:%FRONTEND_PORT%)" cmd /k "title 🍌 Banana Slides 前端服务 && echo. && echo  前端服务正在启动，请稍候... && echo  端口: %FRONTEND_PORT% && echo. && cd /d "%~dp0frontend" && (if not exist node_modules npm install) && npm run dev"

REM 等待前端 Vite 启动（约 5 秒）
echo     等待前端启动 (5 秒)...
timeout /t 5 /nobreak >nul

REM --- 打开浏览器 ---
echo  ► 正在打开浏览器...
start "" "http://localhost:%FRONTEND_PORT%"

echo.
echo  ==========================================
echo   ✅ Banana Slides 已启动！
echo  ==========================================
echo.
echo   前端界面:  http://localhost:%FRONTEND_PORT%
echo   后端接口:  http://localhost:%BACKEND_PORT%
echo   健康检查:  http://localhost:%BACKEND_PORT%/health
echo.
echo   ⚠️  关闭前请先在各服务窗口按 Ctrl+C 停止服务，
echo       然后再关闭窗口，避免端口占用。
echo.
echo   如需停止所有服务，关闭后端和前端的黑色窗口即可。
echo.
pause
