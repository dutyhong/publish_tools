"""
纯 API 服务 - 可部署到云服务器
只提供 AI 内容生成功能，浏览器自动化在用户本地运行
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.content_generator import ContentGenerator

app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 初始化内容生成器
generator = ContentGenerator()

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """根据主题生成文章标题和正文"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        
        if not topic:
            return jsonify({'error': '请输入文章主题'}), 400
        
        title, content = generator.generate(topic)
        
        return jsonify({
            'success': True,
            'title': title,
            'content': content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    return '''
    <html>
    <head><title>多平台发布工具 API</title></head>
    <body style="font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>📝 多平台发布工具 API</h1>
        <h2>接口说明</h2>
        <h3>POST /api/generate</h3>
        <p>根据主题生成文章</p>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
请求:
POST /api/generate
Content-Type: application/json

{
    "topic": "人工智能的发展趋势"
}

响应:
{
    "success": true,
    "title": "2024年AI发展五大趋势",
    "content": "正文内容..."
}
        </pre>
        
        <h3>使用方式</h3>
        <ol>
            <li>本服务部署到云端，提供 AI 生成能力</li>
            <li>用户在本地运行 main.py 进行发布</li>
            <li>或通过 API 集成到其他应用</li>
        </ol>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("=" * 50)
    print("多平台发布工具 - API 服务")
    print("=" * 50)
    print("本地访问: http://localhost:8080")
    print("API 端点: POST /api/generate")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8080, debug=False)

