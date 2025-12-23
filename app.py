import os
import threading
from flask import Flask, render_template, request, jsonify
from playwright.sync_api import sync_playwright

# flask-cors 是可选的
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

from utils.content_generator import generate_article
from utils.auth_manager import AuthManager
from platforms.wechat import WeChatPublisher
from platforms.toutiao import ToutiaoPublisher
from platforms.xiaohongshu import XiaohongshuPublisher

app = Flask(__name__)
if HAS_CORS:
    CORS(app)

# 全局状态
publish_status = {
    "running": False,
    "current_platform": "",
    "message": "",
    "completed": []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """根据主题生成文章"""
    data = request.json
    topic = data.get('topic', '')
    
    if not topic:
        return jsonify({"error": "请输入文章主题"}), 400
    
    try:
        title, content = generate_article(topic)
        
        return jsonify({
            "success": True,
            "title": title,
            "content": content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/publish', methods=['POST'])
def publish_article():
    """发布文章到指定平台"""
    global publish_status
    
    if publish_status["running"]:
        return jsonify({"error": "正在发布中，请稍候"}), 400
    
    data = request.json
    platforms = data.get('platforms', [])
    title = data.get('title', '')
    content = data.get('content', '')
    
    if not platforms:
        return jsonify({"error": "请选择至少一个发布平台"}), 400
    if not title or not content:
        return jsonify({"error": "标题和正文不能为空"}), 400
    
    # 在后台线程中执行发布
    thread = threading.Thread(
        target=do_publish,
        args=(platforms, title, content)
    )
    thread.start()
    
    return jsonify({
        "success": True,
        "message": "开始发布，请在浏览器窗口中完成操作"
    })

def do_publish(platforms, title, content):
    """执行发布（在后台线程中运行）"""
    global publish_status
    
    publish_status = {
        "running": True,
        "current_platform": "",
        "message": "正在启动浏览器...",
        "completed": []
    }
    
    article = {
        'title': title,
        'content': content,
        'images': []
    }
    
    platform_map = {
        'wechat': WeChatPublisher,
        'toutiao': ToutiaoPublisher,
        'xiaohongshu': XiaohongshuPublisher
    }
    
    auth_manager = AuthManager()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            for platform_name in platforms:
                if platform_name not in platform_map:
                    continue
                    
                publish_status["current_platform"] = platform_name
                publish_status["message"] = f"正在处理 {platform_name}..."
                
                PlatformClass = platform_map[platform_name]
                
                # 加载登录状态
                state_path = auth_manager.load_state(PlatformClass.PLATFORM_NAME)
                if state_path:
                    context = browser.new_context(storage_state=state_path)
                else:
                    context = browser.new_context()
                
                publisher = PlatformClass(context)
                
                try:
                    publisher.login()
                    auth_manager.save_state(context, PlatformClass.PLATFORM_NAME)
                    publisher.publish(article)
                    publish_status["completed"].append(platform_name)
                except Exception as e:
                    publish_status["message"] = f"{platform_name} 发布失败: {str(e)}"
                finally:
                    context.close()
            
            browser.close()
            
    except Exception as e:
        publish_status["message"] = f"发布出错: {str(e)}"
    finally:
        publish_status["running"] = False
        publish_status["message"] = "发布完成"

@app.route('/api/status')
def get_status():
    """获取发布状态"""
    return jsonify(publish_status)

if __name__ == '__main__':
    print("=" * 50)
    print("多平台发布工具")
    print("请访问: http://127.0.0.1:8080")
    print("=" * 50)
    app.run(host='127.0.0.1', port=8080, debug=True, threaded=True)

