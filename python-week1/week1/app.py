# app.py
import gradio as gr
import tiktoken
import time
import random
from datetime import datetime
from urllib.parse import quote

class MovieRecommender:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.total_tokens = 0
        self.interaction_count = 0
        
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
    
    def generate_response(self, prompt: str) -> str:
        """根据提示生成响应"""
        # 增加延迟模拟真实API调用
        time.sleep(0.5)
        
        # 检查是否询问特定电影的影评
        for movie_title, movie_info in self.movie_database.items():
            if movie_title in prompt:
                response = (
                    f"《{movie_title}》评分: {movie_info['rating']} ({movie_info['genre']}类型)\n\n"
                    f"{self.get_review_sources(movie_title, movie_info['id'])}"
                )
                token_count = self.calculate_tokens(response)
                self.total_tokens += token_count
                self.interaction_count += 1
                return response
        
        # 检查是否询问类型推荐
        genre_keywords = {
            "浪漫": ["浪漫", "爱情", "情侣", "恋爱"],
            "科幻": ["科幻", "未来", "太空", "外星", "科技"],
            "喜剧": ["喜剧", "搞笑", "幽默", "笑", "欢乐"],
            "剧情": ["剧情", "故事", "人生", "人性"]
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
                    response += f"《{title}》- 评分{info['rating']}\n"
                response += "\n"
            
            response += "您可以询问具体电影的影评资源，例如：\"头号玩家影评\""
            token_count = self.calculate_tokens(response)
            self.total_tokens += token_count
            self.interaction_count += 1
            return response
        
        # 默认回复
        response = (
            "抱歉，我暂时没有这方面的信息。\n\n"
            "您可以尝试：\n"
            "1. 询问特定类型电影推荐（如：浪漫电影、科幻电影）\n"
            "2. 询问具体电影的影评（如：头号玩家影评）\n"
            "3. 询问电影资讯（如：最近有什么好看的电影）"
        )
        token_count = self.calculate_tokens(response)
        self.total_tokens += token_count
        self.interaction_count += 1
        return response
    
    def get_stats(self):
        """获取使用统计"""
        return f"交互次数: {self.interaction_count} | Token消耗: {self.total_tokens}"

# 创建推荐器实例
recommender = MovieRecommender()

def recommend_movie(query):
    """处理电影推荐请求"""
    if not query.strip():
        return "请输入您的问题"
    
    return recommender.generate_response(query)

def get_usage_stats():
    """获取使用统计"""
    return recommender.get_stats()

# 创建Gradio界面
with gr.Blocks(title="AI电影顾问", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎬 AI电影推荐与影评系统")
    gr.Markdown("输入您想了解的电影或类型，获取推荐和影评资源")
    
    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                label="请输入您的问题",
                placeholder="例如：推荐科幻电影 或 头号玩家影评",
                lines=2
            )
            submit_btn = gr.Button("提交查询", variant="primary")
            
            examples = gr.Examples(
                examples=[
                    ["推荐科幻电影"],
                    ["头号玩家影评"],
                    ["最近有什么好看的浪漫电影"],
                    ["王家卫导演最好的作品"]
                ],
                inputs=query_input
            )
        
        with gr.Column(scale=2):
            output = gr.Textbox(label="推荐结果", lines=10, interactive=False)
            stats = gr.Textbox(label="系统统计", value=get_usage_stats, every=5)
    
    submit_btn.click(
        fn=recommend_movie,
        inputs=query_input,
        outputs=output
    )
    
    query_input.submit(
        fn=recommend_movie,
        inputs=query_input,
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=True)