import gradio as gr
import tiktoken
import time
import random
import asyncio
import re
from datetime import datetime, timedelta
from urllib.parse import quote, unquote
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
import uvicorn
import json
import hashlib
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Any
import httpx
from pydantic import BaseModel
import secrets
from contextlib import asynccontextmanager
import os

# 配置
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "048b542052a89f315fa7c6b74bd253f9")  # TMDB API密钥
CACHE_TTL = 3600  # 缓存过期时间（秒）
MAX_HISTORY_LENGTH = 50  # 最大历史记录长度
API_KEY = "your_secure_api_key"  # API访问密钥
SUPPORTED_LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "ja": "日本語"
}
DEFAULT_LANGUAGE = "zh"

# 多语言文本资源
LANG_RESOURCES = {
    "zh": {
        "app_title": "AI电影顾问",
        "welcome_message": "输入您想了解的电影或类型，获取推荐和影评资源",
        "input_placeholder": "例如：推荐科幻电影 或 头号玩家影评 或 科幻电影评分7.0以上",
        "submit_btn": "提交查询",
        "output_label": "推荐结果",
        "stats_label": "系统统计",
        "loading": "加载中...",
        "empty_query": "请输入您的问题",
        "no_info": "抱歉，我暂时没有这方面的信息。",
        "no_movies_matching_criteria": "抱歉，没有找到符合条件的电影。",
        "try_options": "您可以尝试：\n1. 询问特定类型电影推荐（如：浪漫电影、科幻电影）\n2. 询问具体电影的影评（如：头号玩家影评）\n3. 询问电影资讯（如：最近有什么好看的电影）\n4. 指定评分条件（如：科幻电影评分7.0以上）",
        "favorites": "我的收藏",
        "share": "分享",
        "history": "对话历史",
        "load_more": "加载更多",
        "login": "登录",
        "logout": "退出",
        "language": "语言",
        "movie_info": "《{title}》评分: {rating} ({genre}类型)",
        "review_sources": "关于《{title}》的影评资源：",
        "recommendation": "为您推荐以下电影：",
        "genre_movies": "{genre}电影：",
        "please_login": "请先登录以使用此功能",
        "login_success": "登录成功",
        "invalid_credentials": "无效的凭据",
        "page": "页",
        "rating_filter": "评分{min_rating}以上"
    },
    "en": {
        "app_title": "AI Movie Advisor",
        "welcome_message": "Enter movies or genres you're interested in to get recommendations and review resources",
        "input_placeholder": "e.g.: Recommend sci-fi movies or Ready Player One reviews or sci-fi movies with rating above 7.0",
        "submit_btn": "Submit Query",
        "output_label": "Recommendation Results",
        "stats_label": "System Statistics",
        "loading": "Loading...",
        "empty_query": "Please enter your question",
        "no_info": "Sorry, I don't have information about that.",
        "no_movies_matching_criteria": "Sorry, no movies found matching your criteria.",
        "try_options": "You can try:\n1. Ask for movie recommendations by genre (e.g.: romantic movies, sci-fi movies)\n2. Ask for reviews of specific movies (e.g.: Ready Player One reviews)\n3. Ask for movie information (e.g.: What are good recent movies)\n4. Specify rating criteria (e.g.: sci-fi movies with rating above 7.0)",
        "favorites": "My Favorites",
        "share": "Share",
        "history": "Conversation History",
        "load_more": "Load More",
        "login": "Login",
        "logout": "Logout",
        "language": "Language",
        "movie_info": "{title} Rating: {rating} ({genre})",
        "review_sources": "Review resources for {title}:",
        "recommendation": "Recommended movies for you:",
        "genre_movies": "{genre} movies:",
        "please_login": "Please login to use this feature",
        "login_success": "Login successful",
        "invalid_credentials": "Invalid credentials",
        "page": "Page",
        "rating_filter": "with rating above {min_rating}"
    },
    "ja": {
        "app_title": "AI映画アドバイザー",
        "welcome_message": "興味のある映画やジャンルを入力して、推薦とレビュー情報を取得してください",
        "input_placeholder": "例：SF映画を推薦して または レディプレイヤーワンのレビュー または SF映画で評価7.0以上",
        "submit_btn": "クエリを送信",
        "output_label": "推薦結果",
        "stats_label": "システム統計",
        "loading": "読み込み中...",
        "empty_query": "質問を入力してください",
        "no_info": "申し訳ありませんが、その情報は現在提供できません。",
        "no_movies_matching_criteria": "申し訳ありませんが、条件に合う映画が見つかりませんでした。",
        "try_options": "次のように試してみることができます：\n1. 特定のジャンルの映画推薦を求める（例：恋愛映画、SF映画）\n2. 特定の映画のレビューを求める（例：レディプレイヤーワンのレビュー）\n3. 映画情報を求める（例：最近見るべき映画は何ですか）\n4. 評価条件を指定する（例：SF映画で評価7.0以上）",
        "favorites": "お気に入り",
        "share": "共有",
        "history": "会話履歴",
        "load_more": "さらに読み込む",
        "login": "ログイン",
        "logout": "ログアウト",
        "language": "言語",
        "movie_info": "『{title}』評価: {rating}（{genre}）",
        "review_sources": "{title}のレビュー情報：",
        "recommendation": "推薦映画：",
        "genre_movies": "{genre}映画：",
        "please_login": "この機能を使用するにはログインしてください",
        "login_success": "ログイン成功",
        "invalid_credentials": "無効な認証情報",
        "page": "ページ",
        "rating_filter": "評価{min_rating}以上"
    }
}

