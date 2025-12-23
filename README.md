# 📝 多平台内容发布工具

一键将文章发布到微信公众号、头条号、小红书等多个自媒体平台，支持 AI 自动生成内容。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-自动化-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特点

- 🚀 **多平台支持**：微信公众号、头条号、小红书
- 🤖 **AI 内容生成**：输入主题，自动生成标题和正文（通义千问）
- 💾 **登录状态保存**：扫码一次，后续自动登录
- 🖥️ **双模式运行**：命令行 / Web 界面
- 📸 **自动截图**：发布过程自动截图，方便调试

## 🎬 演示

```
=== Multi-Platform Publisher 多平台发布工具 ===
1. 微信公众号 (WeChat)
2. 头条号 (Toutiao)  
3. 小红书 (Xiaohongshu)
4. 全部平台 (All)

选择发布平台 (1-4): 1

=== 内容来源 ===
1. AI 生成（输入主题自动生成标题和正文）
2. 手动输入标题和正文

选择 (1/2): 1
请输入文章主题: 人工智能的发展趋势

正在生成内容，请稍候...
--- 生成结果 ---
标题: 2024年AI发展五大趋势：从ChatGPT到AGI
正文预览: 人工智能正在以前所未有的速度改变我们的世界...
```

## 🚀 快速开始

### 方式一：一键安装（推荐）

**Mac / Linux：**
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/publish-tools/main/install.sh | bash
```

**Windows (PowerShell)：**
```powershell
irm https://raw.githubusercontent.com/YOUR_USERNAME/publish-tools/main/install.ps1 | iex
```

### 方式二：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/publish-tools.git
cd publish-tools

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装浏览器
playwright install chromium

# 5. 运行
python main.py
```

## 📖 使用指南

### 命令行模式

```bash
python main.py
```

按提示操作：
1. 选择发布平台
2. 选择内容来源（AI生成/手动输入）
3. 首次使用需扫码登录
4. 自动完成发布

### Web 界面模式

```bash
python app.py
```

浏览器访问 `http://localhost:8080`

## ⚙️ 配置

### AI 内容生成

默认使用通义千问，需要配置 API Key：

编辑 `utils/content_generator.py`：

```python
API_KEY = "your-api-key-here"  # 替换为你的 API Key
```

获取 API Key：[阿里云 DashScope](https://dashscope.console.aliyun.com/)

### 封面图片

微信公众号默认封面路径：

编辑 `platforms/wechat.py`：

```python
COVER_IMAGE = "/path/to/your/cover.png"  # 替换为你的图片路径
```

## 📁 项目结构

```
publish-tools/
├── main.py                 # 命令行入口
├── app.py                  # Web 服务入口
├── api_server.py           # API 服务（可部署到云端）
├── requirements.txt        # 依赖列表
├── platforms/              # 各平台发布模块
│   ├── base.py            # 基类
│   ├── wechat.py          # 微信公众号
│   ├── toutiao.py         # 头条号
│   └── xiaohongshu.py     # 小红书
├── utils/                  # 工具模块
│   ├── auth_manager.py    # 登录状态管理
│   └── content_generator.py # AI 内容生成
├── templates/              # Web 页面模板
├── auth_states/            # 登录状态存储（自动生成）
└── docs/
    ├── 产品文档.md
    └── 部署指南.md
```

## 🔧 常见问题

### Q: 提示"未登录"怎么办？

A: 删除 `auth_states/` 目录下对应平台的 JSON 文件，重新扫码登录。

### Q: 内容没有填入编辑器？

A: 平台页面结构可能更新了，请提 Issue 反馈。

### Q: AI 生成失败？

A: 检查 API Key 是否正确，网络是否通畅。

### Q: 支持 Windows 吗？

A: 支持！但需要 Python 3.8+ 环境。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📜 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐️

---

**注意**：本工具仅供学习交流使用，请遵守各平台的使用规范。

