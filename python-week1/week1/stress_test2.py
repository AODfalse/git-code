from locust import HttpUser, task, between, events
import json
import random
import time
from locust.exception import StopUser

# 配置 - 请根据实际情况修改
API_KEY = "048b542052a89f315fa7c6b74bd253f9"  # 与应用中的TMDB_API_KEY一致
TEST_USERS = [
    {"username": "user1", "password": "password123"},
    {"username": "user2", "password": "456password"}
]

# 测试查询示例
TEST_QUERIES = [
    "推荐科幻电影",
    "头号玩家影评",
    "最近有什么好看的浪漫电影",
    "王家卫导演最好的作品",
    "科幻电影评分7.0以上",
    "推荐喜剧电影",
    "评分8.5以上的剧情片",
    "泰坦尼克号的影评",
    "推荐最新的动作电影",
    "日本动画电影推荐"
]

# 记录测试结果
test_results = {
    "login_success_count": 0,
    "login_failure_count": 0,
    "predict_success_count": 0,
    "predict_failure_count": 0,
    "login_response_times": [],
    "predict_response_times": [],
    "errors": {}  # 记录错误详情
}

def record_error(error_msg):
    """记录错误信息"""
    if error_msg in test_results["errors"]:
        test_results["errors"][error_msg] += 1
    else:
        test_results["errors"][error_msg] = 1

class MovieAppUser(HttpUser):
    wait_time = between(1, 3)  # 用户操作间隔时间
    token = None
    # 初始化请求头，包含API密钥
    headers = {
        "Content-Type": "application/json",
        "TMDB_API_KEY": API_KEY
    }

    def on_start(self):
        """用户启动时执行登录"""
        self.login()

    def login(self):
        """登录到应用"""
        # 随机选择一个测试用户
        user = random.choice(TEST_USERS)
        
        start_time = time.time()
        try:
            response = self.client.post(
                "/api/login",
                data=json.dumps(user),
                headers=self.headers
            )
            
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            test_results["login_response_times"].append(response_time)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result["status"] == "success":
                        self.token = result["token"]
                        # 添加认证令牌到请求头
                        self.headers["Authorization"] = f"Bearer {self.token}"
                        test_results["login_success_count"] += 1
                    else:
                        test_results["login_failure_count"] += 1
                        record_error(f"登录失败: {result.get('message', '未知错误')}")
                except json.JSONDecodeError:
                    test_results["login_failure_count"] += 1
                    record_error("登录响应不是有效的JSON")
            else:
                test_results["login_failure_count"] += 1
                record_error(f"登录状态码错误: {response.status_code}")
        except Exception as e:
            test_results["login_failure_count"] += 1
            error_msg = f"登录错误: {str(e)}"
            record_error(error_msg)
            print(error_msg)

    @task(3)  # 权重为3，执行频率更高
    def test_predict(self):
        """测试电影推荐接口"""
        if not self.token:
            # 如果未登录成功，尝试重新登录
            self.login()
            if not self.token:
                # 仍然登录失败，停止该用户
                raise StopUser()

        # 随机选择一个测试查询
        query = random.choice(TEST_QUERIES)
        data = {
            "data": [query],
            "user_token": self.token,
            "page": 1,
            "lang": random.choice(["zh", "en", "ja"])
        }
        
        start_time = time.time()
        try:
            response = self.client.post(
                "/api/predict",
                data=json.dumps(data),
                headers=self.headers
            )
            
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            test_results["predict_response_times"].append(response_time)
            
            if response.status_code == 200:
                test_results["predict_success_count"] += 1
            else:
                test_results["predict_failure_count"] += 1
                record_error(f"查询状态码错误: {response.status_code}")
        except Exception as e:
            test_results["predict_failure_count"] += 1
            error_msg = f"查询错误: {str(e)}"
            record_error(error_msg)
            print(error_msg)

    @task(1)  # 权重为1，执行频率较低
    def test_login_again(self):
        """测试重复登录"""
        # 保存当前token以便恢复
        current_token = self.token
        # 临时移除Authorization头
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
        # 执行登录
        self.login()
        # 如果登录失败，恢复之前的token
        if not self.token and current_token:
            self.token = current_token
            self.headers["Authorization"] = f"Bearer {self.token}"

@events.test_stop.add_listener
def print_test_summary(environment, **kwargs):
    """测试结束时打印总结报告"""
    print("\n===== 压力测试总结 =====")
    print(f"登录总次数: {test_results['login_success_count'] + test_results['login_failure_count']}")
    print(f"登录成功次数: {test_results['login_success_count']}")
    print(f"登录失败次数: {test_results['login_failure_count']}")
    
    if test_results['login_response_times']:
        avg_login_time = sum(test_results['login_response_times']) / len(test_results['login_response_times'])
        print(f"平均登录响应时间: {avg_login_time:.2f} ms")
        print(f"最大登录响应时间: {max(test_results['login_response_times']):.2f} ms")
        print(f"最小登录响应时间: {min(test_results['login_response_times']):.2f} ms")
    
    print("\n查询总次数: {predict_success_count} + {predict_failure_count}".format(** test_results))
    print(f"查询成功次数: {test_results['predict_success_count']}")
    print(f"查询失败次数: {test_results['predict_failure_count']}")
    
    if test_results['predict_response_times']:
        avg_predict_time = sum(test_results['predict_response_times']) / len(test_results['predict_response_times'])
        print(f"平均查询响应时间: {avg_predict_time:.2f} ms")
        print(f"最大查询响应时间: {max(test_results['predict_response_times']):.2f} ms")
        print(f"最小查询响应时间: {min(test_results['predict_response_times']):.2f} ms")
    
    # 打印错误详情
    if test_results["errors"]:
        print("\n错误详情:")
        for error, count in test_results["errors"].items():
            print(f"- {error}: {count}次")
    
    print("===========================")
    