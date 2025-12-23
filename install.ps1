# 多平台发布工具 - 一键安装脚本 (Windows PowerShell)
# 使用方法: irm https://raw.githubusercontent.com/YOUR_USERNAME/publish-tools/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Print-Info($message) { Write-Host "[INFO] $message" -ForegroundColor Blue }
function Print-Success($message) { Write-Host "[SUCCESS] $message" -ForegroundColor Green }
function Print-Warning($message) { Write-Host "[WARNING] $message" -ForegroundColor Yellow }
function Print-Error($message) { Write-Host "[ERROR] $message" -ForegroundColor Red }

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       📝 多平台内容发布工具 - 一键安装                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Print-Info "检查 Python 环境..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        Print-Success "找到 $pythonVersion"
    }
} catch {
    Print-Error "未找到 Python！请先安装 Python 3.8+"
    Write-Host "  下载地址: https://www.python.org/downloads/"
    exit 1
}

# 检查 pip
Print-Info "检查 pip..."
try {
    python -m pip --version | Out-Null
    Print-Success "pip 已安装"
} catch {
    Print-Error "未找到 pip！"
    exit 1
}

# 检查 Git
Print-Info "检查 Git..."
try {
    git --version | Out-Null
    Print-Success "Git 已安装"
} catch {
    Print-Error "未找到 Git！请先安装 Git"
    Write-Host "  下载地址: https://git-scm.com/download/win"
    exit 1
}

# 设置安装目录
$INSTALL_DIR = "$env:USERPROFILE\publish-tools"

# 如果目录已存在，询问是否更新
if (Test-Path $INSTALL_DIR) {
    Print-Warning "目录 $INSTALL_DIR 已存在"
    $updateChoice = Read-Host "是否更新？(y/n) [y]"
    if ($updateChoice -eq "" -or $updateChoice -eq "y" -or $updateChoice -eq "Y") {
        Print-Info "更新项目..."
        Set-Location $INSTALL_DIR
        git pull origin main 2>$null
        if ($LASTEXITCODE -ne 0) {
            git pull origin master
        }
    }
} else {
    # 克隆项目
    Print-Info "克隆项目到 $INSTALL_DIR..."
    git clone https://github.com/YOUR_USERNAME/publish-tools.git $INSTALL_DIR
}

Set-Location $INSTALL_DIR

# 创建虚拟环境
Print-Info "创建 Python 虚拟环境..."
if (!(Test-Path "venv")) {
    python -m venv venv
    Print-Success "虚拟环境创建成功"
} else {
    Print-Info "虚拟环境已存在，跳过创建"
}

# 激活虚拟环境并安装依赖
Print-Info "安装 Python 依赖..."
& "$INSTALL_DIR\venv\Scripts\python.exe" -m pip install --upgrade pip
& "$INSTALL_DIR\venv\Scripts\pip.exe" install -r requirements.txt

# 安装 Playwright 浏览器
Print-Info "安装 Chromium 浏览器（可能需要几分钟）..."
& "$INSTALL_DIR\venv\Scripts\playwright.exe" install chromium

# 创建启动脚本
Print-Info "创建启动脚本..."

$startScript = @"
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
pause
"@
$startScript | Out-File -FilePath "$INSTALL_DIR\start.bat" -Encoding ASCII

$startWebScript = @"
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python app.py
pause
"@
$startWebScript | Out-File -FilePath "$INSTALL_DIR\start-web.bat" -Encoding ASCII

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✅ 安装完成！                           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📁 安装目录: $INSTALL_DIR" -ForegroundColor White
Write-Host ""
Write-Host "🚀 运行方式:" -ForegroundColor White
Write-Host "   命令行模式: 双击 $INSTALL_DIR\start.bat" -ForegroundColor Gray
Write-Host "   Web 模式:   双击 $INSTALL_DIR\start-web.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 使用说明: $INSTALL_DIR\README.md" -ForegroundColor Gray
Write-Host ""
Print-Success "感谢使用！如有问题请提 Issue"

# 询问是否立即运行
$runNow = Read-Host "是否立即运行？(y/n) [n]"
if ($runNow -eq "y" -or $runNow -eq "Y") {
    & "$INSTALL_DIR\start.bat"
}

