import time
from .base import BasePublisher

class ToutiaoPublisher(BasePublisher):
    PLATFORM_NAME = "toutiao"
    LOGIN_URL = "https://mp.toutiao.com/"

    def login(self):
        self.page = self.context.new_page()
        
        # 直接访问后台页面
        print(f"[{self.PLATFORM_NAME}] Navigating to backend...")
        self.page.goto("https://mp.toutiao.com/profile_v4/index")
        
        # 等待页面加载
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        current_url = self.page.url
        print(f"[{self.PLATFORM_NAME}] Current URL: {current_url}")
        
        # 判断是否已登录
        # 如果在后台页面，说明已登录
        if "profile_v4" in current_url or "index" in current_url:
            # 额外确认：检查页面是否有登录相关的元素
            if self.page.locator("text=扫码登录").count() > 0 or self.page.locator("text=账号密码登录").count() > 0:
                print(f"[{self.PLATFORM_NAME}] Login page detected. Please scan QR code...")
                # 等待登录成功（URL 变化或者登录元素消失）
                try:
                    self.page.wait_for_url("**/profile_v4/**", timeout=180000)
                except:
                    pass
                print(f"[{self.PLATFORM_NAME}] Login completed.")
            else:
                print(f"[{self.PLATFORM_NAME}] Already logged in!")
        else:
            # 可能跳转到了登录页
            print(f"[{self.PLATFORM_NAME}] Redirected to login. Please scan QR code...")
            try:
                self.page.wait_for_url("**/profile_v4/**", timeout=180000)
            except:
                pass
            print(f"[{self.PLATFORM_NAME}] Login completed.")

    def publish(self, article: dict):
        if not self.page:
            self.login()
            
        print(f"[{self.PLATFORM_NAME}] Navigating to editor...")
        self.page.goto("https://mp.toutiao.com/profile_v4/graphic/publish")
        
        # 等待页面完全加载
        self.page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        try:
            # 截图
            self.page.screenshot(path="toutiao_before_fill.png")
            
            # ========== 先分析页面结构 ==========
            print(f"[{self.PLATFORM_NAME}] Analyzing page structure...")
            
            page_info = self.page.evaluate("""
            () => {
                let info = { editables: [], inputs: [], textareas: [] };
                
                // contenteditable 元素
                document.querySelectorAll('[contenteditable="true"]').forEach((el, i) => {
                    let rect = el.getBoundingClientRect();
                    info.editables.push({
                        index: i,
                        tag: el.tagName,
                        className: el.className,
                        top: rect.top,
                        height: rect.height
                    });
                });
                
                // input 元素
                document.querySelectorAll('input').forEach((el, i) => {
                    let rect = el.getBoundingClientRect();
                    if (rect.width > 100) {  // 过滤掉太小的
                        info.inputs.push({
                            index: i,
                            type: el.type,
                            placeholder: el.placeholder,
                            top: rect.top
                        });
                    }
                });
                
                // textarea 元素
                document.querySelectorAll('textarea').forEach((el, i) => {
                    let rect = el.getBoundingClientRect();
                    info.textareas.push({
                        index: i,
                        placeholder: el.placeholder,
                        top: rect.top,
                        height: rect.height
                    });
                });
                
                return info;
            }
            """)
            
            print(f"[{self.PLATFORM_NAME}] Contenteditable elements:")
            for item in page_info['editables']:
                print(f"[{self.PLATFORM_NAME}]   #{item['index']}: {item['tag']} top={item['top']:.0f}, height={item['height']:.0f}, class={item['className'][:50]}")
            
            print(f"[{self.PLATFORM_NAME}] Input elements:")
            for item in page_info['inputs']:
                print(f"[{self.PLATFORM_NAME}]   #{item['index']}: type={item['type']}, placeholder={item['placeholder'][:30] if item['placeholder'] else 'none'}, top={item['top']:.0f}")
            
            print(f"[{self.PLATFORM_NAME}] Textarea elements:")
            for item in page_info['textareas']:
                print(f"[{self.PLATFORM_NAME}]   #{item['index']}: placeholder={item['placeholder'][:30] if item['placeholder'] else 'none'}, top={item['top']:.0f}, height={item['height']:.0f}")
            
            # ========== 标题 ==========
            print(f"[{self.PLATFORM_NAME}] Filling title...")
            
            # 先尝试 textarea（标题可能是 textarea）
            title_filled = False
            
            # 方法1: 通过 placeholder 找 textarea
            try:
                textarea = self.page.locator("textarea").first
                if textarea.count() > 0:
                    textarea.fill(article['title'])
                    print(f"[{self.PLATFORM_NAME}] Title filled via textarea")
                    title_filled = True
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Textarea failed: {e}")
            
            # 方法2: 通过 input 找
            if not title_filled:
                try:
                    title_input = self.page.locator("input[type='text']").first
                    if title_input.count() > 0:
                        title_input.fill(article['title'])
                        print(f"[{self.PLATFORM_NAME}] Title filled via input")
                        title_filled = True
                except Exception as e:
                    print(f"[{self.PLATFORM_NAME}] Input failed: {e}")
            
            # 方法3: 点击标题区域然后输入
            if not title_filled:
                try:
                    # 点击包含"标题"文字的区域
                    title_area = self.page.get_by_text("请输入文章标题").first
                    title_area.click()
                    time.sleep(0.3)
                    self.page.keyboard.type(article['title'])
                    print(f"[{self.PLATFORM_NAME}] Title filled via click and type")
                    title_filled = True
                except Exception as e:
                    print(f"[{self.PLATFORM_NAME}] Click method failed: {e}")
            
            if not title_filled:
                print(f"[{self.PLATFORM_NAME}] ⚠️  Could not fill title automatically")
            
            time.sleep(0.5)
            
            # ========== 正文 ==========
            print(f"[{self.PLATFORM_NAME}] Filling content...")
            
            # 正文通常在标题下方，高度较大
            content_js = """
            (content) => {
                let editables = document.querySelectorAll('[contenteditable="true"]');
                let contentEl = null;
                let maxHeight = 0;
                
                // 找高度最大的编辑器作为正文
                editables.forEach(el => {
                    let rect = el.getBoundingClientRect();
                    if (rect.height > maxHeight) {
                        maxHeight = rect.height;
                        contentEl = el;
                    }
                });
                
                if (contentEl) {
                    contentEl.focus();
                    contentEl.innerText = content;
                    contentEl.dispatchEvent(new Event('input', { bubbles: true }));
                    return 'Content filled at height=' + maxHeight;
                }
                return 'Content element not found';
            }
            """
            result = self.page.evaluate(content_js, article['content'])
            print(f"[{self.PLATFORM_NAME}] {result}")
            
            # 截图确认
            time.sleep(1)
            self.page.screenshot(path="toutiao_after_fill.png")
            print(f"[{self.PLATFORM_NAME}] Screenshots saved: toutiao_before_fill.png, toutiao_after_fill.png")
            
            # 如果 JS 方法也失败了，提供手动模式
            if "not found" in result.lower():
                print(f"\n[{self.PLATFORM_NAME}] ⚠️  Auto-fill failed. Entering manual mode...")
                print(f"[{self.PLATFORM_NAME}] 1. Click on the TITLE area in browser")
                input("Press Enter when ready: ")
                self.page.keyboard.type(article['title'])
                
                print(f"[{self.PLATFORM_NAME}] 2. Click on the CONTENT area in browser")
                input("Press Enter when ready: ")
                self.page.keyboard.type(article['content'])
            
            # ========== 选择无封面 ==========
            # 展示封面选项：单图、三图、无封面
            print(f"[{self.PLATFORM_NAME}] Looking for cover options (单图/三图/无封面)...")
            try:
                # 先滚动到页面底部附近，封面选项通常在下方
                self.page.keyboard.press("End")
                time.sleep(0.5)
                
                # 方法1: 找到"展示封面"区域，然后定位"无封面"
                result = self.page.evaluate("""
                () => {
                    // 查找所有包含这些文字的元素
                    let allText = document.body.innerText;
                    let hasOptions = allText.includes('单图') && allText.includes('三图');
                    
                    if (!hasOptions) {
                        return 'Cover options not found on page';
                    }
                    
                    // 找到"无封面"文字的元素
                    let walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    
                    let node;
                    while (node = walker.nextNode()) {
                        if (node.textContent.trim() === '无封面') {
                            // 找到了，点击它的父元素
                            let parent = node.parentElement;
                            // 可能需要点击更上层的容器
                            let clickTarget = parent;
                            for (let i = 0; i < 3; i++) {
                                if (clickTarget.onclick || clickTarget.tagName === 'LABEL' || 
                                    clickTarget.classList.contains('radio') || 
                                    clickTarget.querySelector('input[type="radio"]')) {
                                    break;
                                }
                                if (clickTarget.parentElement) {
                                    clickTarget = clickTarget.parentElement;
                                }
                            }
                            clickTarget.click();
                            return 'Clicked: ' + clickTarget.tagName + ' class=' + clickTarget.className;
                        }
                    }
                    
                    // 方法2: 直接找 radio 按钮组，点击最后一个（无封面通常是第三个）
                    let coverSection = null;
                    document.querySelectorAll('*').forEach(el => {
                        if (el.textContent.includes('展示封面') && el.textContent.includes('单图')) {
                            coverSection = el;
                        }
                    });
                    
                    if (coverSection) {
                        let radios = coverSection.querySelectorAll('input[type="radio"], [role="radio"], .radio-item, [class*="radio"]');
                        if (radios.length >= 3) {
                            radios[2].click();  // 第三个是"无封面"
                            return 'Clicked 3rd radio in cover section';
                        }
                        // 找可点击的元素
                        let items = coverSection.querySelectorAll('[class*="item"], label, span');
                        for (let item of items) {
                            if (item.textContent.includes('无封面')) {
                                item.click();
                                return 'Clicked item containing 无封面';
                            }
                        }
                    }
                    
                    return 'Could not click 无封面';
                }
                """)
                print(f"[{self.PLATFORM_NAME}] Cover selection result: {result}")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Could not select '无封面': {e}")
            
            # ========== 自动发布 ==========
            print(f"[{self.PLATFORM_NAME}] Clicking publish button...")
            try:
                # 用 JavaScript 找到并点击发布按钮
                result = self.page.evaluate("""
                () => {
                    // 找所有按钮和可点击元素
                    let buttons = document.querySelectorAll('button, [role="button"], .btn, [class*="btn"]');
                    
                    for (let btn of buttons) {
                        let text = btn.textContent.trim();
                        // 匹配"预览并发布"、"发布"等
                        if (text === '预览并发布' || text === '发布' || text === '发布文章') {
                            btn.click();
                            return 'Clicked: ' + btn.tagName + ' text=' + text;
                        }
                    }
                    
                    // 方法2: 找包含"发布"的按钮
                    for (let btn of buttons) {
                        let text = btn.textContent.trim();
                        if (text.includes('发布') && !text.includes('定时')) {
                            btn.click();
                            return 'Clicked button containing 发布: ' + text;
                        }
                    }
                    
                    return 'Publish button not found';
                }
                """)
                print(f"[{self.PLATFORM_NAME}] Publish result: {result}")
                
                if 'Clicked' in result:
                    time.sleep(2)
                    
                    # 检查是否有确认弹窗
                    confirm_result = self.page.evaluate("""
                    () => {
                        let confirmBtns = document.querySelectorAll('button, [role="button"]');
                        for (let btn of confirmBtns) {
                            let text = btn.textContent.trim();
                            if (text.includes('确认') || text.includes('确定') || text === '发布') {
                                btn.click();
                                return 'Confirmed: ' + text;
                            }
                        }
                        return 'No confirm dialog';
                    }
                    """)
                    print(f"[{self.PLATFORM_NAME}] {confirm_result}")
                    
                    print(f"[{self.PLATFORM_NAME}] ✅ Article published successfully!")
                else:
                    print(f"[{self.PLATFORM_NAME}] ⚠️  Could not find publish button. Please publish manually.")
                    input("Press Enter after publishing: ")
                    
            except Exception as e:
                print(f"[{self.PLATFORM_NAME}] Error clicking publish: {e}")
                input("Press Enter after publishing manually: ")
            
            time.sleep(2)

        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] Error: {e}")
            self.page.screenshot(path="toutiao_error.png")
