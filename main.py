import sys
import os
from playwright.sync_api import sync_playwright
from utils.auth_manager import AuthManager
from utils.content_generator import generate_article
from platforms.wechat import WeChatPublisher
from platforms.toutiao import ToutiaoPublisher
from platforms.xiaohongshu import XiaohongshuPublisher

def get_article_content():
    """获取文章内容：AI生成或手动输入"""
    print("\n=== 内容来源 ===")
    print("1. AI 生成（输入主题自动生成标题和正文）")
    print("2. 手动输入标题和正文")
    
    content_choice = input("选择 (1/2): ").strip()
    
    if content_choice == "1":
        # AI 生成（通义千问）
        topic = input("\n请输入文章主题: ").strip()
        print("正在生成内容，请稍候...")
        
        title, content = generate_article(topic)
        
        print(f"\n--- 生成结果 ---")
        print(f"标题: {title}")
        print(f"正文预览: {content[:200]}...")
        
        confirm = input("\n使用这个内容？(y/n) [y]: ").strip().lower()
        if confirm == 'n':
            title = input("请输入新标题: ").strip() or title
            content = input("请输入新正文: ").strip() or content
        
        return title, content
    else:
        # 手动输入
        title = input("文章标题: ").strip()
        content = input("文章正文: ").strip()
        return title, content

def main():
    print("=== Multi-Platform Publisher 多平台发布工具 ===")
    print("1. 微信公众号 (WeChat)")
    print("2. 头条号 (Toutiao)")
    print("3. 小红书 (Xiaohongshu)")
    print("4. 全部平台 (All)")
    
    choice = input("选择发布平台 (1-4): ").strip()
    
    # 获取文章内容
    title, content = get_article_content()
    
    # 图片路径
    image_path = ""
    if choice == '3' or choice == '4':
        image_path = input("图片路径 (小红书必填): ").strip()
    else:
        want_image = input("是否添加封面图？(y/n) [n]: ").strip().lower()
        if want_image == 'y':
            image_path = input("图片路径: ").strip()

    
    article = {
        'title': title,
        'content': content,
        'images': [image_path] if image_path else []
    }
    
    platforms = []
    if choice == '1':
        platforms.append(WeChatPublisher)
    elif choice == '2':
        platforms.append(ToutiaoPublisher)
    elif choice == '3':
        platforms.append(XiaohongshuPublisher)
    elif choice == '4':
        platforms.append(WeChatPublisher)
        platforms.append(ToutiaoPublisher)
        platforms.append(XiaohongshuPublisher)
    else:
        print("Invalid choice")
        return

    auth_manager = AuthManager()

    with sync_playwright() as p:
        # Launch browser (Headful so user can see/login)
        browser = p.chromium.launch(headless=False)
        
        for PlatformClass in platforms:
            platform_name = PlatformClass.PLATFORM_NAME
            print(f"\n--- Processing {platform_name} ---")
            
            # Load existing state if available
            state_path = auth_manager.load_state(platform_name)
            
            if state_path:
                print(f"Loading session from {state_path}")
                context = browser.new_context(storage_state=state_path)
            else:
                print("No existing session found. Starting fresh context.")
                context = browser.new_context()
            
            publisher = PlatformClass(context)
            
            try:
                # 1. Login (or verify login)
                publisher.login()
                
                # 2. Save state after successful login/check
                auth_manager.save_state(context, platform_name)
                
                # 3. Publish (直接开始，不询问)
                publisher.publish(article)
                print(f"Finished processing {platform_name}")
                    
            except Exception as e:
                print(f"Error on {platform_name}: {e}")
            finally:
                context.close()
                
        print("\nAll tasks completed.")
        browser.close()

if __name__ == "__main__":
    main()

