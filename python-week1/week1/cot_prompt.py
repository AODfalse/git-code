import os
from dotenv import load_dotenv
import requests
import json
import re

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
            data=json.dumps(payload))
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return None

def validate_recommendation(movie: dict, criteria: dict) -> bool:
    """检查推荐是否满足条件"""
    if "genre" in criteria and criteria["genre"] not in movie["genres"]:
        return False

    if "director" in criteria and criteria["director"] != movie["director"]:
        return False

    if "year" in criteria and criteria["year"] != movie["year"]:
        return False

    return True


def build_cot_prompt(question: str) -> str:
    """构建带CoT推理链的Prompt"""
    return f"""
你是一位严谨的影评人，请按步骤思考后回答。
当前可推荐电影库：
- 《奥本海默》（传记/历史，诺兰导演，2023）
- 《流浪地球2》（科幻/灾难，郭帆导演，2023）
- 《热辣滚烫》（喜剧/励志，贾玲导演，2024）
---
用户问题：{question}
---
推理步骤：
1. 需求解析：明确用户核心需求
   - 检查：是否涉及类型/导演/年份等条件？
2. 电影筛选：根据需求匹配候选
   - 验证：类型/导演/年份是否匹配？
3. 合理性过滤：排除明显不合理项
   - 检查：是否有年龄限制/文化冲突？
4. 生成推荐：按格式输出结果

---
最终输出要求：
```json
{{
  "recommendations": [
    {{
      "title": "电影名",
      "director": "导演",
      "reason": "推荐理由（不超过20字）"
    }}
  ],
  "reasoning": "完整的推理过程" 
}}
"""

# 测试用例
test_cases = [
    "推荐诺兰导演的科幻电影",  # 测试类型与导演冲突
    "适合中学生观看的励志片",
    "2015年之前的高分华语电影"  # 测试无匹配项
]

# 电影数据库
movie = [
    {"title": "奥本海默", "genres": ["传记", "历史"], "director": "诺兰", "year": 2023},
    {"title": "流浪地球2", "genres": ["科幻", "灾难"], "director": "郭帆", "year": 2023},
    {"title": "热辣滚烫", "genres": ["喜剧", "励志"], "director": "贾玲", "year": 2024}
]

# 电影数据库
criteria = [
    { "genres": ["传记", "历史"]},
    { "genres": ["科幻", "灾难"]},
    { "genres": ["喜剧", "励志"]}
]

for question in test_cases:
    print(f"\n{'='*50}\n问题：{question}")
    prompt = build_cot_prompt(question)
    validate = validate_recommendation(movie, criteria)
    # 调用API获取响应
    response = call_deepseek(prompt)
    if not response:
        continue
        
    print(f"\n原始响应：\n{response}")
    
    # 提取JSON部分
    json_match = re.search(r'```json\n({.*?})\n```', response, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group(1))
            print("\n解析结果：")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
    
    # 提取推理步骤
    steps = re.findall(r"\d+\..+?(?=\n\d+\.|\Z)", response, re.DOTALL)
    print("\n推理步骤：")
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step.strip()}")