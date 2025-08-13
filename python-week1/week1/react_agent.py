from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain_core.language_models.llms import BaseLLM
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv
import os
import json
import warnings

# 忽略LangChain的弃用警告
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# 加载环境变量
load_dotenv("deepseek.env", encoding="utf-8")

class DeepSeekLLM(BaseLLM):
    """自定义DeepSeek LLM包装器"""
    
    temperature: float = 0.3
    max_tokens: int = 500
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        return self._generate([prompt], stop=stop, **kwargs).generations[0][0].text
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        headers = {
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt} for prompt in prompts],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload))
            response.raise_for_status()
            return self._create_llm_result(response.json())
        except Exception as e:
            raise ValueError(f"DeepSeek API调用失败: {str(e)}")
    
    def _create_llm_result(self, response: Dict) -> Any:
        from langchain.schema import LLMResult, Generation
        choices = response.get("choices", [])
        generations = []
        for choice in choices:
            text = choice["message"]["content"]
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": "deepseek-chat"}

# TMDB搜索工具
def tmdb_search(query: str) -> str:
    """搜索电影信息的工具函数"""
    url = f"https://api.themoviedb.org/3/search/movie?query={query}&api_key={os.getenv('TMDB_API_KEY')}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        movies = response.json().get("results", [])
        # 筛选导演是诺兰的电影
        nolan_movies = [
            m for m in movies 
            if any("Christopher Nolan" in crew.get("name", "") 
                  for crew in m.get("crew", []))
        ]
        return str([{
            "title": m["title"],
            "release_date": m.get("release_date", "未知"),
            "overview": m.get("overview", "无简介")[:100] + "..."
        } for m in sorted(
            nolan_movies[:3],
            key=lambda x: x.get("release_date", ""),
            reverse=True
        )])
    except Exception as e:
        return f"搜索失败: {str(e)}"

# 创建工具列表
tools = [
    Tool(
        name="TMDB_Search",
        func=tmdb_search,
        description="用于搜索电影信息。输入导演姓名或电影名称，返回包含标题、上映日期和简介的列表。"
    )
]

# 初始化DeepSeek LLM
llm = DeepSeekLLM(temperature=0)

# 创建并运行代理
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True  # 添加输出解析错误处理
)

# 执行查询
if __name__ == "__main__":
    try:
        query = "诺兰最新导演的电影是什么？"
        print(f"正在查询: {query}")
        # 使用新的invoke方法替代run
        result = agent.invoke({"input": query})
        print("\n最终结果:")
        print(result["output"])
    except Exception as e:
        print(f"执行出错: {str(e)}")