import os
import logging
from dotenv import load_dotenv
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from stock_api_client import StockDataAPI  # 导入股票数据API

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 初始化股票API
try:
    stock_api = StockDataAPI()
    logger.info("✅ 股票数据API初始化成功")
except Exception as e:
    logger.error(f"❌ 股票数据API初始化失败: {str(e)}")
    raise  # 初始化失败则终止程序

# 配置DeepSeek模型
def initialize_llm():
    """初始化语言模型"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("请在.env文件中设置DEEPSEEK_API_KEY")
    
    try:
        llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1",
            temperature=0.3  # 低温度确保回答更稳定
        )
        logger.info("✅ DeepSeek模型初始化成功")
        return llm
    except Exception as e:
        logger.error(f"❌ 模型初始化失败: {str(e)}")
        raise

# 创建股票工具函数
def stock_price_tool(symbol: str) -> str:
    """查询股票实时价格"""
    try:
        logger.info(f"查询股票价格: {symbol}")
        data = stock_api.get_stock_price(symbol)
        
        # 确保数值类型正确
        price = data['price'] if isinstance(data['price'], (int, float)) else "未知"
        change = data['change'] if isinstance(data['change'], (int, float)) else "未知"
        change_percent = data['change_percent'] if isinstance(data['change_percent'], (int, float)) else "未知"
        
        return f"""
{symbol}股票实时信息:
- 当前价格: {price}
- 涨跌额: {change} (涨跌幅: {change_percent}%)
- 成交量: {data.get('volume', 'N/A')}
- 成交额: {data.get('amount', 'N/A')}
- 数据来源: {data.get('source', '未知')}
        """.strip()
    except Exception as e:
        error_msg = f"获取{symbol}价格失败: {str(e)}"
        logger.warning(error_msg)
        return error_msg

def company_info_tool(symbol: str) -> str:
    """查询公司基本信息"""
    try:
        logger.info(f"查询公司信息: {symbol}")
        info = stock_api.get_company_info(symbol)
        return f"""
{info['name']}({symbol})公司概况:
- 所属行业: {info.get('industry', '未知')}
- 市值: {info.get('market_cap', '未知')}
- 公司描述: {info.get('description', '暂无描述')}
        """.strip()
    except Exception as e:
        error_msg = f"获取{symbol}公司信息失败: {str(e)}"
        logger.warning(error_msg)
        return error_msg

def investment_analysis_tool(query: str) -> str:
    """进行投资分析和建议"""
    try:
        logger.info(f"进行投资分析: {query[:50]}...")  # 只显示前50字符
        llm = initialize_llm()  # 初始化分析用的模型
        
        prompt = f"""
作为专业投资顾问，请分析以下投资问题：{query}

请从以下角度提供专业分析：
1. 投资价值评估（结合行业地位和基本面）
2. 风险因素分析（市场风险、政策风险等）
3. 市场前景展望（短期和长期趋势）
4. 具体投资建议（简明扼要）

请用专业但易懂的语言回答，避免使用过于复杂的术语。
        """.strip()
        
        return llm.invoke(prompt).content
    except Exception as e:
        error_msg = f"投资分析失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# 创建工具列表
def create_tools():
    """创建Agent可用的工具列表"""
    return [
        Tool(
            name="Stock_Price_Query",
            func=stock_price_tool,
            description="查询股票实时价格、涨跌幅和成交量，输入股票代码（如AAPL、600519）"
        ),
        Tool(
            name="Company_Info_Query",
            func=company_info_tool,
            description="查询公司基本信息，包括所属行业、市值和公司描述，输入股票代码"
        ),
        Tool(
            name="Investment_Analysis",
            func=investment_analysis_tool,
            description="对特定股票或投资问题进行专业分析和建议，输入具体问题"
        )
    ]

# 初始化Agent系统
def create_agent(llm, tools):
    """创建智能代理"""
    try:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5  # 限制最大迭代次数，避免无限循环
        )
        logger.info("✅ Agent系统初始化成功")
        return agent
    except Exception as e:
        logger.error(f"❌ Agent初始化失败: {str(e)}")
        raise

def format_agent_response(response):
    """格式化Agent响应，使其更易读"""
    return f"""
🤖 智能投资助手分析结果:
{response}
    """.strip()

# 主程序
if __name__ == "__main__":
    try:
        # 初始化核心组件
        llm = initialize_llm()
        tools = create_tools()
        agent = create_agent(llm, tools)
        
        print("="*60)
        print("🚀 股票分析Agent系统已启动")
        print("📌 支持功能: 股票价格查询、公司信息查询、投资分析建议")
        print("💡 输入示例: '查询600519的价格'、'AAPL的公司信息'、'分析贵州茅台的投资价值'")
        print("🔚 输入'退出'或'quit'结束对话")
        print("="*60 + "\n")
        
        while True:
            user_input = input("💬 请输入您的问题: ").strip()
            
            if user_input.lower() in ['退出', 'quit', 'exit']:
                print("👋 感谢使用，再见！")
                break
                
            if not user_input:
                print("⚠️ 请输入有效的问题")
                continue
            
            print("🔄 正在分析中...\n")
            try:
                response = agent.run(user_input)
                formatted_response = format_agent_response(response)
                print(formatted_response + "\n")
                print("-"*60 + "\n")  # 分隔线
            except Exception as e:
                print(f"❌ 处理请求时出错: {str(e)}")
                print("💡 请尝试重新表述您的问题\n")
                
    except Exception as e:
        print(f"💥 程序启动失败: {str(e)}")
        print("请检查环境变量和依赖是否正确配置")
