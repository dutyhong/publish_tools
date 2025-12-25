"""
浏览器智能检测和管理模块
优先使用用户本地 Chrome，如果没有则使用 Playwright 的 Chromium
"""

import os
import platform
import subprocess
import sys


def get_chrome_path():
    """获取用户电脑上 Chrome 浏览器的路径"""
    system = platform.system()
    
    if system == "Darwin":  # Mac
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    elif system == "Windows":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            # Edge 也可以用
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
    else:  # Linux
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
        ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def check_playwright_browser():
    """检查 Playwright 的 Chromium 是否已安装"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception:
        return False


def install_playwright_browser():
    """安装 Playwright 的 Chromium 浏览器"""
    print("=" * 50)
    print("正在下载浏览器，请稍候...")
    print("这只需要执行一次，大约需要下载 200MB")
    print("=" * 50)
    
    try:
        # 使用 playwright install chromium
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ 浏览器下载完成！")
            return True
        else:
            print(f"❌ 下载失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 下载出错: {e}")
        return False


def get_browser_info():
    """获取浏览器信息，返回 (executable_path, browser_type)"""
    # 1. 优先检查本地 Chrome
    chrome_path = get_chrome_path()
    if chrome_path:
        return chrome_path, "local_chrome"
    
    # 2. 检查 Playwright Chromium
    if check_playwright_browser():
        return None, "playwright_chromium"
    
    # 3. 都没有，需要下载
    return None, "need_install"


def ensure_browser():
    """确保浏览器可用，返回配置信息"""
    chrome_path, browser_type = get_browser_info()
    
    if browser_type == "local_chrome":
        print(f"✅ 检测到本地 Chrome: {chrome_path}")
        return {"executable_path": chrome_path}
    
    elif browser_type == "playwright_chromium":
        print("✅ 使用 Playwright 内置浏览器")
        return {}
    
    else:  # need_install
        print("⚠️ 未检测到 Chrome 浏览器")
        print("您有两个选择：")
        print("  1. 安装 Google Chrome (推荐)")
        print("  2. 自动下载内置浏览器 (约 200MB)")
        
        choice = input("\n输入 'y' 自动下载内置浏览器，或安装 Chrome 后按 Enter 重试: ").strip().lower()
        
        if choice == 'y':
            if install_playwright_browser():
                return {}
            else:
                print("下载失败，请手动安装 Chrome 浏览器")
                sys.exit(1)
        else:
            # 重新检测
            chrome_path = get_chrome_path()
            if chrome_path:
                print(f"✅ 检测到 Chrome: {chrome_path}")
                return {"executable_path": chrome_path}
            else:
                print("未检测到 Chrome，程序退出")
                sys.exit(1)


def launch_browser(playwright, headless=False):
    """启动浏览器（智能选择）"""
    browser_config = ensure_browser()
    
    launch_options = {
        "headless": headless,
    }
    
    if browser_config.get("executable_path"):
        launch_options["executable_path"] = browser_config["executable_path"]
        # 使用本地 Chrome 时，可能需要指定 channel
        launch_options["channel"] = None  # 不使用 channel
    
    return playwright.chromium.launch(**launch_options)


# 全局浏览器配置缓存
_browser_config = None

def get_browser_config():
    """获取浏览器配置（缓存）"""
    global _browser_config
    if _browser_config is None:
        _browser_config = ensure_browser()
    return _browser_config

