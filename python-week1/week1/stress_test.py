# stress_test.py (修正版)
from locust import HttpUser, task, between
import random
import json

class MovieBotUser(HttpUser):
    wait_time = between(1, 3)
    
    queries = [
        "推荐科幻电影",
        "头号玩家影评",
        "最近有什么好看的浪漫电影",
        "推荐喜剧电影",
        "盗梦空间评价",
        "泰坦尼克号影评",
        "阿凡达怎么样",
        "推荐剧情片"
    ]
    
    @task
    def ask_movie_recommendation(self):
        query = random.choice(self.queries)
        
        # 使用Gradio期望的JSON格式
        payload = {
            "data": [query],
            "fn_index": 0,
            "session_hash": "test_session"
        }
        
        self.client.post(
            "/api/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )