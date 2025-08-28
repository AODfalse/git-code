import os
import time
import random
import tiktoken
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import quote

# 加载环境变量
load_dotenv()

class MovieBotV1:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.total_tokens = 0
        self.interaction_count = 0
        self.session_start = datetime.now()
        
        # 电影数据库（包含TMDB ID）
        self.movie_database = {
            "恋恋笔记本": {"rating": 8.5, "genre": "浪漫", "id": 11036},
            "爱在黎明破晓前": {"rating": 8.8, "genre": "浪漫", "id": 76},
            "时空恋旅人": {"rating": 8.7, "genre": "浪漫", "id": 122906},
            "沙丘2": {"rating": 8.8, "genre": "科幻", "id": 693134},
            "降临": {"rating": 7.9, "genre": "科幻", "id": 329865},
            "银翼杀手2049": {"rating": 8.3, "genre": "科幻", "id": 335984},
            "白日梦想家": {"rating": 8.5, "genre": "喜剧", "id": 181533},
            "三傻大闹宝莱坞": {"rating": 9.2, "genre": "喜剧", "id": 20453},
            "功夫": {"rating": 8.7, "genre": "喜剧", "id": 14048},
            "头号玩家": {"rating": 8.7, "genre": "科幻", "id": 333339},
            "盗梦空间": {"rating": 9.0, "genre": "科幻", "id": 27205},
            "泰坦尼克号": {"rating": 9.4, "genre": "浪漫", "id": 597},
            "阿凡达": {"rating": 8.8, "genre": "科幻", "id": 19995},
            "肖申克的救赎": {"rating": 9.7, "genre": "剧情", "id": 278},
            "霸王别姬": {"rating": 9.6, "genre": "剧情", "id": 14282}
        }
    
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
    
    def get_review_sources(self, movie_title: str, movie_id: int) -> str:
        """生成影评资源链接"""
        encoded_title = quote(movie_title)
        return (
            f"关于《{movie_title}》的影评资源：\n"
            f"1. 豆瓣电影：https://movie.douban.com/subject/{movie_id}/\n"
            f"2. 知乎讨论：https://www.zhihu.com/search?q={encoded_title}+影评\n"
            f"3. 烂番茄：https://www.rottentomatoes.com/search?search={encoded_title}\n"
            f"4. 专业媒体：可在《看电影》杂志或Variety网站搜索相关评论"
        )
    
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
        # 检查是否询问特定电影的影评
        for movie_title, movie_info in self.movie_database.items():
            if movie_title in prompt:
                return (
                    f"《{movie_title}》评分: {movie_info['rating']} ({movie_info['genre']}类型)\n\n"
                    f"{self.get_review_sources(movie_title, movie_info['id'])}"
                )
        
        # 检查是否询问类型推荐
        genre_keywords = {
            "浪漫": ["浪漫", "爱情", "情侣", "恋爱"],
            "科幻": ["科幻", "未来", "太空", "外星", "科技"],
            "喜剧": ["喜剧", "搞笑", "幽默", "笑", "欢乐"]
        }
        
        matched_genres = []
        for genre, keywords in genre_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                matched_genres.append(genre)
        
        if matched_genres:
            response = "为您推荐以下电影：\n\n"
            for genre in matched_genres:
                response += f"{genre}电影：\n"
                movies_in_genre = [
                    (title, info) for title, info in self.movie_database.items() 
                    if info["genre"] == genre
                ]
                # 按评分排序
                movies_in_genre.sort(key=lambda x: x[1]["rating"], reverse=True)
                
                for title, info in movies_in_genre[:3]:  # 每种类型最多推荐3部
                    response += f"《{title}》- 评分{info['rating']} (ID: {info['id']})\n"
                response += "\n"
            
            response += "您可以询问具体电影的影评资源，例如：\"头号玩家影评\""
            return response
        
        # 默认回复
        return (
            "抱歉，我暂时没有这方面的信息。\n\n"
            "您可以尝试：\n"
            "1. 询问特定类型电影推荐（如：浪漫电影、科幻电影）\n"
            "2. 询问具体电影的影评（如：头号玩家影评）\n"
            "3. 询问电影资讯（如：最近有什么好看的电影）"
        )
    
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
    print("电影推荐与影评机器人 v1.0 (已启用流式输出和Token监控)")
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