import time
from .base import BasePublisher

class XiaohongshuPublisher(BasePublisher):
    PLATFORM_NAME = "xiaohongshu"
    LOGIN_URL = "https://creator.xiaohongshu.com/"

    def login(self):
        self.page = self.context.new_page()
        self.page.goto(self.LOGIN_URL)
        
        try:
            # Check for login state
            # Look for "Publish" button or avatar
            print(f"[{self.PLATFORM_NAME}] Checking login status...")
            self.page.wait_for_selector(".header-user-info", timeout=5000) 
            # Note: Selector .header-user-info is a guess based on common patterns, needs verification
            # Actually XHS creator center often has a sidebar with "发布笔记"
            print(f"[{self.PLATFORM_NAME}] Already logged in.")
        except:
            print(f"[{self.PLATFORM_NAME}] Not logged in. Please scan QR code/Login.")
            # Wait for user
            # Waiting for the main content area or sidebar to appear
            self.page.wait_for_selector(".content-container", timeout=120000)
            print(f"[{self.PLATFORM_NAME}] Login detected.")

    def publish(self, article: dict):
        if not self.page:
            self.login()
            
        print(f"[{self.PLATFORM_NAME}] Navigating to editor...")
        
        # Click "Publish Note"
        # URL: https://creator.xiaohongshu.com/publish/publish
        self.page.goto("https://creator.xiaohongshu.com/publish/publish")
        
        try:
            # XHS requires image upload first usually
            images = article.get('images', [])
            if not images:
                print(f"[{self.PLATFORM_NAME}] Error: Xiaohongshu requires images.")
                return

            # Find file input
            # Usually hidden input type='file'
            # We use set_input_files
            
            # Wait for the upload area to ensure page is loaded
            self.page.wait_for_selector(".upload-container") 
            
            # Look for the file input
            file_input = self.page.locator("input[type='file']")
            file_input.set_input_files(images)
            
            print(f"[{self.PLATFORM_NAME}] Images uploaded.")
            
            # Wait for upload to process (spinners etc)
            time.sleep(3) 
            
            # Fill Title
            # Placeholder usually contains "填写标题"
            title_input = self.page.locator("input[placeholder*='标题']")
            title_input.fill(article['title'])
            
            # Fill Content/Description
            # Placeholder usually contains "填写正文"
            content_input = self.page.locator(".ql-editor") # Quill editor often used or similar div
            if not content_input.count():
                content_input = self.page.locator("#post-content") # Fallback ID
            
            # If standard locators fail, we try generic contenteditable
            if not content_input.count():
                 content_input = self.page.locator("[contenteditable='true']")
            
            content_input.fill(article['content'])
            
            print(f"[{self.PLATFORM_NAME}] Content filled.")
            
            time.sleep(2)

        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] Error publishing: {e}")
            self.page.screenshot(path="xhs_error.png")

