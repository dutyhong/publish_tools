import time
from .base import BasePublisher

class XiaohongshuPublisher(BasePublisher):
    PLATFORM_NAME = "xiaohongshu"
    LOGIN_URL = "https://creator.xiaohongshu.com/"

    def login(self):
        self.page = self.context.new_page()
        
        # 设置更长的超时时间
        self.page.set_default_timeout(60000)  # 60秒
        
        # 直接访问发布页面，如果未登录会自动跳转到登录页
        print(f"[{self.PLATFORM_NAME}] Navigating to publish page...")
        try:
            self.page.goto("https://creator.xiaohongshu.com/publish/publish", timeout=60000)
        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] Page load slow, continuing... {e}")
        
        print(f"[{self.PLATFORM_NAME}] Checking login status...")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except:
            pass
        time.sleep(3)  # 等久一点，让页面完全加载
        
        # 截图看看当前状态
        self.page.screenshot(path="xhs_login_check.png")
        
        current_url = self.page.url
        print(f"[{self.PLATFORM_NAME}] Current URL: {current_url}")
        
        # 检查是否在发布页面（已登录）
        if "publish/publish" in current_url:
            # 再检查页面内容，确认不是登录页
            page_content = self.page.content()
            if "短信登录" not in page_content and "扫码登录" not in page_content:
                print(f"[{self.PLATFORM_NAME}] ✅ Already logged in! (on publish page)")
                return
        
        # 检查是否在登录页面
        page_content = self.page.content()
        
        # 判断是否需要登录
        needs_login = (
            "login" in current_url or 
            "短信登录" in page_content or 
            "扫码登录" in page_content or
            "手机号" in page_content
        )
        
        print(f"[{self.PLATFORM_NAME}] Needs login: {needs_login}")
        
        # 如果不需要登录，直接返回
        if not needs_login:
            print(f"[{self.PLATFORM_NAME}] ✅ Already logged in!")
            return
        
        if needs_login:
            print(f"[{self.PLATFORM_NAME}] ========================================")
            print(f"[{self.PLATFORM_NAME}] 需要登录小红书创作者中心")
            print(f"[{self.PLATFORM_NAME}] 请在浏览器中选择登录方式：")
            print(f"[{self.PLATFORM_NAME}]   方式1: 点击右上角二维码图标，用小红书APP扫码")
            print(f"[{self.PLATFORM_NAME}]   方式2: 输入手机号+验证码登录")
            print(f"[{self.PLATFORM_NAME}] ========================================")
            print(f"[{self.PLATFORM_NAME}] 等待登录完成（最长3分钟）...")
            
            # 等待用户登录成功
            try:
                last_url = ""
                for i in range(180):  # 最多等3分钟
                    time.sleep(1)
                    current_url = self.page.url
                    
                    # 每10秒打印一次状态
                    if i % 10 == 0:
                        print(f"[{self.PLATFORM_NAME}] Waiting... URL: {current_url[:60]}...")
                    
                    # URL 变化时打印
                    if current_url != last_url:
                        print(f"[{self.PLATFORM_NAME}] URL changed to: {current_url}")
                        last_url = current_url
                    
                    # 检查是否已经进入发布页面
                    if "publish" in current_url and "login" not in current_url:
                        print(f"[{self.PLATFORM_NAME}] ✅ Login successful! Now on publish page.")
                        time.sleep(2)
                        return
                    
                    # 检查是否在创作者中心首页
                    if "creator.xiaohongshu.com" in current_url:
                        # 检查页面是否还有登录表单
                        try:
                            login_form = self.page.locator("text=短信登录").count()
                            phone_input = self.page.locator("text=手机号").count()
                            if login_form == 0 and phone_input == 0:
                                print(f"[{self.PLATFORM_NAME}] ✅ Login successful!")
                                time.sleep(2)
                                return
                        except:
                            pass
                    
                    # 检查是否有用户头像或昵称（登录成功的标志）
                    try:
                        avatar = self.page.locator(".user-avatar, .avatar, [class*='avatar']").count()
                        if avatar > 0:
                            print(f"[{self.PLATFORM_NAME}] ✅ Login successful! (avatar detected)")
                            time.sleep(2)
                            return
                    except:
                        pass
                
                # 超时后截图
                self.page.screenshot(path="xhs_login_timeout.png")
                print(f"[{self.PLATFORM_NAME}] ⚠️  Login timeout. Screenshot saved: xhs_login_timeout.png")
                print(f"[{self.PLATFORM_NAME}] Current URL: {self.page.url}")
                print(f"[{self.PLATFORM_NAME}] If you are logged in, press Enter to continue...")
                input()
                
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Login error: {e}")
        else:
            print(f"[{self.PLATFORM_NAME}] ✅ Already logged in!")

    def publish(self, article: dict):
        if not self.page:
            self.login()
            
        print(f"[{self.PLATFORM_NAME}] Starting publish process...")
        
        # 检查当前是否已在发布页面
        current_url = self.page.url
        if "publish/publish" not in current_url:
            print(f"[{self.PLATFORM_NAME}] Navigating to publish page...")
            try:
                self.page.goto("https://creator.xiaohongshu.com/publish/publish", timeout=30000)
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Navigation slow: {e}")
        
        # 等待页面加载（不用 networkidle，容易卡住）
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except:
            pass
        time.sleep(2)
        
        # 截图查看页面状态
        self.page.screenshot(path="xhs_publish_page.png")
        print(f"[{self.PLATFORM_NAME}] Screenshot saved: xhs_publish_page.png")
        
        # ========== 关闭"试试文字配图吧"弹窗 ==========
        print(f"[{self.PLATFORM_NAME}] Closing popup '试试文字配图吧'...")
        
        try:
            # 这个弹窗没有关闭按钮，需要点击弹窗外部
            # 弹窗在左上角，点击右侧空白区域来关闭
            
            # 方法1: 点击页面右侧区域（弹窗外部）
            # 获取页面尺寸
            viewport = self.page.viewport_size
            if viewport:
                # 点击页面右侧中间位置
                click_x = viewport['width'] - 100
                click_y = viewport['height'] // 2
                self.page.mouse.click(click_x, click_y)
                print(f"[{self.PLATFORM_NAME}] Clicked right side of page ({click_x}, {click_y})")
                time.sleep(1)
            
            # 方法2: 点击上传区域两次（灰色虚线框内）
            self.page.mouse.click(700, 400)
            print(f"[{self.PLATFORM_NAME}] Clicked center upload area (1st)")
            time.sleep(0.5)
            self.page.mouse.click(700, 400)
            print(f"[{self.PLATFORM_NAME}] Clicked center upload area (2nd)")
            time.sleep(0.5)
            
            # 方法3: 按 Escape
            self.page.keyboard.press("Escape")
            time.sleep(0.5)
            
            # 方法4: JavaScript 隐藏包含"试试文字配图"的元素
            self.page.evaluate("""
            () => {
                // 找到包含"试试文字配图"的元素并隐藏
                let allElements = document.querySelectorAll('*');
                for (let el of allElements) {
                    if (el.textContent && el.textContent.includes('试试文字配图')) {
                        // 找到这个元素的父容器（弹窗）
                        let parent = el;
                        for (let i = 0; i < 5; i++) {
                            if (parent.parentElement) {
                                parent = parent.parentElement;
                            }
                        }
                        parent.style.display = 'none';
                        parent.remove();
                        return 'Removed popup via JS';
                    }
                }
                return 'Popup not found';
            }
            """)
            print(f"[{self.PLATFORM_NAME}] Attempted to remove popup via JS")
            time.sleep(1)
            
        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] Popup handling error: {e}")
        
        self.page.screenshot(path="xhs_after_popup_close.png")
        
        # ========== 点击"上传图文"选项卡 ==========
        print(f"[{self.PLATFORM_NAME}] Clicking '上传图文' tab...")
        
        tab_clicked = False
        
        # 方法1: 直接用坐标点击选项卡（从截图分析位置）
        # 选项卡在页面中间上方，"上传图文"是第二个，大约 x=390, y=127
        try:
            self.page.mouse.click(390, 127)
            print(f"[{self.PLATFORM_NAME}] Clicked position (390, 127) for '上传图文' tab")
            time.sleep(1)
            
            # 检查是否成功（页面应该显示"上传图片"按钮而不是"上传视频"）
            page_content = self.page.content()
            if "上传图片" in page_content and "拖拽图片" in page_content:
                tab_clicked = True
                print(f"[{self.PLATFORM_NAME}] Tab switch successful!")
        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] Coordinate click failed: {e}")
        
        # 方法2: 使用 locator（带滚动）
        if not tab_clicked:
            try:
                # 精确查找选项卡区域的"上传图文"
                tabs = self.page.locator("text=上传图文")
                for i in range(tabs.count()):
                    tab = tabs.nth(i)
                    box = tab.bounding_box()
                    if box and box['y'] < 200:  # 选项卡在页面上方
                        # 先滚动到元素可见
                        tab.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        tab.click(force=True)
                        print(f"[{self.PLATFORM_NAME}] Clicked '上传图文' tab via locator")
                        tab_clicked = True
                        time.sleep(2)
                        break
            except Exception as e:
                # 不打印详细错误，因为可能还有其他方法成功
                print(f"[{self.PLATFORM_NAME}] Locator method: trying next...")
        
        # 方法3: JavaScript 点击
        if not tab_clicked:
            try:
                result = self.page.evaluate("""
                () => {
                    // 找选项卡区域（通常有特定的 class）
                    let tabs = document.querySelectorAll('[class*="tab"], [role="tab"]');
                    for (let tab of tabs) {
                        if (tab.textContent.trim() === '上传图文') {
                            tab.click();
                            return 'Clicked via tab class';
                        }
                    }
                    
                    // 遍历所有元素找精确匹配
                    let elements = document.querySelectorAll('span, div, a, li');
                    for (let el of elements) {
                        let rect = el.getBoundingClientRect();
                        // 选项卡在页面上方 (y < 200) 且文字精确匹配
                        if (el.textContent.trim() === '上传图文' && rect.top < 200 && rect.top > 50) {
                            el.click();
                            return 'Clicked via position filter: y=' + rect.top;
                        }
                    }
                    return 'Not found';
                }
                """)
                print(f"[{self.PLATFORM_NAME}] JS result: {result}")
                if 'Clicked' in result:
                    tab_clicked = True
                    time.sleep(2)
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] JS method failed: {e}")
        
        if not tab_clicked:
            print(f"[{self.PLATFORM_NAME}] ⚠️  Could not auto-click '上传图文'.")
            print(f"[{self.PLATFORM_NAME}] Please click '上传图文' tab manually, then press Enter...")
            input()
        
        time.sleep(1)
        self.page.screenshot(path="xhs_image_tab.png")
        
        try:
            # ========== 1. 上传图片 ==========
            images = article.get('images', [])
            if not images or not images[0]:
                print(f"[{self.PLATFORM_NAME}] ⚠️  小红书必须上传图片！")
                print(f"[{self.PLATFORM_NAME}] 请手动上传图片后按 Enter 继续...")
                input()
            else:
                print(f"[{self.PLATFORM_NAME}] Uploading images: {images}")
                
                upload_success = False
                
                # 方法1: 直接设置 input.upload-input（从日志看到这是正确的元素）
                try:
                    file_input = self.page.locator("input.upload-input, input[type='file']").first
                    if file_input.count() > 0:
                        file_input.set_input_files(images)
                        print(f"[{self.PLATFORM_NAME}] ✅ Images uploaded via input.upload-input")
                        upload_success = True
                        time.sleep(3)
                except Exception as e:
                    print(f"[{self.PLATFORM_NAME}] Method 1 (upload-input) failed: {e}")
                
                # 方法2: 用 JavaScript 直接设置文件
                if not upload_success:
                    try:
                        # 找到 input[type=file] 并触发
                        file_inputs = self.page.locator("input[type='file']")
                        count = file_inputs.count()
                        print(f"[{self.PLATFORM_NAME}] Found {count} file inputs")
                        
                        for i in range(count):
                            try:
                                file_inputs.nth(i).set_input_files(images)
                                print(f"[{self.PLATFORM_NAME}] ✅ Images uploaded via input #{i}")
                                upload_success = True
                                time.sleep(3)
                                break
                            except Exception as e:
                                print(f"[{self.PLATFORM_NAME}] Input #{i} failed: {e}")
                                continue
                    except Exception as e:
                        print(f"[{self.PLATFORM_NAME}] Method 2 failed: {e}")
                
                if not upload_success:
                    print(f"[{self.PLATFORM_NAME}] ⚠️  Auto upload failed.")
                    print(f"[{self.PLATFORM_NAME}] Please upload image manually, then press Enter...")
                    input()
            
            # 等待图片处理
            time.sleep(2)
            self.page.screenshot(path="xhs_after_upload.png")
            
            # ========== 2. 处理内容（小红书限制1000字）==========
            title = article['title']
            content = article['content']
            
            # 小红书正文限制 1000 字
            if len(content) > 1000:
                print(f"[{self.PLATFORM_NAME}] ⚠️  Content too long ({len(content)} chars), truncating to 1000...")
                content = content[:950] + "\n\n...(内容已截断)"
            
            # 小红书标题限制 20 字
            if len(title) > 20:
                print(f"[{self.PLATFORM_NAME}] ⚠️  Title too long ({len(title)} chars), truncating to 20...")
                title = title[:20]
            
            # ========== 3. 填写标题 ==========
            print(f"[{self.PLATFORM_NAME}] Filling title...")
            
            title_filled = False
            
            # 方法1: placeholder 包含"标题"
            try:
                title_input = self.page.locator("input[placeholder*='标题']")
                if title_input.count() > 0:
                    title_input.first.fill(title)
                    print(f"[{self.PLATFORM_NAME}] Title filled via placeholder")
                    title_filled = True
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Title method 1 failed: {e}")
            
            # 方法2: 用 JavaScript 查找
            if not title_filled:
                result = self.page.evaluate("""
                (title) => {
                    // 找标题输入框
                    let inputs = document.querySelectorAll('input, [contenteditable="true"]');
                    for (let input of inputs) {
                        let placeholder = input.getAttribute('placeholder') || '';
                        let text = input.innerText || '';
                        if (placeholder.includes('标题') || text.includes('填写标题')) {
                            if (input.tagName === 'INPUT') {
                                input.value = title;
                            } else {
                                input.innerText = title;
                            }
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            return 'Title filled via JS';
                        }
                    }
                    return 'Title input not found';
                }
                """, title)
                print(f"[{self.PLATFORM_NAME}] {result}")
                if 'filled' in result:
                    title_filled = True
            
            time.sleep(0.5)
            
            # ========== 4. 填写正文 ==========
            print(f"[{self.PLATFORM_NAME}] Filling content (length: {len(content)} chars)...")
            
            content_filled = False
            
            # 方法1: 找 Quill 编辑器
            try:
                content_editor = self.page.locator(".ql-editor, [contenteditable='true']")
                if content_editor.count() > 0:
                    # 找到最合适的编辑器（通常是较大的那个）
                    for i in range(content_editor.count()):
                        editor = content_editor.nth(i)
                        box = editor.bounding_box()
                        if box and box['height'] > 100:
                            editor.click()
                            editor.fill(content)
                            print(f"[{self.PLATFORM_NAME}] Content filled via editor")
                            content_filled = True
                            break
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Content method 1 failed: {e}")
            
            # 方法2: JavaScript
            if not content_filled:
                result = self.page.evaluate("""
                (content) => {
                    // 找正文编辑器
                    let editors = document.querySelectorAll('.ql-editor, [contenteditable="true"]');
                    for (let editor of editors) {
                        let rect = editor.getBoundingClientRect();
                        // 找较大的编辑区域
                        if (rect.height > 100) {
                            editor.focus();
                            editor.innerText = content;
                            editor.dispatchEvent(new Event('input', { bubbles: true }));
                            return 'Content filled via JS';
                        }
                    }
                    return 'Content editor not found';
                }
                """, content)
                print(f"[{self.PLATFORM_NAME}] {result}")
            
            time.sleep(1)
            self.page.screenshot(path="xhs_after_fill.png")
            
            # ========== 4. 点击发布按钮 ==========
            print(f"[{self.PLATFORM_NAME}] Looking for publish button...")
            
            publish_clicked = False
            
            # 方法1: 找"发布"按钮
            for btn_text in ["发布", "发布笔记", "立即发布"]:
                try:
                    publish_btn = self.page.get_by_text(btn_text, exact=True)
                    if publish_btn.count() > 0:
                        publish_btn.first.click()
                        print(f"[{self.PLATFORM_NAME}] Clicked '{btn_text}'")
                        publish_clicked = True
                        break
                except:
                    continue
            
            # 方法2: JavaScript
            if not publish_clicked:
                result = self.page.evaluate("""
                () => {
                    let buttons = document.querySelectorAll('button, [class*="btn"], [class*="publish"]');
                    for (let btn of buttons) {
                        let text = btn.textContent.trim();
                        if (text === '发布' || text === '发布笔记' || text.includes('发布')) {
                            btn.click();
                            return 'Clicked: ' + text;
                        }
                    }
                    return 'Publish button not found';
                }
                """)
                print(f"[{self.PLATFORM_NAME}] JS result: {result}")
                if 'Clicked' in result:
                    publish_clicked = True
            
            if not publish_clicked:
                print(f"[{self.PLATFORM_NAME}] ⚠️  Could not find publish button. Please click manually, then press Enter...")
                input()
            
            time.sleep(3)
            
            # ========== 5. 处理可能的确认弹窗 ==========
            for confirm_text in ["确定", "确认", "发布", "知道了"]:
                try:
                    confirm_btn = self.page.get_by_text(confirm_text, exact=True)
                    if confirm_btn.count() > 0:
                        confirm_btn.first.click()
                        print(f"[{self.PLATFORM_NAME}] Clicked confirm: '{confirm_text}'")
                        time.sleep(1)
                except:
                    continue
            
            time.sleep(2)
            self.page.screenshot(path="xhs_final.png")
            print(f"[{self.PLATFORM_NAME}] ✅ Publish completed!")
            
        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] Error: {e}")
            self.page.screenshot(path="xhs_error.png")
            import traceback
            traceback.print_exc()
