from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain_core.language_models.llms import BaseLLM
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv
import os
import json
import warnings

# 忽略LangChain的弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

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
                data=json.dumps(payload)
            )
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

def get_director_id(director_name: str) -> int:
    """获取导演ID"""
    url = f"https://api.themoviedb.org/3/search/person?query={director_name}&api_key={os.getenv('TMDB_API_KEY')}"
    response = requests.get(url).json()
    if response["results"]:
        return response["results"][0]["id"]
    return 0

def tmdb_search(query: str) -> str:
    """搜索指定导演的电影"""
    try:
        # 提取导演姓名（中文或英文）
        director = "Christopher Nolan" if "诺兰" in query else query.split("导演")[0].strip()
        
        # 获取导演ID
        director_id = get_director_id(director)
        if not director_id:
            return f"找不到导演{director}的信息"
        
        # 获取该导演的电影
        url = f"https://api.themoviedb.org/3/person/{director_id}/movie_credits?api_key={os.getenv('TMDB_API_KEY')}"
        response = requests.get(url).json()
        
        # 筛选导演作品并按日期排序
        directed_movies = [
            m for m in response["crew"] 
            if m.get("job") == "Director"
        ]
        sorted_movies = sorted(
            directed_movies,
            key=lambda x: x.get("release_date", ""),
            reverse=True
        )
        
        # 格式化结果
        return str([{
            "title": m["title"],
            "release_date": m.get("release_date", "未知日期"),
            "overview": m.get("overview", "暂无简介")[:50] + "..."
        } for m in sorted_movies[:3]])
        
    except Exception as e:
        return f"搜索失败: {str(e)}"

# 创建工具
tools = [
    Tool(
        name="TMDB_Search",
        func=tmdb_search,
        description="用于搜索导演的电影作品。输入包含导演姓名的查询，返回电影列表。"
    )
]

# 初始化DeepSeek LLM
llm = DeepSeekLLM(temperature=0)

# 创建代理
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

def main():
    print("电影信息查询系统（输入q退出）")
    print("示例问题：诺兰最新导演的电影是什么？\n李安导演的经典作品有哪些？")
    
    while True:
        try:
            query = input("\n请输入您的问题：").strip()
            if query.lower() in ["q", "quit", "exit"]:
                break
                
            if not query:
                print("问题不能为空")
                continue
                
            print(f"\n正在查询: {query}")
            result = agent.invoke({"input": query})
            print("\n查询结果:")
            print(result["output"])
            
        except KeyboardInterrupt:
            print("\n已中断查询")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()