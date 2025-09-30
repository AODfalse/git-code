import os
import logging
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from stock_api_client import StockDataAPI

# 加载环境变量
load_dotenv()

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"stock_agent_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("RobustStockAgent")

class RobustStockAgent:
    """强化版股票Agent，含错误处理、重试机制和搜索引擎fallback"""
    
    def __init__(self):
        self.stock_api = StockDataAPI()
        self.retry_count = 3
        self.retry_delay = 2  # 秒
        self.request_count = 0
        self.start_time = datetime.now()
        # 搜索引擎配置（使用SerpAPI）
        self.serp_api_key = os.getenv("SERPAPI_KEY")
        self.enable_search_fallback = bool(self.serp_api_key)
        if self.enable_search_fallback:
            logger.info("✅ 搜索引擎 fallback 已启用")
        else:
            logger.warning("⚠️ 未配置SERPAPI_KEY，搜索引擎功能已禁用")
    
    def _search_stock_info(self, query: str) -> str:
        """通过搜索引擎获取股票信息（fallback机制）"""
        if not self.enable_search_fallback:
            return "⚠️ 未配置搜索引擎API，无法获取补充信息"
        
        try:
            logger.info(f"🔍 正在搜索: {query}")
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serp_api_key,
                "no_cache": "true"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # 检查HTTP错误
            results = response.json()
            
            # 提取相关信息
            if "organic_results" in results and len(results["organic_results"]) > 0:
                top_result = results["organic_results"][0]
                return f"""
📰 搜索引擎补充信息:
标题: {top_result.get('title', '无标题')}
摘要: {top_result.get('snippet', '无摘要')}
来源: {top_result.get('source', '未知来源')}
                """.strip()
            else:
                return "🔍 未找到相关搜索结果"
                
        except Exception as e:
            logger.error(f"❌ 搜索失败: {str(e)}")
            return f"⚠️ 搜索服务出错: {str(e)[:50]}"
    
    def safe_api_call(self, symbol: str, function: str, **kwargs):
        """带重试机制的API调用，失败时触发搜索引擎fallback"""
        for attempt in range(self.retry_count):
            try:
                self.request_count += 1
                logger.info(f"尝试 {attempt+1}/{self.retry_count}: 查询{symbol}的{function}")
                
                if function == "price":
                    result = self.stock_api.get_stock_price(symbol)
                elif function == "company_info":
                    result = self.stock_api.get_company_info(symbol)
                else:
                    return {"error": f"未知功能: {function}"}
                
                # 验证结果
                if result and not result.get('error'):
                    logger.info(f"✅ 成功获取{symbol}的{function}数据")
                    return result
                else:
                    raise ValueError(f"API返回无效数据: {result}")
                
            except Exception as e:
                logger.error(f"❌ 尝试 {attempt+1} 失败: {str(e)}")
                if attempt < self.retry_count - 1:
                    logger.info(f"⏳ 等待{self.retry_delay}秒后重试...")
                    time.sleep(self.retry_delay)
        
        # 所有重试失败，触发fallback
        logger.warning(f"💥 所有重试失败，启动fallback机制")
        error_result = {
            "error": f"查询失败: {str(e)}",
            "symbol": symbol,
            "function": function
        }
        
        # 价格查询失败时，调用搜索引擎补充信息
        if function == "price":
            search_query = f"{symbol} 股票实时价格 最新行情"
            error_result["search_info"] = self._search_stock_info(search_query)
        
        return error_result
    
    def format_stock_response(self, data: dict) -> str:
        """格式化股票响应数据（安全处理缺失字段）"""
        if data.get('error'):
            base_msg = f"❌ 数据获取失败: {data['error']}"
            # 附加搜索信息
            if "search_info" in data:
                return f"{base_msg}\n{data['search_info']}"
            return base_msg
        
        if 'price' in data:
            return f"""
📊 股票价格信息 [{data.get('source', '实时数据')}]:
┌ 股票代码: {data.get('symbol', '未知')}
├ 当前价格: {data.get('price', '未知')}
├ 涨跌情况: {data.get('change', '未知')} ({data.get('change_percent', '未知')}%)
├ 成交量: {data.get('volume', 'N/A')}
└ 成交额: {data.get('amount', 'N/A')}
            """.strip()
        elif 'name' in data:
            return f"""
🏢 公司概况:
┌ 公司名称: {data.get('name', '未知')}
├ 所属行业: {data.get('industry', '未知')}
├ 市值规模: {data.get('market_cap', '未知')}
└ 业务描述: {data.get('description', '暂无描述')}  # 修复KeyError的关键行
            """.strip()
        else:
            return "📝 数据格式未知"
    
    def get_performance_stats(self):
        """获取性能统计"""
        duration = datetime.now() - self.start_time
        return {
            "total_requests": self.request_count,
            "uptime_seconds": duration.total_seconds(),
            "requests_per_minute": self.request_count / (duration.total_seconds() / 60) if duration.total_seconds() > 0 else 0
        }
    
    def batch_query(self, symbols: list, functions: list) -> dict:
        """批量查询多个股票的多个功能"""
        results = {}
        
        for symbol in symbols:
            results[symbol] = {}
            for function in functions:
                logger.info(f"批量查询: {symbol} - {function}")
                results[symbol][function] = self.safe_api_call(symbol, function)
                # 避免过于频繁的请求
                time.sleep(0.5)
        
        return results

# 使用示例
if __name__ == "__main__":
    agent = RobustStockAgent()
    
    # 测试单个查询（包含可能失败的案例）
    print("=== 单个股票查询测试 ===")
    price_data = agent.safe_api_call("600519", "price")  # 尝试A股实时价格
    print(agent.format_stock_response(price_data))
    
    company_data = agent.safe_api_call("AAPL", "company_info")  # 测试公司信息
    print(agent.format_stock_response(company_data))
    
    # 测试批量查询
    print("\n=== 批量查询测试 ===")
    symbols = ["AAPL", "MSFT", "600519", "INVALID_CODE"]  # 包含无效代码
    functions = ["price", "company_info"]
    
    batch_results = agent.batch_query(symbols, functions)
    
    for symbol, data in batch_results.items():
        print(f"\n📈 {symbol} 综合分析:")
        for func, result in data.items():
            print(agent.format_stock_response(result))
            print("-" * 50)
    
    # 显示性能统计
    stats = agent.get_performance_stats()
    print(f"\n📊 性能统计:")
    print(f"- 总请求数: {stats['total_requests']}")
    print(f"- 运行时间: {stats['uptime_seconds']:.2f}秒")
    print(f"- 请求频率: {stats['requests_per_minute']:.2f}次/分钟")
