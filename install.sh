#!/bin/bash

# 多平台发布工具 - 一键安装脚本 (Mac/Linux)
# 使用方法: curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/publish-tools/main/install.sh | bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       📝 多平台内容发布工具 - 一键安装                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python
print_info "检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "找到 Python $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "找到 Python $PYTHON_VERSION"
else
    print_error "未找到 Python！请先安装 Python 3.8+"
    echo "  Mac: brew install python3"
    echo "  Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi

# 检查 pip
print_info "检查 pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "未找到 pip！"
    echo "  请运行: $PYTHON_CMD -m ensurepip --upgrade"
    exit 1
fi
print_success "pip 已安装"

# 检查 git
print_info "检查 Git..."
if ! command -v git &> /dev/null; then
    print_error "未找到 Git！请先安装 Git"
    echo "  Mac: brew install git"
    echo "  Ubuntu: sudo apt install git"
    exit 1
fi
print_success "Git 已安装"

# 设置安装目录
INSTALL_DIR="$HOME/publish-tools"

# 如果目录已存在，询问是否更新
if [ -d "$INSTALL_DIR" ]; then
    print_warning "目录 $INSTALL_DIR 已存在"
    read -p "是否更新？(y/n) [y]: " UPDATE_CHOICE
    UPDATE_CHOICE=${UPDATE_CHOICE:-y}
    if [ "$UPDATE_CHOICE" = "y" ] || [ "$UPDATE_CHOICE" = "Y" ]; then
        print_info "更新项目..."
        cd "$INSTALL_DIR"
        git pull origin main || git pull origin master
    else
        print_info "跳过更新"
    fi
else
    # 克隆项目
    print_info "克隆项目到 $INSTALL_DIR..."
    git clone https://github.com/YOUR_USERNAME/publish-tools.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# 创建虚拟环境
print_info "创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    print_success "虚拟环境创建成功"
else
    print_info "虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
print_info "安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 安装 Playwright 浏览器
print_info "安装 Chromium 浏览器（可能需要几分钟）..."
playwright install chromium

# 创建启动脚本
print_info "创建启动脚本..."

cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
EOF
chmod +x "$INSTALL_DIR/start.sh"

cat > "$INSTALL_DIR/start-web.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python app.py
EOF
chmod +x "$INSTALL_DIR/start-web.sh"

# 创建命令别名（可选）
print_info "是否添加命令别名到 shell？(输入 y 后可以直接运行 'publish' 命令)"
read -p "(y/n) [n]: " ADD_ALIAS
ADD_ALIAS=${ADD_ALIAS:-n}

if [ "$ADD_ALIAS" = "y" ] || [ "$ADD_ALIAS" = "Y" ]; then
    SHELL_RC=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    
    if [ -n "$SHELL_RC" ]; then
        echo "" >> "$SHELL_RC"
        echo "# 多平台发布工具" >> "$SHELL_RC"
        echo "alias publish='$INSTALL_DIR/start.sh'" >> "$SHELL_RC"
        echo "alias publish-web='$INSTALL_DIR/start-web.sh'" >> "$SHELL_RC"
        print_success "别名已添加到 $SHELL_RC"
        print_info "请运行 'source $SHELL_RC' 或重新打开终端生效"
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ 安装完成！                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 安装目录: $INSTALL_DIR"
echo ""
echo "🚀 运行方式:"
echo "   命令行模式: $INSTALL_DIR/start.sh"
echo "   Web 模式:   $INSTALL_DIR/start-web.sh"
echo ""
if [ "$ADD_ALIAS" = "y" ] || [ "$ADD_ALIAS" = "Y" ]; then
    echo "   或直接运行: publish / publish-web"
    echo ""
fi
echo "📖 使用说明: $INSTALL_DIR/README.md"
echo ""
print_success "感谢使用！如有问题请提 Issue"

