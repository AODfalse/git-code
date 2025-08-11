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

def build_fewshot_prompt():
    """构建带Few-shot示例的Prompt"""
    base_prompt = """
你是一位专业影评人，请根据示例风格回答问题。
当前可推荐电影：《奥本海默》《芭比》《流浪地球2》《封神第一部》《热辣滚烫》
---
"""
    
    few_shot_examples = """
示例对话（正例）：
用户：推荐科幻电影
AI：建议考虑：
1. 《流浪地球2》- 中国科幻里程碑（2023，豆瓣8.3）
2. 《沙丘》- 史诗级科幻巨制（2021，豆瓣7.7）
3. 《降临》- 烧脑外星文明题材（2016，豆瓣7.8）

用户：推荐喜剧片
AI：推荐选择：
1. 《热辣滚烫》- 励志喜剧（2024，豆瓣7.9）
2. 《芭比》- 荒诞幽默（2023，豆瓣8.1）
3. 《疯狂元素城》- 动画喜剧（2023，豆瓣7.3）

示例对话（反例）：
用户：我想看汤姆·克鲁斯的电影
AI：错误推荐：推荐《招魂》（非主演作品，恐怖片不适合）
正确推荐：
1. 《碟中谍7》- 动作巅峰（2023，豆瓣7.8）
2. 《壮志凌云2》- 空战经典（2022，豆瓣8.0）
"""
    
    return base_prompt + few_shot_examples + "\n用户问题：{question}"

# 测试用例
test_cases = [
    "推荐适合家庭观看的电影",
    "我想看诺兰导演的作品",
    "推荐恐怖片给10岁小孩"  # 测试负样本效果
]

for question in test_cases:
    prompt = build_fewshot_prompt().format(question=question)
    response = [call_deepseek(prompt, t) for t in [0.3, 0.7, 1.0]]  # 使用Day1的API调用函数
    print(f"问题：{question}\n回答：{response}\n")
    