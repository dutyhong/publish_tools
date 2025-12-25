#!/bin/bash
# Mac 启动脚本 - 双击此文件启动程序

cd "$(dirname "$0")"

echo "=========================================="
echo "🚀 多平台发布工具 - 启动中..."
echo "=========================================="

# 检查是否已打包（存在可执行文件）
if [ -f "./多平台发布工具" ]; then
    echo "运行打包版本..."
    ./多平台发布工具
    exit 0
fi

# 开发模式：检查 Python 环境
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3！"
    echo "请先安装 Python: https://www.python.org/downloads/"
    read -p "按 Enter 键退出..."
    exit 1
fi

# 检查依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 检查 Playwright
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "正在安装 Playwright..."
    pip3 install playwright
fi

# 启动应用
echo ""
echo "启动应用..."
python3 app.py

read -p "按 Enter 键退出..."

