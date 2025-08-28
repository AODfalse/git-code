import os
import time
import random
import tiktoken
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

class MovieBotV1:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.total_tokens = 0
        self.interaction_count = 0
        self.session_start = datetime.now()
    
    def calculate_tokens(self, text: str) -> int:
        """计算文本的Token数量"""
        return len(self.encoder.encode(text))
    
    def safe_response(self, response: str, confidence: float = 0.8) -> str:
        """添加安全边界，防止幻觉"""
        if confidence < 0.7:
            phrases = ["据我所知", "根据我的理解", "基于现有资料"]
            return f"{random.choice(phrases)}，{response}"
        elif confidence < 0.5:
            return f"信息可能不准确，请谨慎参考：{response}"
        else:
            return response
    
    def stream_response(self, prompt: str):
        """流式输出响应"""
        self.interaction_count += 1
        print("思考中", end="", flush=True)
        
        # 模拟思考过程
        for _ in range(3):
            time.sleep(0.5)
            print(".", end="", flush=True)
        
        print("\n")  # 思考结束，开始输出
        
        # 生成响应
        response = self.generate_response(prompt)
        safe_response = self.safe_response(response, confidence=0.8)
        
        # 流式输出
        token_count = 0
        for char in safe_response:
            print(char, end='', flush=True)
            token_count += self.calculate_tokens(char)
            time.sleep(0.03)  # 控制输出速度
        
        # 更新Token计数
        self.total_tokens += token_count
        
        print(f"\n\n本次消耗Token: {token_count}")
        return safe_response
    
    def generate_response(self, prompt: str) -> str:
        """根据提示生成响应"""
        # 知识库 - 实际应用中应使用更复杂的检索系统
        knowledge_base = {
            "浪漫电影": [
                "《恋恋笔记本》- 经典爱情故事，评分8.5",
                "《爱在黎明破晓前》- 邂逅与对话的浪漫，评分8.8",
                "《时空恋旅人》- 温馨幽默的英式爱情，评分8.7"
            ],
            "科幻电影": [
                "《沙丘2》- 史诗级科幻续作，评分8.8",
                "《降临》- 关于语言与时间的深刻思考，评分7.9",
                "《银翼杀手2049》- 视觉与哲学的盛宴，评分8.3"
            ],
            "喜剧电影": [
                "《白日梦想家》- 冒险与梦想的喜剧，评分8.5",
                "《三傻大闹宝莱坞》- 教育与人生的喜剧，评分9.2",
                "《功夫》- 周星驰经典无厘头喜剧，评分8.7"
            ]
        }
        
        # 简单关键词匹配
        for category, movies in knowledge_base.items():
            if category in prompt:
                return "\n".join(movies)
        
        return "抱歉，我暂时没有这方面的信息。您可以尝试询问特定类型的电影推荐。"
    
    def get_usage_report(self):
        """生成使用情况报告"""
        cost_per_1k = 0.002  # 假设每1000Token成本$0.002
        total_cost = (self.total_tokens / 1000) * cost_per_1k
        session_duration = datetime.now() - self.session_start
        
        return (
            f"\n===== 使用情况报告 =====\n"
            f"会话开始时间: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"会话持续时间: {session_duration}\n"
            f"交互次数: {self.interaction_count}\n"
            f"总Token消耗: {self.total_tokens}\n"
            f"估算成本: ${total_cost:.4f}\n"
            f"平均每次交互: {self.total_tokens/max(1, self.interaction_count):.1f} Token\n"
            f"========================="
        )

def main():
    bot = MovieBotV1()
    print("电影推荐机器人 v1.0 (已启用流式输出和Token监控)")
    print("输入'退出'或'quit'结束对话\n")
    
    while True:
        try:
            user_input = input("您: ").strip()
            
            if user_input.lower() in ['退出', 'quit', 'exit']:
                print(bot.get_usage_report())
                break
                
            if not user_input:
                continue
                
            print("AI: ", end="", flush=True)
            bot.stream_response(user_input)
            print()  # 空行分隔
            
        except KeyboardInterrupt:
            print("\n\n会话已中断")
            print(bot.get_usage_report())
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main()