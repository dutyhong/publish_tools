#!/usr/bin/env python3
"""
打包脚本：生成独立可执行文件
运行: python build.py

用户无需安装 Python 即可使用打包后的程序
"""

import subprocess
import platform
import shutil
import os
import sys

def check_pyinstaller():
    """检查 PyInstaller 是否安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

def build():
    """执行打包"""
    system = platform.system()
    print(f"\n{'=' * 50}")
    print(f"🔨 正在为 {system} 打包...")
    print(f"{'=' * 50}\n")
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()
    
    # 清理旧的构建
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name}/...")
            shutil.rmtree(dir_name)
    
    # 数据文件分隔符（Windows 用 ; ，其他系统用 :）
    sep = ';' if system == 'Windows' else ':'
    
    # PyInstaller 命令
    cmd = [
        'pyinstaller',
        '--name=多平台发布工具',
        f'--add-data=templates{sep}templates',
        f'--add-data=static{sep}static',
        '--hidden-import=playwright',
        '--hidden-import=playwright.sync_api',
        '--hidden-import=playwright._impl',
        '--hidden-import=flask',
        '--hidden-import=openai',
        '--hidden-import=greenlet',
        '--collect-all=playwright',
        '--noconfirm',
        '--console',  # 显示控制台窗口
        'app.py'
    ]
    
    print("执行命令:")
    print(' '.join(cmd))
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        return False
    
    # 复制额外文件
    dist_dir = os.path.join('dist', '多平台发布工具')
    
    # 复制 platforms 和 utils 目录（如果需要）
    for folder in ['platforms', 'utils', 'auth_states']:
        src = folder
        dst = os.path.join(dist_dir, folder)
        if os.path.exists(src) and not os.path.exists(dst):
            if folder == 'auth_states':
                os.makedirs(dst, exist_ok=True)
            else:
                shutil.copytree(src, dst)
    
    # 创建启动说明
    readme_content = """# 多平台发布工具 - 使用说明

## 快速开始

### Windows 用户
双击 `多平台发布工具.exe` 即可运行

### Mac/Linux 用户
在终端中运行：
```
./多平台发布工具
```

## 首次使用

1. 程序会自动检测浏览器
   - 如果已安装 Chrome，直接使用
   - 如果没有，会提示下载内置浏览器（约 200MB）

2. 浏览器自动打开 http://127.0.0.1:8080

3. 选择平台、输入主题、生成内容、发布！

## 注意事项

- 首次使用各平台需要扫码登录
- 登录状态会自动保存
- 关闭程序窗口将停止服务

## 问题反馈

如有问题，请联系开发者
"""
    
    with open(os.path.join(dist_dir, '使用说明.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n{'=' * 50}")
    print("✅ 打包完成！")
    print(f"{'=' * 50}")
    print(f"\n📁 输出目录: dist/多平台发布工具/")
    print(f"\n📦 分发方式:")
    print(f"   1. 将 'dist/多平台发布工具' 文件夹压缩成 zip")
    print(f"   2. 分享给用户下载")
    print(f"   3. 用户解压后双击运行即可")
    
    # 计算大小
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(dist_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    size_mb = total_size / (1024 * 1024)
    print(f"\n📊 文件大小: {size_mb:.1f} MB")
    
    return True

def create_zip():
    """创建 zip 压缩包"""
    dist_dir = os.path.join('dist', '多平台发布工具')
    if not os.path.exists(dist_dir):
        print("请先运行打包")
        return
    
    system = platform.system().lower()
    zip_name = f"多平台发布工具_{system}"
    
    print(f"\n正在创建压缩包 {zip_name}.zip ...")
    shutil.make_archive(
        os.path.join('dist', zip_name),
        'zip',
        'dist',
        '多平台发布工具'
    )
    print(f"✅ 压缩包已创建: dist/{zip_name}.zip")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='打包多平台发布工具')
    parser.add_argument('--zip', action='store_true', help='打包后创建 zip 压缩包')
    args = parser.parse_args()
    
    if build():
        if args.zip:
            create_zip()

