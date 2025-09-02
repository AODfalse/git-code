from locust import HttpUser, task, between, events
from locust.exception import StopUser
import json
import random
import time
from faker import Faker

# 初始化Faker用于生成模拟数据
fake = Faker('zh_CN')

# 测试用的查询语句列表
TEST_QUERIES = [
    "推荐科幻电影",
    "头号玩家影评",
    "最近有什么好看的浪漫电影",
    "王家卫导演最好的作品",
    "推荐喜剧片",
    "豆瓣高分电影",
    "动作片推荐",
    "肖申克的救赎影评",
    "2023年最佳电影",
    "适合情侣看的电影"
]

# 有效的登录凭据（根据你的USER_DB）
VALID_CREDENTIALS = [
    {"username": "user1", "password": "password123"},
    {"username": "user2", "password": "456password"}
]

# 无效的登录凭据
INVALID_CREDENTIALS = [
    {"username": "invalid", "password": "wrong"},
    {"username": "user1", "password": "wrong"},
    {"username": "", "password": ""}
]

class MovieApiUser(HttpUser):
    wait_time = between(1, 3)  # 用户操作之间的等待时间
    token = None
    auth_header = None

    def on_start(self):
        """用户开始会话时的操作 - 尝试登录"""
        # 随机选择登录方式：有效登录、无效登录或不登录
        login_choice = random.choices(
            ["valid", "invalid", "none"],
            weights=[0.6, 0.2, 0.2],
            k=1
        )[0]

        if login_choice == "valid":
            # 使用有效凭据登录
            creds = random.choice(VALID_CREDENTIALS)
            self.login(creds["username"], creds["password"])
        elif login_choice == "invalid":
            # 使用无效凭据登录
            creds = random.choice(INVALID_CREDENTIALS)
            self.login(creds["username"], creds["password"], expect_success=False)

    def login(self, username, password, expect_success=True):
        """登录方法"""
        with self.client.post(
            "/api/login",
            json={"username": username, "password": password},
            catch_response=True,
            name="/api/login"
        ) as response:
            try:
                result = json.loads(response.text)
                if expect_success:
                    if response.status_code == 200 and result.get("status") == "success":
                        self.token = result.get("token")
                        self.auth_header = {"X-API-Key": "your_secure_api_key"}
                        response.success()
                    else:
                        response.failure(f"登录失败: {response.text}")
                else:
                    if response.status_code == 200 and result.get("status") == "error":
                        response.success()  # 预期失败，所以标记为成功
                    else:
                        response.failure(f"预期登录失败但结果不符: {response.text}")
            except Exception as e:
                response.failure(f"登录处理错误: {str(e)}")

    @task(5)  # 权重5，比其他任务更频繁执行
    def test_predict_endpoint(self):
        """测试预测API端点"""
        # 随机选择一个查询
        query = random.choice(TEST_QUERIES)
        
        # 随机选择语言
        lang = random.choice(["zh", "en", "ja"])
        
        # 随机选择页码
        page = random.randint(1, 3)
        
        # 构建请求数据
        data = {
            "data": [query],
            "page": page,
            "lang": lang
        }
        
        # 如果已登录，添加用户token
        if self.token:
            data["user_token"] = self.token
        
        # 发送请求
        with self.client.post(
            "/api/predict",
            json=data,
            headers=self.auth_header,
            catch_response=True,
            name="/api/predict"
        ) as response:
            try:
                if response.status_code == 200:
                    result = json.loads(response.text)
                    if "data" in result:
                        response.success()
                    else:
                        response.failure("响应不包含数据字段")
                elif response.status_code == 403:
                    response.failure("认证失败")
                else:
                    response.failure(f"状态码错误: {response.status_code}")
            except Exception as e:
                response.failure(f"处理响应时出错: {str(e)}")

    @task(1)
    def test_login_workflow(self):
        """单独测试登录流程"""
        # 随机选择有效或无效凭据
        if random.random() < 0.7:  # 70%概率使用有效凭据
            creds = random.choice(VALID_CREDENTIALS)
            self.login(creds["username"], creds["password"])
        else:
            creds = random.choice(INVALID_CREDENTIALS)
            self.login(creds["username"], creds["password"], expect_success=False)

    @task(2)
    def test_multiple_queries(self):
        """模拟连续多次查询"""
        # 连续进行2-4次查询
        for _ in range(random.randint(2, 4)):
            self.test_predict_endpoint()
            time.sleep(random.uniform(0.5, 1.5))  # 模拟用户阅读时间

    def on_stop(self):
        """用户会话结束时的操作"""
        pass

if __name__ == "__main__":
    import os
    os.system("locust -f movie_api_stress_test.py")
