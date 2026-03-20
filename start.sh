#!/bin/bash
# Banana Slides - 一键本地启动脚本 (macOS / Linux)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo " =========================================="
echo "   🍌 Banana Slides - 一键本地启动脚本"
echo " =========================================="
echo ""

# -----------------------------------------------
# 1. 检查并创建 .env 文件
# -----------------------------------------------
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "[1/4] 未检测到 .env 文件，正在从模板创建..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "       .env 文件已创建！"
    echo ""
    echo " ⚠️  重要：请先编辑根目录下的 .env 文件，填入你的 API Key！"
    echo "       例如: GOOGLE_API_KEY=你的密钥  或  OPENAI_API_KEY=你的密钥"
    echo ""
    echo " 正在用默认编辑器打开 .env 文件..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -e "$SCRIPT_DIR/.env"
    else
        "${EDITOR:-nano}" "$SCRIPT_DIR/.env"
    fi
    echo ""
    echo " 配置完毕后，请重新运行本脚本（按任意键退出）。"
    read -rn1 _dummy
    exit 0
else
    echo "[1/4] 检测到 .env 文件 ✓"
fi

# -----------------------------------------------
# 2. 读取端口配置（从 .env 中读取，默认 5000 / 3000）
# -----------------------------------------------
_parse_port() {
    local key="$1"
    local default="$2"
    local val
    val=$(grep -E "^${key}[[:space:]]*=" "$SCRIPT_DIR/.env" \
          | grep -v '^[[:space:]]*#' \
          | head -1 \
          | sed 's/^[^=]*=//;s/#.*//' \
          | tr -d ' \t\r\n')
    echo "${val:-$default}"
}

BACKEND_PORT=$(_parse_port "BACKEND_PORT" "5000")
FRONTEND_PORT=$(_parse_port "FRONTEND_PORT" "3000")

echo "[2/4] 端口配置：后端=${BACKEND_PORT}  前端=${FRONTEND_PORT} ✓"
echo ""

# -----------------------------------------------
# 3. 检查必要工具
# -----------------------------------------------
echo "[3/4] 检查运行环境..."

# 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo ""
    echo " ❌ 未检测到 Python3！"
    echo "    请安装 Python 3.10+: https://www.python.org/downloads/"
    exit 1
fi
PY_VER=$(python3 --version 2>&1)
echo "       Python: ${PY_VER} ✓"

# 检查 Node.js / npm
if ! command -v npm &>/dev/null; then
    echo ""
    echo " ❌ 未检测到 Node.js / npm！"
    echo "    请安装 Node.js 18+: https://nodejs.org/"
    exit 1
fi
NODE_VER=$(node --version 2>&1)
echo "       Node.js: ${NODE_VER} ✓"

# 检查 uv（可选，但推荐）
if command -v uv &>/dev/null; then
    UV_VER=$(uv --version 2>&1)
    echo "       uv: ${UV_VER} ✓ (推荐，用于管理 Python 依赖)"
else
    echo "       uv: 未安装（将使用 pip + venv）"
fi

echo ""

# -----------------------------------------------
# 4. 在独立窗口中启动后端和前端
# -----------------------------------------------
echo "[4/4] 启动服务..."
echo ""

# 在新终端窗口中运行命令
_open_terminal() {
    local title="$1"
    local cmd="$2"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript <<OSAEOF
tell application "Terminal"
    do script "$cmd"
    set custom title of front window to "$title"
end tell
OSAEOF
    elif command -v gnome-terminal &>/dev/null; then
        gnome-terminal --title="$title" -- bash -c "$cmd; exec bash" &
    elif command -v xterm &>/dev/null; then
        xterm -title "$title" -e "bash -c '$cmd; exec bash'" &
    else
        # No GUI terminal found — run in background, log output to file
        bash -c "$cmd" > "/tmp/banana-slides-$(echo "$title" | tr ' ' '_').log" 2>&1 &
        echo "       (后台运行，日志: /tmp/banana-slides-$(echo "$title" | tr ' ' '_').log)"
    fi
}

# --- 启动后端 ---
echo "  [启动] 正在启动后端服务（新窗口）..."
_open_terminal "Banana Slides 后端" "cd '$SCRIPT_DIR' && bash '$SCRIPT_DIR/start-backend.sh'"

# --- 等待后端就绪（轮询 /health 接口，最多等 60 秒）---
echo "       等待后端就绪..."
WAIT_COUNT=0
while true; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 \
        "http://localhost:${BACKEND_PORT}/health" 2>/dev/null)
    if [ "$HTTP_STATUS" = "200" ]; then
        break
    fi
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [ "$WAIT_COUNT" -ge 30 ]; then
        break
    fi
    sleep 2
done

if [ "$WAIT_COUNT" -ge 30 ]; then
    echo ""
    echo "  [!!] 后端未在 60 秒内就绪，请检查「Banana Slides 后端」窗口中的错误信息。"
    echo ""
fi

# --- 启动前端 ---
echo "  [启动] 正在启动前端服务（新窗口）..."
_open_terminal "Banana Slides 前端" "cd '$SCRIPT_DIR' && bash '$SCRIPT_DIR/start-frontend.sh'"

# --- 等待前端 Vite 就绪（轮询端口，最多等 60 秒）---
echo "       等待前端就绪..."
WAIT_COUNT=0
while true; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 \
        "http://localhost:${FRONTEND_PORT}" 2>/dev/null)
    if [ "$HTTP_STATUS" = "200" ]; then
        break
    fi
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [ "$WAIT_COUNT" -ge 30 ]; then
        break
    fi
    sleep 2
done

if [ "$WAIT_COUNT" -ge 30 ]; then
    echo ""
    echo "  [!!] 前端未在 60 秒内就绪，请检查「Banana Slides 前端」窗口中的错误信息。"
    echo ""
fi

echo ""
echo " =========================================="
echo "   Banana Slides 已启动！"
echo " =========================================="
echo ""
echo "   前端界面:  http://localhost:${FRONTEND_PORT}"
echo "   后端接口:  http://localhost:${BACKEND_PORT}"
echo "   健康检查:  http://localhost:${BACKEND_PORT}/health"
echo ""
echo "   浏览器已由前端服务自动打开（若未自动打开，请手动访问上方地址）。"
echo "   如遇错误，请查看「后端服务」和「前端服务」两个窗口中的报错信息。"
echo ""
echo "   关闭前请先在各服务窗口按 Ctrl+C 停止服务，"
echo "   然后再关闭窗口，避免端口占用。"
echo ""
echo "   按任意键关闭此窗口（服务将继续在各自窗口中运行）..."
read -rn1 _dummy
