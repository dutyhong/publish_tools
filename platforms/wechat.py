import time
import re
from .base import BasePublisher

class WeChatPublisher(BasePublisher):
    PLATFORM_NAME = "wechat"
    LOGIN_URL = "https://mp.weixin.qq.com/"
    COVER_IMAGE = "/Users/duty/pictures/00000.png"

    def login(self):
        self.page = self.context.new_page()
        self.page.goto(self.LOGIN_URL)
        
        print(f"[{self.PLATFORM_NAME}] Checking login status...")
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        current_url = self.page.url
        
        if "token=" in current_url:
            print(f"[{self.PLATFORM_NAME}] Already logged in!")
            return
        
        print(f"[{self.PLATFORM_NAME}] Please scan QR code to login...")
        try:
            self.page.wait_for_url("**/cgi-bin/home**", timeout=180000)
            print(f"[{self.PLATFORM_NAME}] Login successful!")
        except:
            if "token=" in self.page.url:
                print(f"[{self.PLATFORM_NAME}] Login successful!")

    def publish(self, article: dict):
        if not self.page:
            self.login()

        print(f"[{self.PLATFORM_NAME}] Navigating to editor...")
        
        # 获取 token
        current_url = self.page.url
        token_match = re.search(r'token=(\d+)', current_url)
        
        if not token_match:
            self.page.goto("https://mp.weixin.qq.com/")
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            current_url = self.page.url
            token_match = re.search(r'token=(\d+)', current_url)
        
        if not token_match:
            print(f"[{self.PLATFORM_NAME}] Error: Could not get token.")
            return
        
        token = token_match.group(1)
        
        # 访问图文编辑器
        editor_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token={token}&lang=zh_CN"
        self.page.goto(editor_url)
        self.page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        try:
            self.page.screenshot(path="wechat_editor.png")
            
            # ========== 1. 填充标题 ==========
            print(f"[{self.PLATFORM_NAME}] Filling title...")
            
            # 用 Playwright 直接操作标题输入框
            title_filled = False
            
            # 方法1: 用 Playwright 的 fill 直接填充
            try:
                # 微信公众号编辑器的标题通常是一个 span 或 div 带有特定 class
                title_input = self.page.locator('[id="title"], .title_input, .js_title')
                if title_input.count() > 0:
                    title_input.first.click()
                    time.sleep(0.3)
                    self.page.keyboard.press("Control+a")
                    self.page.keyboard.type(article['title'])
                    print(f"[{self.PLATFORM_NAME}] Title filled via Playwright locator")
                    title_filled = True
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Playwright method failed: {e}")
            
            # 方法2: 用 JavaScript
            if not title_filled:
                title_result = self.page.evaluate("""
                (title) => {
                    // 找包含"标题"占位符的元素
                    let allElements = document.querySelectorAll('*');
                    for (let el of allElements) {
                        let placeholder = el.getAttribute('data-placeholder') || '';
                        if (placeholder.includes('标题')) {
                            el.focus();
                            el.innerText = title;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            return 'Title filled via data-placeholder';
                        }
                    }
                    
                    // 找 class 包含 title 的 contenteditable
                    let titleEl = document.querySelector('.title[contenteditable], .js_title[contenteditable], [class*="title"][contenteditable]');
                    if (titleEl) {
                        titleEl.focus();
                        titleEl.innerText = title;
                        titleEl.dispatchEvent(new Event('input', { bubbles: true }));
                        return 'Title filled via class selector';
                    }
                    
                    // 找 id 包含 title 的元素
                    titleEl = document.querySelector('#title, [id*="title"]');
                    if (titleEl) {
                        if (titleEl.tagName === 'INPUT' || titleEl.tagName === 'TEXTAREA') {
                            titleEl.value = title;
                        } else {
                            titleEl.innerText = title;
                        }
                        titleEl.dispatchEvent(new Event('input', { bubbles: true }));
                        return 'Title filled via id selector';
                    }
                    
                    return 'Title element not found';
                }
                """, article['title'])
                print(f"[{self.PLATFORM_NAME}] {title_result}")
                if 'filled' in title_result:
                    title_filled = True
            
            # 验证标题是否填入
            time.sleep(0.5)
            current_title = self.page.evaluate("""
            () => {
                let titleEl = document.querySelector('#title, .title_input, .js_title, [data-placeholder*="标题"]');
                if (titleEl) {
                    return titleEl.innerText || titleEl.value || '';
                }
                return '';
            }
            """)
            print(f"[{self.PLATFORM_NAME}] Current title in editor: '{current_title[:30]}...' (length={len(current_title)})")
            
            if not current_title.strip():
                print(f"[{self.PLATFORM_NAME}] ⚠️  Title not filled! Please fill manually, then press Enter...")
                print(f"[{self.PLATFORM_NAME}] Title to fill: {article['title']}")
                input()
            
            time.sleep(0.5)
            
            # ========== 2. 填充正文 ==========
            print(f"[{self.PLATFORM_NAME}] Filling content...")
            
            content_result = self.page.evaluate("""
            (content) => {
                // 方法1: 找包含"正文"或"从这里开始"占位符的元素
                let allElements = document.querySelectorAll('[contenteditable="true"]');
                for (let el of allElements) {
                    let placeholder = el.getAttribute('data-placeholder') || '';
                    let text = el.innerText || '';
                    if (placeholder.includes('正文') || placeholder.includes('从这里') || 
                        text.includes('从这里开始写正文')) {
                        el.focus();
                        el.innerText = content;
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        return 'Content filled via placeholder/text match';
                    }
                }
                
                // 方法2: 找 class 包含 content/editor/body 的大编辑区域
                let contentEl = document.querySelector('.content[contenteditable], .editor-content[contenteditable], .js_content[contenteditable]');
                if (contentEl) {
                    contentEl.focus();
                    contentEl.innerText = content;
                    contentEl.dispatchEvent(new Event('input', { bubbles: true }));
                    return 'Content filled via class selector';
                }
                
                // 方法3: 找最大的可见 contenteditable（排除标题）
                let editables = document.querySelectorAll('[contenteditable="true"]');
                let maxHeight = 0;
                let bestEl = null;
                for (let el of editables) {
                    let rect = el.getBoundingClientRect();
                    // 只要高度大于 200 的（排除标题等小区域）
                    if (rect.height > 200 && rect.height > maxHeight && rect.width > 0) {
                        maxHeight = rect.height;
                        bestEl = el;
                    }
                }
                if (bestEl) {
                    bestEl.focus();
                    bestEl.innerText = content;
                    bestEl.dispatchEvent(new Event('input', { bubbles: true }));
                    return 'Content filled via largest editable (height=' + maxHeight + ')';
                }
                
                return 'Content element not found';
            }
            """, article['content'])
            print(f"[{self.PLATFORM_NAME}] {content_result}")
            
            time.sleep(1)
            self.page.screenshot(path="wechat_after_fill.png")
            print(f"[{self.PLATFORM_NAME}] Screenshot saved: wechat_after_fill.png")
            
            # ========== 3. 点击发表按钮 ==========
            print(f"[{self.PLATFORM_NAME}] Looking for publish button...")
            
            # 尝试多种方式找发表按钮
            publish_clicked = False
            
            # 方法1: 精确匹配"发表"
            try:
                publish_btn = self.page.get_by_text("发表", exact=True)
                if publish_btn.count() > 0:
                    publish_btn.first.click(timeout=5000)
                    print(f"[{self.PLATFORM_NAME}] Clicked '发表'")
                    publish_clicked = True
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Method 1 failed: {e}")
            
            # 方法2: 用 JavaScript 找按钮
            if not publish_clicked:
                try:
                    result = self.page.evaluate("""
                    () => {
                        let buttons = document.querySelectorAll('button, .weui-desktop-btn, [class*="btn"]');
                        for (let btn of buttons) {
                            let text = btn.textContent.trim();
                            if (text === '发表' || text === '发布') {
                                btn.click();
                                return 'Clicked: ' + text;
                            }
                        }
                        return 'No publish button found';
                    }
                    """)
                    print(f"[{self.PLATFORM_NAME}] JS result: {result}")
                    if 'Clicked' in result:
                        publish_clicked = True
                except Exception as e:
                    print(f"[{self.PLATFORM_NAME}] Method 2 failed: {e}")
            
            if not publish_clicked:
                print(f"[{self.PLATFORM_NAME}] ⚠️  Could not find publish button. Please click manually, then press Enter...")
                input()
            
            time.sleep(2)
            self.page.screenshot(path="wechat_publish_dialog.png")
            
            # ========== 4. 处理发表弹窗 ==========
            print(f"[{self.PLATFORM_NAME}] Handling publish dialog...")
            
            # 等待弹窗出现
            time.sleep(1)
            
            # 4.1 上传封面图片
            cover_image = self.COVER_IMAGE
            if article.get('images') and len(article['images']) > 0 and article['images'][0]:
                cover_image = article['images'][0]
            
            print(f"[{self.PLATFORM_NAME}] Uploading cover: {cover_image}")
            
            # 使用 JavaScript 在弹窗中找到封面上传区域并触发点击
            cover_uploaded = False
            
            try:
                # 方法1: 找弹窗中的"拖拽或选择封面"文字并点击
                upload_text = self.page.get_by_text("拖拽或选择封面")
                if upload_text.count() > 0:
                    print(f"[{self.PLATFORM_NAME}] Found '拖拽或选择封面', trying to upload...")
                    # 使用 file chooser 上传
                    with self.page.expect_file_chooser(timeout=3000) as fc_info:
                        upload_text.first.click(timeout=3000)
                    file_chooser = fc_info.value
                    file_chooser.set_files(cover_image)
                    print(f"[{self.PLATFORM_NAME}] Cover uploaded!")
                    cover_uploaded = True
                    time.sleep(3)  # 等待图片上传完成
                else:
                    print(f"[{self.PLATFORM_NAME}] '拖拽或选择封面' not found")
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Cover upload method 1 failed: {e}")
            
            # 方法2: 如果方法1失败，手动上传
            if not cover_uploaded:
                print(f"[{self.PLATFORM_NAME}] ⚠️  Auto upload failed. Please upload cover manually.")
                print(f"[{self.PLATFORM_NAME}] Click '拖拽或选择封面', select image, then press Enter...")
                input()
                cover_uploaded = True
            
            # 4.2 填写摘要（只在发表弹窗中操作，不影响编辑器）
            summary = article['content'][:100] if len(article['content']) > 100 else article['content']
            # 移除换行符，只保留纯文本
            summary = summary.replace('\n', ' ').replace('\r', '')
            
            try:
                # 截图查看当前弹窗状态
                self.page.screenshot(path="wechat_before_summary.png")
                
                # 用 JavaScript 精确定位弹窗中的摘要框
                summary_result = self.page.evaluate("""
                (summary) => {
                    // 首先找到发表弹窗（通常有特定的 class）
                    let dialogs = document.querySelectorAll('.weui-desktop-dialog__wrp, .publish-dialog, [class*="dialog"], [class*="modal"]');
                    
                    for (let dialog of dialogs) {
                        // 检查弹窗是否可见
                        let style = window.getComputedStyle(dialog);
                        if (style.display === 'none' || style.visibility === 'hidden') continue;
                        
                        // 在弹窗中找摘要相关的输入框
                        let textareas = dialog.querySelectorAll('textarea');
                        for (let ta of textareas) {
                            // 检查是否是摘要输入框（不是标题）
                            let placeholder = (ta.getAttribute('placeholder') || '').toLowerCase();
                            let parent = ta.closest('[class*="summary"], [class*="digest"], [class*="desc"]');
                            
                            // 如果 placeholder 包含摘要相关词，或者在摘要容器内
                            if (placeholder.includes('摘要') || placeholder.includes('简介') || 
                                placeholder.includes('描述') || parent) {
                                ta.focus();
                                ta.value = summary;
                                ta.dispatchEvent(new Event('input', { bubbles: true }));
                                ta.dispatchEvent(new Event('change', { bubbles: true }));
                                return 'Summary filled in dialog textarea';
                            }
                        }
                    }
                    
                    // 如果上面没找到，找页面上有 maxlength 限制的 textarea（摘要通常有字数限制）
                    let textareas = document.querySelectorAll('textarea[maxlength]');
                    for (let ta of textareas) {
                        let maxlen = parseInt(ta.getAttribute('maxlength') || '0');
                        // 摘要通常限制 120 或 140 字左右
                        if (maxlen >= 100 && maxlen <= 200) {
                            ta.focus();
                            ta.value = summary;
                            ta.dispatchEvent(new Event('input', { bubbles: true }));
                            return 'Summary filled via maxlength textarea';
                        }
                    }
                    
                    return 'No summary textarea found (skipped)';
                }
                """, summary)
                print(f"[{self.PLATFORM_NAME}] {summary_result}")
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Summary fill skipped: {e}")
            
            time.sleep(1)
            
            # 4.3 点击发表/确认按钮
            for btn_text in ["发表", "确认发表", "确定"]:
                try:
                    btn = self.page.get_by_text(btn_text, exact=True)
                    if btn.count() > 0:
                        btn.first.click()
                        print(f"[{self.PLATFORM_NAME}] Clicked '{btn_text}'")
                        time.sleep(2)
                        break
                except:
                    continue
            
            # ========== 5. 处理AI声明弹窗 ==========
            print(f"[{self.PLATFORM_NAME}] Checking AI declaration dialog...")
            
            # 等待弹窗出现
            time.sleep(1)
            
            # 点击"无需声明并发表"
            try:
                no_declare = self.page.get_by_text("无需声明并发表")
                if no_declare.count() > 0:
                    no_declare.first.click()
                    print(f"[{self.PLATFORM_NAME}] Clicked '无需声明并发表'")
                    time.sleep(2)
                else:
                    # 用 JavaScript 强制点击
                    result = self.page.evaluate("""
                    () => {
                        let buttons = document.querySelectorAll('button, .weui-desktop-btn, [class*="btn"]');
                        for (let btn of buttons) {
                            if (btn.textContent.includes('无需声明') || btn.textContent.includes('直接发表')) {
                                btn.click();
                                return 'Clicked via JS: ' + btn.textContent;
                            }
                        }
                        return 'Button not found';
                    }
                    """)
                    print(f"[{self.PLATFORM_NAME}] {result}")
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] AI declaration handling failed: {e}")
            
            time.sleep(2)
            
            # 最后检查是否还有其他弹窗需要确认
            for btn_text in ["确定", "确认", "知道了"]:
                try:
                    btn = self.page.get_by_text(btn_text, exact=True)
                    if btn.count() > 0:
                        btn.first.click()
                        print(f"[{self.PLATFORM_NAME}] Clicked '{btn_text}'")
                        time.sleep(1)
                except:
                    continue
            
            print(f"[{self.PLATFORM_NAME}] ✅ Publish completed!")
            
        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] Error: {e}")
            self.page.screenshot(path="wechat_error.png")
            import traceback
            traceback.print_exc()