# 模拟用户数据库
USER_DB = {
    "user1": {"password": hashlib.sha256("password123".encode()).hexdigest(), "preferences": ["科幻", "剧情"]},
    "user2": {"password": hashlib.sha256("456password".encode()).hexdigest(), "preferences": ["浪漫", "喜剧"]}
}

# 用户会话管理
user_sessions = {}

# 电影数据库（包含TMDB ID）
movie_database = {
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

# 缓存实现
class Cache:
    def __init__(self):
        self.cache = {}
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self.cache:
            data, expiry = self.cache[key]
            if datetime.now() < expiry:
                return data
            # 缓存过期，移除
            del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> None:
        """设置缓存数据"""
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
        
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()

# 创建缓存实例
cache = Cache()

# 用户认证
class User:
    def __init__(self, username: str, preferences: List[str]):
        self.username = username
        self.preferences = preferences
        self.favorites = []
        self.history = []
        
    def add_favorite(self, movie_title: str) -> bool:
        """添加电影到收藏"""
        if movie_title in movie_database and movie_title not in self.favorites:
            self.favorites.append(movie_title)
            return True
        return False
        
    def remove_favorite(self, movie_title: str) -> bool:
        """从收藏中移除电影"""
        if movie_title in self.favorites:
            self.favorites.remove(movie_title)
            return True
        return False
        
    def add_history(self, query: str, response: str) -> None:
        """添加对话到历史记录"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response
        })
        # 限制历史记录长度
        if len(self.history) > MAX_HISTORY_LENGTH:
            self.history = self.history[-MAX_HISTORY_LENGTH:]

# 创建FastAPI应用
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    app.state.cache = cache
    app.state.movie_database = movie_database
    yield
    # 关闭时清理
    pass

app = FastAPI(title="Movie Recommendation API", lifespan=lifespan)
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "048b542052a89f315fa7c6b74bd253f9")
# API密钥验证
api_key_header = APIKeyHeader(name="TMDB_API_KEY", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == TMDB_API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

# 数据模型
class QueryRequest(BaseModel):
    data: List[str]
    user_token: Optional[str] = None
    page: int = 1
    lang: str = DEFAULT_LANGUAGE

class LoginRequest(BaseModel):
    username: str
    password: str

class MovieRecommender:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.total_tokens = 0
        self.interaction_count = 0
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        
    def calculate_tokens(self, text: str) -> int:
        """计算文本的Token数量"""
        return len(self.encoder.encode(text))
    
    def get_lang_text(self, key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
        """获取多语言文本"""
        lang = lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        try:
            text = LANG_RESOURCES[lang][key]
            if kwargs:
                return text.format(** kwargs)
            return text
        except KeyError:
            #  fallback to default language if key not found
            return LANG_RESOURCES[DEFAULT_LANGUAGE][key].format(**kwargs)
    
    def safe_response(self, response: str, confidence: float = 0.8) -> str:
        """添加安全边界，防止幻觉"""
        if confidence < 0.7:
            phrases = ["据我所知", "根据我的理解", "基于现有资料"]
            return f"{random.choice(phrases)}，{response}"
        elif confidence < 0.5:
            return f"信息可能不准确，请谨慎参考：{response}"
        else:
            return response
    
    def extract_rating_filter(self, prompt: str) -> Optional[float]:
        """从用户查询中提取评分筛选条件"""
        # 匹配中文表达（如：评分7.0以上、评分大于7、7分以上）
        chinese_patterns = [
            r'评分(\d+(?:\.\d+)?)以上',
            r'评分大于(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)分以上'
        ]
        
        # 匹配英文表达（如：rating above 7.0, rating > 7, 7+ rating）
        english_patterns = [
            r'rating above (\d+(?:\.\d+)?)',
            r'rating > (\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\+ rating'
        ]
        
        # 匹配日文表达（如：評価7.0以上、7点以上）
        japanese_patterns = [
            r'評価(\d+(?:\.\d+)?)以上',
            r'(\d+(?:\.\d+)?)点以上'
        ]
        
        # 尝试所有模式
        for pattern in chinese_patterns + english_patterns + japanese_patterns:
            match = re.search(pattern, prompt)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
                    
        return None
    
    @lru_cache(maxsize=100)
    def get_review_sources(self, movie_title: str, movie_id: int, lang: str = DEFAULT_LANGUAGE) -> str:
        """生成影评资源链接"""
        encoded_title = quote(movie_title)
        sources = [
            f"1. 豆瓣电影：https://movie.douban.com/subject/{movie_id}/",
            f"2. 知乎讨论：https://www.zhihu.com/search?q={encoded_title}+影评",
            f"3. 烂番茄：https://www.rottentomatoes.com/search?search={encoded_title}",
            "4. 专业媒体：可在《看电影》杂志或Variety网站搜索相关评论"
        ]
        
        if lang == "en":
            sources = [
                f"1. Douban: https://movie.douban.com/subject/{movie_id}/",
                f"2. Zhihu: https://www.zhihu.com/search?q={encoded_title}+reviews",
                f"3. Rotten Tomatoes: https://www.rottentomatoes.com/search?search={encoded_title}",
                "4. Professional media: Search reviews in 'Cinephilia' magazine or Variety website"
            ]
        elif lang == "ja":
            sources = [
                f"1. 豆瓣映画：https://movie.douban.com/subject/{movie_id}/",
                f"2. 知乎：https://www.zhihu.com/search?q={encoded_title}+レビュー",
                f"3. ロッテントマト：https://www.rottentomatoes.com/search?search={encoded_title}",
                "4. 専門媒体：「映画を見る」誌またはVarietyウェブサイトで検索できます"
            ]
            
        return f"{self.get_lang_text('review_sources', lang, title=movie_title)}\n" + "\n".join(sources)
    
    async def fetch_tmdb_data(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """从TMDB API获取数据"""
        if not TMDB_API_KEY:
            return None
            
        params = params or {}
        params["api_key"] = TMDB_API_KEY
        
        cache_key = f"tmdb_{endpoint}_{json.dumps(params, sort_keys=True)}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.tmdb_base_url}/{endpoint}", params=params)
                response.raise_for_status()
                data = response.json()
                cache.set(cache_key, data)
                return data
        except httpx.HTTPError as e:
            print(f"TMDB API error: {str(e)}")
            return None
        except Exception as e:
            print(f"Error fetching TMDB data: {str(e)}")
            return None
    
    async def get_movie_details(self, movie_id: int, lang: str = "zh-CN") -> Optional[Dict[str, Any]]:
        """获取电影详细信息"""
        return await self.fetch_tmdb_data(f"movie/{movie_id}", {"language": lang})
    
    async def search_movies(self, query: str, page: int = 1, lang: str = "zh-CN") -> Optional[Dict[str, Any]]:
        """搜索电影"""
        return await self.fetch_tmdb_data("search/movie", {
            "query": query,
            "page": page,
            "language": lang
        })
    
    async def get_similar_movies(self, movie_id: int, page: int = 1) -> Optional[Dict[str, Any]]:
        """获取相似电影"""
        return await self.fetch_tmdb_data(f"movie/{movie_id}/similar", {"page": page})
    
    async def get_popular_movies(self, genre: Optional[str] = None, page: int = 1, lang: str = "zh-CN") -> Optional[Dict[str, Any]]:
        """获取热门电影"""
        params = {"page": page, "language": lang}
        if genre:
            # TMDB的 genre ID映射
            genre_ids = {
                "动作": 28, "冒险": 12, "动画": 16, "喜剧": 35, "犯罪": 80,
                "纪录片": 99, "剧情": 18, "家庭": 10751, "奇幻": 14, "历史": 36,
                "恐怖": 27, "音乐": 10402, "悬疑": 9648, "浪漫": 10749, "科幻": 878,
                "惊悚": 53, "战争": 10752, "西部": 37
            }
            genre_id = genre_ids.get(genre)
            if genre_id:
                params["with_genres"] = genre_id
                
        return await self.fetch_tmdb_data("movie/popular", params)
    
    async def generate_response(self, prompt: str, user: Optional[User] = None, 
                               page: int = 1, lang: str = DEFAULT_LANGUAGE) -> Tuple[str, int, int]:
        """根据提示生成响应，返回(响应内容, 总页数, 当前页码)"""
        # 增加延迟模拟真实API调用
        await asyncio.sleep(0.3)
        
        # 检查是否询问特定电影的影评
        for movie_title, movie_info in movie_database.items():
            if movie_title in prompt:
                # 尝试从TMDB获取更多信息
                tmdb_lang = "zh-CN" if lang == "zh" else "en-US" if lang == "en" else "ja-JP"
                details = await self.get_movie_details(movie_info["id"], tmdb_lang)
                
                rating = details.get("vote_average", movie_info["rating"]) if details else movie_info["rating"]
                response = self.get_lang_text("movie_info", lang, 
                                            title=movie_title, 
                                            rating=rating, 
                                            genre=movie_info["genre"]) + "\n\n"
                
                response += self.get_review_sources(movie_title, movie_info["id"], lang)
                
                # 如果有TMDB数据，添加更多信息
                if details:
                    overview = details.get("overview", "")
                    if overview:
                        response += f"\n\n剧情简介: {overview}"
                
                token_count = self.calculate_tokens(response)
                self.total_tokens += token_count
                self.interaction_count += 1
                return (response, 1, 1)
        
        # 提取评分筛选条件
        min_rating = self.extract_rating_filter(prompt)
        
        # 检查是否询问类型推荐
        genre_keywords = {
            "浪漫": ["浪漫", "爱情", "情侣", "恋爱", "romance", "love", "恋愛", "ロマンス"],
            "科幻": ["科幻", "未来", "太空", "外星", "科技", "sci-fi", "science", "SF", "科学", "未来"],
            "喜剧": ["喜剧", "搞笑", "幽默", "笑", "欢乐", "comedy", "funny", "コメディ", "笑"],
            "剧情": ["剧情", "故事", "人生", "人性", "drama", "story", "ドラマ", "物語"]
        }
        
        matched_genres = []
        for genre, keywords in genre_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                matched_genres.append(genre)
        
        if matched_genres:
            # 每页显示5部电影
            items_per_page = 5
            response = self.get_lang_text("recommendation", lang) + "\n\n"
            
            # 尝试从TMDB获取流行电影
            tmdb_movies = None
            all_filtered_movies = []  # 存储所有符合条件的电影
            
            for genre in matched_genres:
                # 添加类型和可能的评分筛选条件说明
                genre_label = self.get_lang_text("genre_movies", lang, genre=genre)
                if min_rating:
                    rating_label = self.get_lang_text("rating_filter", lang, min_rating=min_rating)
                    response += f"{genre_label} {rating_label}\n"
                else:
                    response += f"{genre_label}\n"
                
                # 先尝试从TMDB获取
                tmdb_lang = "zh-CN" if lang == "zh" else "en-US" if lang == "en" else "ja-JP"
                tmdb_movies = await self.get_popular_movies(genre, page, tmdb_lang)
                
                if tmdb_movies and tmdb_movies.get("results"):
                    # 筛选出符合评分条件的电影
                    filtered_movies = []
                    for movie in tmdb_movies["results"]:
                        # TMDB评分是10分制
                        if min_rating is None or (movie.get("vote_average") and movie["vote_average"] >= min_rating):
                            filtered_movies.append(movie)
                    
                    # 保存所有筛选后的电影用于分页
                    all_filtered_movies.extend(filtered_movies)
                    
                    # 处理分页
                    start_idx = (page - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    paginated_movies = filtered_movies[start_idx:end_idx]
                    
                    # 计算总页数
                    total_pages = max(1, (len(filtered_movies) + items_per_page - 1) // items_per_page)
                    
                    # 添加电影到响应
                    for i, movie in enumerate(paginated_movies):
                        title = movie.get("title", movie.get("original_title", "未知电影"))
                        rating = movie.get("vote_average", "N/A")
                        # 格式化评分，保留一位小数
                        if isinstance(rating, float):
                            rating = f"{rating:.1f}"
                        response += f"{start_idx + i + 1}. 《{title}》- 评分{rating}\n"
                        
                    # 如果没有符合条件的电影
                    if not filtered_movies:
                        response += self.get_lang_text("no_movies_matching_criteria", lang) + "\n"
                else:
                    # TMDB获取失败，使用本地数据库
                    movies_in_genre = [
                        (title, info) for title, info in movie_database.items() 
                        if info["genre"] == genre
                    ]
                    
                    # 应用评分筛选
                    if min_rating is not None:
                        movies_in_genre = [
                            (title, info) for title, info in movies_in_genre
                            if info["rating"] >= min_rating
                        ]
                    
                    # 按评分排序
                    movies_in_genre.sort(key=lambda x: x[1]["rating"], reverse=True)
                    
                    # 分页处理
                    start_idx = (page - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    paginated_movies = movies_in_genre[start_idx:end_idx]
                    total_pages = max(1, (len(movies_in_genre) + items_per_page - 1) // items_per_page)
                    
                    # 添加电影到响应
                    for i, (title, info) in enumerate(paginated_movies):
                        response += f"{start_idx + i + 1}. 《{title}》- 评分{info['rating']}\n"
                        
                    # 如果没有符合条件的电影
                    if not movies_in_genre:
                        response += self.get_lang_text("no_movies_matching_criteria", lang) + "\n"
                
                response += "\n"
            
            response += self.get_lang_text("try_options", lang)
            
            # 添加分页信息
            if tmdb_movies and all_filtered_movies:
                total_pages = max(1, (len(all_filtered_movies) + items_per_page - 1) // items_per_page)
            elif not tmdb_movies:
                total_movies = sum(len([t for t, i in movie_database.items() if i["genre"] == g]) for g in matched_genres)
                total_pages = max(1, (total_movies + items_per_page - 1) // items_per_page)
            else:
                total_pages = 1
                
            if total_pages > 1:
                response += f"\n{self.get_lang_text('page', lang)} {page}/{total_pages} | {self.get_lang_text('load_more', lang)}"
            
            token_count = self.calculate_tokens(response)
            self.total_tokens += token_count
            self.interaction_count += 1
            return (response, total_pages, page)
        
        # 默认回复
        response = self.get_lang_text("no_info", lang) + "\n\n"
        response += self.get_lang_text("try_options", lang)
        
        token_count = self.calculate_tokens(response)
        self.total_tokens += token_count
        self.interaction_count += 1
        return (response, 1, 1)
    
    def get_stats(self) -> str:
        """获取使用统计"""
        return f"交互次数: {self.interaction_count} | Token消耗: {self.total_tokens}"

# 创建推荐器实例
recommender = MovieRecommender()

async def get_current_user(token: Optional[str]) -> Optional[User]:
    """获取当前登录用户"""
    if not token:
        return None
    return user_sessions.get(token)

async def recommend_movie(query: str, user_token: Optional[str] = None, 
                         page: int = 1, lang: str = DEFAULT_LANGUAGE) -> Tuple[str, int, int]:
    """处理电影推荐请求"""
    if not query.strip():
        return (recommender.get_lang_text("empty_query", lang), 1, 1)
    
    user = await get_current_user(user_token)
    response, total_pages, current_page = await recommender.generate_response(query, user, page, lang)
    
    # 如果用户已登录，添加到历史记录
    if user:
        user.add_history(query, response)
        
    return (response, total_pages, current_page)

async def user_login(username: str, password: str) -> Tuple[Optional[str], str]:
    """用户登录"""
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if username in USER_DB and USER_DB[username]["password"] == hashed_pw:
        # 生成会话令牌
        token = secrets.token_urlsafe(32)
        # 创建用户实例
        user = User(username, USER_DB[username]["preferences"])
        user_sessions[token] = user
        return (token, recommender.get_lang_text("login_success"))
    return (None, recommender.get_lang_text("invalid_credentials"))

async def add_favorite(movie_title: str, user_token: Optional[str]) -> str:
    """添加电影到收藏"""
    user = await get_current_user(user_token)
    if not user:
        return recommender.get_lang_text("please_login")
    
    if user.add_favorite(movie_title):
        return f"《{movie_title}》已添加到收藏"
    return f"添加失败，《{movie_title}》可能不存在或已在收藏中"

def generate_share_link(query: str) -> str:
    """生成分享链接"""
    encoded_query = quote(query)
    return f"http://localhost:7860/?q={encoded_query}"

# 创建Gradio界面
with gr.Blocks(title=recommender.get_lang_text("app_title"), theme=gr.themes.Soft()) as demo:
    # 状态变量
    user_token = gr.State(None)
    current_page = gr.State(1)
    total_pages = gr.State(1)
    current_lang = gr.State(DEFAULT_LANGUAGE)
    history_visible = gr.State(False)  # 新增状态变量跟踪历史记录可见性
    
    gr.Markdown(f"# 🎬 {recommender.get_lang_text('app_title')}")
    gr.Markdown(recommender.get_lang_text("welcome_message"))
    
    with gr.Row():
        # 登录/用户区域
        with gr.Column(scale=1):
            login_btn = gr.Button(recommender.get_lang_text("login"))
            logout_btn = gr.Button(recommender.get_lang_text("logout"), visible=False)
            username_input = gr.Textbox(label="用户名", visible=False)
            password_input = gr.Textbox(label="密码", type="password", visible=False)
            login_status = gr.Textbox(label="登录状态", visible=False)
            
            # 语言选择
            lang_select = gr.Dropdown(
                choices=list(SUPPORTED_LANGUAGES.values()),
                value=SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE],
                label=recommender.get_lang_text("language")
            )
            
            # 收藏列表
            favorites_list = gr.List(label=recommender.get_lang_text("favorites"))
        
        # 主内容区域
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                label=recommender.get_lang_text("input_placeholder"),
                placeholder=recommender.get_lang_text("input_placeholder"),
                lines=2
            )
            
            with gr.Row():
                submit_btn = gr.Button(recommender.get_lang_text("submit_btn"), variant="primary")
                share_btn = gr.Button(recommender.get_lang_text("share"))
                favorite_btn = gr.Button(recommender.get_lang_text("favorites"))
            
            # 分页控制
            with gr.Row(visible=False) as pagination_row:
                prev_btn = gr.Button("上一页")
                page_info = gr.Textbox(label="页码", interactive=False)
                next_btn = gr.Button("下一页")
            
            # 加载动画
            loading = gr.Textbox(recommender.get_lang_text("loading"), visible=False)
            output = gr.Textbox(label=recommender.get_lang_text("output_label"), lines=10, interactive=False)
            stats = gr.Textbox(label=recommender.get_lang_text("stats_label"), value=recommender.get_stats, every=5)
            
            # 历史记录
            history_btn = gr.Button(recommender.get_lang_text("history"))
            history_output = gr.Textbox(label=recommender.get_lang_text("history"), lines=10, interactive=False, visible=False)
            
            examples = gr.Examples(
                examples=[
                    ["推荐科幻电影"],
                    ["头号玩家影评"],
                    ["最近有什么好看的浪漫电影"],
                    ["王家卫导演最好的作品"],
                    ["科幻电影评分7.0以上"]  # 新增示例
                ],
                inputs=query_input
            )
    
    # 登录逻辑
    def toggle_login(visible):
        return {
            username_input: gr.update(visible=not visible),
            password_input: gr.update(visible=not visible),
            login_btn: gr.update(visible=visible),
            logout_btn: gr.update(visible=not visible)
        }
    
    login_btn.click(
        fn=lambda: toggle_login(True),
        outputs=[username_input, password_input, login_btn, logout_btn]
    )
    
    async def perform_login(username, password):
        token, message = await user_login(username, password)
        if token:
            return {
                user_token: token,
                login_status: message,
                username_input: gr.update(visible=False),
                password_input: gr.update(visible=False),
                login_btn: gr.update(visible=False),
                logout_btn: gr.update(visible=True)
            }
        return {login_status: message}
    
    username_input.submit(
        fn=perform_login,
        inputs=[username_input, password_input],
        outputs=[user_token, login_status, username_input, password_input, login_btn, logout_btn]
    )
    
    password_input.submit(
        fn=perform_login,
        inputs=[username_input, password_input],
        outputs=[user_token, login_status, username_input, password_input, login_btn, logout_btn]
    )
    
    logout_btn.click(
        fn=lambda: {
            user_token: None,
            username_input: gr.update(visible=False),
            password_input: gr.update(visible=False),
            login_btn: gr.update(visible=True),
            logout_btn: gr.update(visible=False),
            favorites_list: []
        },
        outputs=[user_token, username_input, password_input, login_btn, logout_btn, favorites_list]
    )
    
    # 语言切换
    def change_language(selected_lang):
        lang_code = next(k for k, v in SUPPORTED_LANGUAGES.items() if v == selected_lang)
        return {
            current_lang: lang_code,
            query_input: gr.update(
                label=recommender.get_lang_text("input_placeholder", lang_code),
                placeholder=recommender.get_lang_text("input_placeholder", lang_code)
            ),
            output: gr.update(label=recommender.get_lang_text("output_label", lang_code)),
            stats: gr.update(label=recommender.get_lang_text("stats_label", lang_code)),
            submit_btn: gr.update(value=recommender.get_lang_text("submit_btn", lang_code)),
            share_btn: gr.update(value=recommender.get_lang_text("share", lang_code)),
            favorite_btn: gr.update(value=recommender.get_lang_text("favorites", lang_code)),
            history_btn: gr.update(value=recommender.get_lang_text("history", lang_code)),
            history_output: gr.update(label=recommender.get_lang_text("history", lang_code)),
            lang_select: gr.update(label=recommender.get_lang_text("language", lang_code))
        }
    
    lang_select.change(
        fn=change_language,
        inputs=[lang_select],
        outputs=[
            current_lang, query_input, output, stats, submit_btn, 
            share_btn, favorite_btn, history_btn, history_output, lang_select
        ]
    )
    
    # 查询处理
    async def handle_query(query, token, page, lang):
        # 显示加载状态
        loading_visible = True
        output_visible = False
        
        # 执行查询
        result, total, current = await recommend_movie(query, token, page, lang)
        
        # 隐藏加载状态，显示结果
        loading_visible = False
        output_visible = True
        pagination_visible = total > 1
        page_info_text = f"{current}/{total}"
        
        return {
            loading: gr.update(value=recommender.get_lang_text("loading", lang), visible=loading_visible),
            output: gr.update(value=result, visible=output_visible),
            total_pages: total,
            current_page: current,
            pagination_row: gr.update(visible=pagination_visible),
            page_info: gr.update(value=page_info_text)
        }
    
    submit_btn.click(
        fn=lambda q, t, l: {loading: gr.update(visible=True), output: gr.update(visible=False)},
        inputs=[query_input, user_token, current_lang],
        outputs=[loading, output],
        queue=False
    ).then(
        fn=handle_query,
        inputs=[query_input, user_token, current_page, current_lang],
        outputs=[loading, output, total_pages, current_page, pagination_row, page_info]
    )
    
    query_input.submit(
        fn=lambda q, t, l: {loading: gr.update(visible=True), output: gr.update(visible=False)},
        inputs=[query_input, user_token, current_lang],
        outputs=[loading, output],
        queue=False
    ).then(
        fn=handle_query,
        inputs=[query_input, user_token, current_page, current_lang],
        outputs=[loading, output, total_pages, current_page, pagination_row, page_info]
    )
    
    # 分页控制
    async def change_page(token, query, current, total, direction, lang):
        if direction == "next" and current < total:
            new_page = current + 1
        elif direction == "prev" and current > 1:
            new_page = current - 1
        else:
            new_page = current
            
        result, total, current = await recommend_movie(query, token, new_page, lang)
        return {
            output: gr.update(value=result),
            current_page: new_page,
            page_info: gr.update(value=f"{new_page}/{total}")
        }
    
    next_btn.click(
        fn=change_page,
        inputs=[user_token, query_input, current_page, total_pages, gr.State("next"), current_lang],
        outputs=[output, current_page, page_info]
    )
    
    prev_btn.click(
        fn=change_page,
        inputs=[user_token, query_input, current_page, total_pages, gr.State("prev"), current_lang],
        outputs=[output, current_page, page_info]
    )
    
    # 收藏功能
    async def handle_favorite(query, token, lang):
        if not token:
            return recommender.get_lang_text("please_login", lang)
            
        user = await get_current_user(token)
        if not user:
            return recommender.get_lang_text("please_login", lang)
            
        # 尝试从输出中提取电影名称
        output_text = output.value
        if not output_text:
            return "没有可收藏的电影"
            
        # 提取所有电影标题
        movie_titles = [title for title in movie_database.keys() if title in output_text]
        
        if not movie_titles:
            return "未找到可收藏的电影"
            
        # 收藏第一个找到的电影
        success = user.add_favorite(movie_titles[0])
        if success:
            return f"《{movie_titles[0]}》已添加到收藏"
        return f"《{movie_titles[0]}》已在收藏中"
    
    favorite_btn.click(
        fn=handle_favorite,
        inputs=[query_input, user_token, current_lang],
        outputs=[output]
    )
    
    # 显示收藏
    async def show_favorites(token, lang):
        user = await get_current_user(token)
        if not user:
            return {
                favorites_list: [recommender.get_lang_text("please_login", lang)]
            }
        return {
            favorites_list: user.favorites if user.favorites else ["暂无收藏"]
        }
    
    favorite_btn.click(
        fn=show_favorites,
        inputs=[user_token, current_lang],
        outputs=[favorites_list]
    )
    
    # 分享功能
    def handle_share(query):
        if not query:
            return "请先输入查询内容"
        return generate_share_link(query)
    
    share_btn.click(
        fn=handle_share,
        inputs=[query_input],
        outputs=[output]
    )
    
    # 历史记录
    async def toggle_history(token, visible_state, lang):
        user = await get_current_user(token)
        new_visible = not visible_state
        
        if not user:
            return {
                history_output: gr.update(
                    value=recommender.get_lang_text("please_login", lang), 
                    visible=new_visible
                ),
                history_visible: new_visible
            }
            
        # 格式化历史记录
        history_text = "\n\n".join([
            f"[{h['timestamp'].split('T')[1][:8]}] 问: {h['query']}\n答: {h['response'][:100]}..." 
            for h in reversed(user.history)
        ])
        
        return {
            history_output: gr.update(
                value=history_text if user.history else "暂无历史记录", 
                visible=new_visible
            ),
            history_visible: new_visible
        }
    
    history_btn.click(
        fn=toggle_history,
        inputs=[user_token, history_visible, current_lang],
        outputs=[history_output, history_visible]
    )

# 添加API端点
@app.post("/api/predict", dependencies=[Depends(get_api_key)])
async def api_predict(request: QueryRequest):
    """专门的API端点，处理JSON请求"""
    try:
        # 提取查询内容
        query = request.data[0] if request.data and len(request.data) > 0 else ""
        
        # 处理查询
        response, total_pages, current_page = await recommend_movie(
            query, request.user_token, request.page, request.lang
        )
        
        return {
            "data": [response],
            "page": current_page,
            "total_pages": total_pages,
            "is_generating": False,
            "duration": 0.5,
            "average_duration": 0.5
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 登录API
@app.post("/api/login")
async def api_login(request: LoginRequest):
    """用户登录API"""
    try:
        token, message = await user_login(request.username, request.password)
        if token:
            return {
                "status": "success",
                "message": message,
                "token": token
            }
        return {
            "status": "error",
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 将Gradio应用挂载到FastAPI
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7860)
    