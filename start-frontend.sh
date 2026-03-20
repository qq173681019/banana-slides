#!/bin/bash
# Banana Slides - Frontend Service Startup Script (macOS / Linux)

echo ""
echo " =========================================="
echo "   Banana Slides - Frontend Service"
echo " =========================================="
echo ""
echo " Starting, please wait..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/frontend" || exit 1

if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -ne 0 ]; then
        echo ""
        echo " [ERROR] npm install failed."
        echo ""
        read -rp " Press Enter to close this window..." _dummy
        exit 1
    fi
fi

npm run dev
if [ $? -ne 0 ]; then
    echo ""
    echo " [ERROR] Frontend exited unexpectedly. Check the output above."
    echo ""
fi

echo " Press Enter to close this window..."
read -rp "" _dummy
