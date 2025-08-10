import requests

response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={"Authorization": "Bearer sk-8e6cab5152e5434d840afa871153bf56"},
    json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "你好"}]
    }
)

data = response.json()

# DeepSeek的Token统计路径（与OpenAI不同）
if "usage" in data:
    print(f"Token用量: {data['usage']}")  # 完整用量统计
    print(f"输入Token: {data['usage']['prompt_tokens']}")
    print(f"输出Token: {data['usage']['completion_tokens']}")
else:
    print("当前API版本未返回用量统计，请检查文档")