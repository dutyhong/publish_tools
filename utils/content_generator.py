import openai
from typing import Tuple

# 通义千问配置
API_KEY = "sk-eff2128169cc440db8a76dc084bcc8ab"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen3-max"


class ContentGenerator:
    """使用通义千问生成文章"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        
    def generate(self, topic: str) -> Tuple[str, str]:
        """根据主题生成文章标题和正文"""
        print(f"[AI] 正在调用通义千问生成文章...")
        print(f"[AI] 主题: {topic}")
        
        prompt = f"""请根据以下主题，生成一篇适合发布在微信公众号和头条的文章。先收集网上其他人的看法，再结合其他人的看法和观点，总结发表自己的看法，一定要有自己的观点。

主题：{topic}

要求：
1. 标题要吸引人，20字以内
2. 正文800-1500字，结构清晰，分段落
3. 内容要有价值，适合大众阅读
4. 语言通俗易懂，避免过于专业的术语

请按以下格式输出：
【标题】
（这里写标题）

【正文】
（这里写正文）
"""
        
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的自媒体内容创作者，擅长撰写吸引人的文章。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        print(f"[AI] 生成完成!")
        
        return self._parse_result(result)
    
    def _parse_result(self, result: str) -> Tuple[str, str]:
        """解析返回结果"""
        title = ""
        content = ""
        
        if "【标题】" in result:
            parts = result.split("【标题】")
            if len(parts) > 1:
                title_part = parts[1].split("【正文】")[0] if "【正文】" in parts[1] else parts[1]
                title = title_part.strip().strip("：:").strip()
        
        if "【正文】" in result:
            parts = result.split("【正文】")
            if len(parts) > 1:
                content = parts[1].strip()
        
        if not title:
            lines = result.strip().split("\n")
            title = lines[0].strip()[:30]
        
        if not content:
            lines = result.strip().split("\n")
            content = "\n".join(lines[1:]).strip()
        
        return title, content


# 创建全局实例
generator = ContentGenerator()


def generate_article(topic: str) -> Tuple[str, str]:
    """生成文章的便捷函数"""
    return generator.generate(topic)
