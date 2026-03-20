#!/bin/bash
# Banana Slides - macOS 双击启动入口
# 在 Finder 中双击本文件，macOS 会自动打开终端并运行此脚本。
# Double-click this file in Finder to launch Banana Slides on macOS.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "$SCRIPT_DIR/start.sh"
