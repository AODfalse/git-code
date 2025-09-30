# tool_calling_basic.py
import os
from dotenv import load_dotenv
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
import logging
from modelscope import snapshot_download
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 配置DeepSeek API
try:
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        openai_api_base="https://api.deepseek.com/v1"  # DeepSeek API端点
    )
    logger.info("DeepSeek LLM初始化成功")
except Exception as e:
    logger.warning(f"DeepSeek LLM初始化失败: {e}")
    llm = None

# 创建股票数据工具
def get_stock_price(symbol: str) -> str:
    """获取股票当前价格，输入股票代码"""
    # 模拟真实股票数据
    stock_data = {
        "AAPL": {"price": "178.72", "change": "+2.15", "change_percent": "+1.22%"},
        "MSFT": {"price": "337.69", "change": "+1.23", "change_percent": "+0.37%"},
        "TSLA": {"price": "209.98", "change": "-3.45", "change_percent": "-1.62%"},
        "NVDA": {"price": "950.02", "change": "+25.67", "change_percent": "+2.78%"}
    }
    
    if symbol.upper() in stock_data:
        data = stock_data[symbol.upper()]
        return f"{symbol}当前价格: ${data['price']}，涨跌: {data['change']} ({data['change_percent']})"
    else:
        return f"未找到股票代码 {symbol} 的数据"

def get_stock_news(symbol: str) -> str:
    """获取股票相关新闻，输入股票代码"""
    news_data = {
        "AAPL": "苹果公司宣布新款iPhone销量超预期，分析师看好未来增长",
        "MSFT": "微软Azure云服务收入增长强劲，企业市场表现突出",
        "TSLA": "特斯拉发布新款Model 3，预计将推动销量增长",
        "NVDA": "英伟达AI芯片需求旺盛，数据中心业务持续增长"
    }
    
    return news_data.get(symbol.upper(), f"暂无{symbol}相关新闻")

# 创建工具列表
tools = [
    Tool(
        name="Stock_Price",
        func=get_stock_price,
        description="查询股票当前价格，输入股票代码如AAPL、MSFT"
    ),
    Tool(
        name="Stock_News",
        func=get_stock_news,
        description="获取股票相关新闻，输入股票代码"
    )
]

# 初始化Agent
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True
)

# 执行查询
if __name__ == "__main__":
#    if not os.getenv("DEEPSEEK_API_KEY"):
#        print("请设置DEEPSEEK_API_KEY环境变量")
#    else:
        queries = [
            "苹果公司(AAPL)的当前股价是多少？有什么最新新闻？",
            "查询微软和英伟达的股价，并比较它们的表现",
            "特斯拉最近有什么新闻？当前价格如何？"
        ]
        
        for query in queries:
            print(f"\n查询: {query}")
            result = agent.run(query)
            print(f"结果: {result}")
            print("-" * 80)