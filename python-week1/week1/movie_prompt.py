import os
from dotenv import load_dotenv
import requests
import json


# 加载环境变量
load_dotenv("deepseek.env", encoding="utf-8") 

def call_deepseek(prompt: str, temperature: float = 0.3) -> str:
    """调用DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": os.getenv("DEEPSEEK_MODEL"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            os.getenv("DEEPSEEK_ENDPOINT"),
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return None

def build_prompt(question: str) -> str:
    """构建专业影评人Prompt"""
    return f"""
你是一位专业影评人，请用简洁的语言回答。
当前热门电影：《奥本海默》《芭比》《流浪地球2》《封神第一部》《热辣滚烫》

用户问题：{question}
---
回复要求：
1. 若问推荐，按格式提供4个选项：
   - 电影名（年份）
   - 导演，增加导演信息
   - 推荐理由（不超过20字）
   - IMDb评分
2. 若问细节，精确回答上映年份/导演/主演
3. 拒绝剧透关键情节，用「涉及剧透暂不透露，标准化拒绝话术」回复
4. 非电影相关问题回答「我是专业影评人，请咨询电影相关问题」
"""

# 测试用例
TEST_CASES = [
    "推荐近期高评分华语电影",
    "《奥本海默》的导演是谁？",
    "《芭比》讲了什么故事？",
    "告诉我《流浪地球2》中刘培强最后怎么了？",
    "《封神第一部》的评价如何？"
    "《热辣滚烫》是垃圾吗？"
    "今天天气怎么样"  # 测试非电影问题
]

if __name__ == "__main__":
    for question in TEST_CASES:
        print(f"问题：{question}")
        prompt = build_prompt(question)
        answers = [call_deepseek(prompt, t) for t in [0.3, 0.7, 1.0]]
        print(f"回答：{answers}\n{'-'*50}")
        print(f"Token用量: {requests.json()['usage']}")