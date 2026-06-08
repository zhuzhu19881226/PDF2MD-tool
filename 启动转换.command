#!/bin/bash
# ==========================================
# PDF转Markdown - 智能启动脚本
# ==========================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 如果没有 TTY（从 Finder 双击），重新用 Terminal 打开
if [ ! -t 0 ] && [ -z "$FROM_TERMINAL" ]; then
    osascript -e "tell application \"Terminal\" to do script \"clear; cd '$SCRIPT_DIR' && FROM_TERMINAL=1 bash '$0'; exit\"" 2>/dev/null
    exit 0
fi

# 检查 Python
for py in "/opt/homebrew/bin/python3" "/usr/local/bin/python3" "/usr/bin/python3"; do
    [ -x "$py" ] && { PYTHON="$py"; break; }
done

if [ -z "$PYTHON" ]; then
    echo "❌ 未找到 Python3，请安装: brew install python3"
    read -p "按回车键退出..."
    exit 1
fi

clear
echo "========================================"
echo "   PDF → Markdown 转换工具"
echo "========================================"
echo ""
echo "请选择模式："
echo "  1) 网页版（推荐）- 浏览器操作，界面友好"
echo "  2) 终端版 - 命令行交互"
echo ""
read -p "请输入 [1/2] (默认 1): " choice
choice=${choice:-1}

if [ "$choice" = "2" ]; then
    echo ""
    "$PYTHON" "$SCRIPT_DIR/pdf_to_md.py"
else
    echo ""
    "$PYTHON" "$SCRIPT_DIR/网页转换.py"
fi
