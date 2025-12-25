@echo off
chcp 65001 > nul
title 多平台发布工具

echo ==========================================
echo 🚀 多平台发布工具 - 启动中...
echo ==========================================

cd /d "%~dp0"

REM 检查是否已打包（存在可执行文件）
if exist "多平台发布工具.exe" (
    echo 运行打包版本...
    start "" "多平台发布工具.exe"
    exit /b 0
)

REM 开发模式：检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 检查 Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python！
    echo 请先安装 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖
python -c "import flask" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

REM 检查 Playwright
python -c "import playwright" 2>nul
if errorlevel 1 (
    echo 正在安装 Playwright...
    pip install playwright
)

echo.
echo 启动应用...
python app.py

pause

