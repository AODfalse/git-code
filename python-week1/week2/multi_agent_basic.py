import os
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# 配置DeepSeek模型
def get_llm():
    """获取配置好的LLM实例"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "sk-8e6cab5152e5434d840afa871153bf56")
    
    if not api_key or api_key.strip() == "":
        raise ValueError("请设置有效的DEEPSEEK_API_KEY环境变量")
        
    return ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=api_key,
        openai_api_base="https://api.deepseek.com/v1",
        temperature=0.3
    )

# 创建专业Agent函数
def financial_analysis(query: str) -> str:
    """金融分析Agent"""
    prompt = f"""
    作为专业金融分析师，请分析：{query}
    
    请提供：
    1. 基本面分析（财务数据、盈利能力）
    2. 技术面分析（市场表现、趋势）
    3. 投资建议和风险提示
    """
    return llm.invoke(prompt).content

def market_research(query: str) -> str:
    """市场研究Agent"""
    prompt = f"""
    作为市场研究员，请研究：{query}
    
    请提供：
    1. 行业数据和市场趋势
    2. 竞争格局分析
    3. 增长前景评估
    """
    return llm.invoke(prompt).content

# 初始化LLM
try:
    llm = get_llm()
except ValueError as e:
    print(f"初始化失败: {e}")
    exit(1)

# 创建工具列表
tools = [
    Tool(
        name="Financial_Analyst",
        func=financial_analysis,
        description="用于股票分析和投资建议，输入公司名称或股票代码"
    ),
    Tool(
        name="Market_Researcher",
        func=market_research,
        description="用于市场数据研究和行业分析，输入行业或公司名称"
    )
]

# 创建输出解析器
output_parser = StructuredChatOutputParser()

# 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""你是一个拥有金融分析和市场研究能力的助手。
    你可以使用以下工具来帮助回答问题：
    
    {tools}
    
    工具名称列表：{[tool.name for tool in tools]}
    
    使用工具的格式如下，必须严格遵守：
    ```json
    {{{{
      "action": {{
        "name": "工具名称",
        "parameters": {{
          "query": "查询内容"
        }}
      }}
    }}}}
    ```
    
    {output_parser.get_format_instructions()}
    
    根据用户问题，选择合适的工具进行分析。如果不需要工具，可以直接回答。"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 创建记忆
memory = ConversationBufferMemory(
    memory_key="chat_history", 
    return_messages=True,
    output_key="output"
)

# 创建Agent
agent = create_structured_chat_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    output_parser=output_parser
)

# 创建Agent执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    return_intermediate_steps=False,
    handle_parsing_errors=True
)

# 多Agent协作示例
def multi_agent_chat(question):
    """多Agent协作对话"""
    print(f"用户问题: {question}")
    response = agent_executor.invoke({
        "input": question,
        "agent_scratchpad": []
    })
    print(f"AI回答: {response['output']}")
    return response['output']

if __name__ == "__main__":
    questions = [
        "分析苹果公司的投资价值",
        "研究科技行业的市场趋势",
        "对比分析苹果和微软的投资潜力"
    ]
    
    for question in questions:
        multi_agent_chat(question)
        print("\n" + "="*50 + "\n")
    