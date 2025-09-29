# multi_agent_basic.py
from autogen import AssistantAgent, UserProxyAgent
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取 API Key，确保已设置 DEEPSEEK_API_KEY
api_key = os.getenv("DEEPSEEK_API_KEY") 

# 正确的 LLM 配置
config_list = [
    {
        "model": "deepseek-chat",  # 例如 "deepseek-chat", "deepseek-reasoner"
        "api_key": api_key,
        "base_url": "https://api.deepseek.com",  # DeepSeek API 的端点
        "api_type": "openai"  # 关键修正：使用 'openai' 而不是 'open_ai'
    }
]

# 创建金融分析师Agent
financial_analyst = AssistantAgent(
    name="Financial_Analyst",
    system_message="""你是一名专业金融分析师，擅长股票市场分析和投资建议。
    请使用专业术语和数据分析来支持你的观点。
    当用户询问股票或公司时，提供详细的基本面分析和技术分析。""",
    llm_config={"config_list": config_list}
)

# 创建数据查询Agent
data_researcher = AssistantAgent(
    name="Data_Researcher",
    system_message="""你负责查询和整理金融市场数据。
    当分析师需要具体数据时，你会提供准确的市场数据、财务指标和行业比较。""",
    llm_config={"config_list": config_list}
)

# 创建用户代理
user_proxy = UserProxyAgent(
    name="User_Proxy",
    human_input_mode="TERMINATE",  # 在需要时请求人工输入
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},
    system_message="""你是一个用户代理，负责与金融分析师和数据研究员沟通。
    你会将用户的问题转发给合适的专家，并整理他们的回答。"""
)

# 初始化对话
def initiate_stock_analysis(symbol):
    """初始化股票分析对话"""
    user_proxy.initiate_chat(
        financial_analyst,
        message=f"请分析{symbol}公司最近一个季度的财务表现和投资潜力"
    )

# 示例使用
if __name__ == "__main__":
    # 设置OpenAI API密钥（如果未在环境变量中设置）
    if not os.getenv("OPENAI_API_KEY"):
        print("请设置OPENAI_API_KEY环境变量")
    else:
        initiate_stock_analysis("AAPL")