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
<<<<<<< HEAD
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
=======
        openai_api_key=os.getenv("DEEPSEEK_API_KEY", "sk-8e6cab5152e5434d840afa871153bf56"),
>>>>>>> 6e5e589f394b2b03a2ffc9ad836f67a928b834e2
        openai_api_base="https://api.deepseek.com/v1"  # DeepSeek API端点
    )
    logger.info("DeepSeek LLM初始化成功")
except Exception as e:
    logger.warning(f"DeepSeek LLM初始化失败: {e}")
    llm = None

class MultiModelAgentSystem:
    """基于ModelScope的多模型Agent系统"""
    
    def __init__(self):
        # 可以加载多个不同的模型作为不同的Agent
        self.models = {}
        self.use_fallback = False
        self.setup_models()
    
    def setup_models(self):
        """设置多个模型作为不同的Agent"""
        try:
            # 尝试安装缺失的依赖
            self._install_dependencies()
            
            # 替换为更稳定的模型，避免使用需要megatron_util的模型
            # 金融分析模型 - 使用bert-base-chinese作为替代
            self.models['financial'] = pipeline(
                task=Tasks.text_generation,
                model='ZhipuAI/chatglm2-6b',  # 更稳定的中文模型
                model_revision='v1.0.2'
            )
            logger.info("金融分析Agent初始化完成")
            
            # 市场研究模型 - 使用另一个可靠模型
            self.models['research'] = pipeline(
                task=Tasks.text_generation, 
                model='baichuan-inc/Baichuan-13B-Chat',  # 百川模型
                model_revision='v1.0.0'
            )
            logger.info("数据研究Agent初始化完成")
            
        except Exception as e:
            logger.error(f"模型初始化失败: {str(e)}")
            self.setup_fallback_agents()
    
    def _install_dependencies(self):
        """安装可能缺失的依赖"""
        try:
            import megatron_util
        except ImportError:
            logger.info("检测到缺少megatron_util，尝试安装...")
            try:
                import subprocess
                import sys
                # 尝试安装可能包含megatron_util的包
                subprocess.check_call([sys.executable, "-m", "pip", "install", "megatron-llm"])
                logger.info("megatron-llm安装成功")
            except Exception as e:
                logger.warning(f"自动安装megatron-llm失败: {e}，将尝试使用替代模型")
    
    def setup_fallback_agents(self):
        """备用Agent设置（基于规则或DeepSeek）"""
        self.use_fallback = True
        if llm:
            logger.info("使用DeepSeek作为备用Agent系统")
        else:
            logger.info("使用基于规则的备用Agent系统")
        
    def financial_analysis(self, symbol):
        """金融分析Agent"""
        prompt = f"详细分析{symbol}公司的投资价值、潜在风险、近期财务表现和未来发展前景。"
        
        # 优先使用modelscope模型
        if 'financial' in self.models and not self.use_fallback:
            try:
                result = self.models['financial'](prompt, max_length=500)
                return result.get('text', '分析结果生成中...').strip()
            except Exception as e:
                logger.error(f"金融分析模型调用失败: {e}")
                self.use_fallback = True
        
        #  fallback到DeepSeek
        if llm and not self.use_fallback:
            try:
                response = llm.invoke(prompt)
                return response.content.strip()
            except Exception as e:
                logger.error(f"DeepSeek调用失败: {e}")
                self.use_fallback = True
        
        # 最后使用基于规则的回复
        return f"基于规则分析：{symbol}是一家在其行业内具有影响力的公司。从财务角度看，建议关注其营收增长率、利润率和资产负债率等关键指标。近期市场波动可能对其股价产生影响，需结合宏观经济环境综合评估投资价值。"
    
    def market_research(self, symbol):
        """市场研究Agent"""
        prompt = f"详细研究{symbol}公司的市场份额、主要竞争对手、行业趋势、消费者评价和市场扩张策略。"
        
        # 优先使用modelscope模型
        if 'research' in self.models and not self.use_fallback:
            try:
                result = self.models['research'](prompt, max_length=500)
                return result.get('text', '研究结果生成中...').strip()
            except Exception as e:
                logger.error(f"市场研究模型调用失败: {e}")
                self.use_fallback = True
        
        #  fallback到DeepSeek
        if llm and not self.use_fallback:
            try:
                response = llm.invoke(prompt)
                return response.content.strip()
            except Exception as e:
                logger.error(f"DeepSeek调用失败: {e}")
                self.use_fallback = True
        
        # 最后使用基于规则的回复
        return f"基于规则研究：{symbol}在行业中占据重要地位，市场份额处于领先水平。其主要竞争对手包括行业内其他头部企业，公司通过持续创新和市场推广维持竞争优势。近年来，该公司在多个新兴市场的业务增长显著。"

# 使用示例
if __name__ == "__main__":
    print("初始化多模型Agent系统...")
    agent_system = MultiModelAgentSystem()
    
    # 多Agent协作分析
    companies = ["苹果", "特斯拉", "微软"]
    
    for company in companies:
        print(f"\n=== 分析 {company} 公司 ===")
        
        # 金融分析Agent工作
        financial_analysis = agent_system.financial_analysis(company)
        print(f"金融分析: {financial_analysis}")
        
        # 市场研究Agent工作  
        market_research = agent_system.market_research(company)
        print(f"市场研究: {market_research}")
