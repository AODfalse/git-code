from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_deepseek import ChatDeepSeek  # 正确导入方式
from langchain.memory import ConversationBufferMemory

# 加载环境变量
load_dotenv()

# 配置DeepSeek API
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com/v1"  # DeepSeek API端点
)

# 金融分析师Agent函数
def financial_analysis(query: str) -> str:
    prompt = f"作为专业金融分析师，请分析：{query}\n请提供基本面分析、技术面分析和投资建议。"
    return llm.invoke(prompt).content

# 数据研究员Agent函数  
def market_research(query: str) -> str:
    prompt = f"作为数据研究员，请研究：{query}\n请提供数据统计、行业对比和历史趋势分析。"
    return llm.invoke(prompt).content

# 创建工具列表
tools = [
    Tool(
        name="Financial_Analysis",
        func=financial_analysis,
        description="用于股票分析和投资建议"
    ),
    Tool(
        name="Market_Research", 
        func=market_research,
        description="用于市场数据研究和统计分析"
    )
]

# 创建记忆和Agent执行器
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

# 使用示例
if __name__ == "__main__":
    response = agent.run("分析苹果公司(AAPL)的当前投资价值")
    print(response)