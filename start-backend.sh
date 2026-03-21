#!/bin/bash
# Banana Slides - Backend Service Startup Script (macOS / Linux)

echo ""
echo " =========================================="
echo "   Banana Slides - Backend Service"
echo " =========================================="
echo ""
echo " Starting, please wait..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend" || exit 1

if command -v uv &>/dev/null; then
    uv run python -m alembic upgrade heads
    if [ $? -ne 0 ]; then
        echo ""
        echo " [ERROR] Database migration failed."
        echo ""
        read -rp " Press Enter to close this window..." _dummy
        exit 1
    fi
    uv run python app.py
    if [ $? -ne 0 ]; then
        echo ""
        echo " [ERROR] Backend exited unexpectedly. Check the output above."
        echo ""
        echo "   If you see 'Address already in use' / 端口已被占用："
        echo "   - macOS: disable AirPlay Receiver in"
        echo "     System Settings → General → AirDrop & Handoff"
        echo "   - Or set a different port in .env: BACKEND_PORT=5001"
        echo ""
    fi
else
    # Fallback: pip + venv
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo ""
            echo " [ERROR] Failed to create virtual environment."
            echo ""
            read -rp " Press Enter to close this window..." _dummy
            exit 1
        fi
    fi
    source venv/bin/activate
    pip install -q -e "$SCRIPT_DIR"
    if [ $? -ne 0 ]; then
        echo ""
        echo " [ERROR] Failed to install dependencies."
        echo ""
        read -rp " Press Enter to close this window..." _dummy
        exit 1
    fi
    python -m alembic upgrade heads
    if [ $? -ne 0 ]; then
        echo ""
        echo " [ERROR] Database migration failed."
        echo ""
        read -rp " Press Enter to close this window..." _dummy
        exit 1
    fi
    python app.py
    if [ $? -ne 0 ]; then
        echo ""
        echo " [ERROR] Backend exited unexpectedly. Check the output above."
        echo ""
        echo "   If you see 'Address already in use' / 端口已被占用："
        echo "   - macOS: disable AirPlay Receiver in"
        echo "     System Settings → General → AirDrop & Handoff"
        echo "   - Or set a different port in .env: BACKEND_PORT=5001"
        echo ""
    fi
fi

echo " Press Enter to close this window..."
read -rp "" _dummy
