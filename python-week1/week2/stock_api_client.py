import os
import akshare as ak
from dotenv import load_dotenv
import json
from typing import Dict
import logging

# 基础配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class StockDataAPI:
    """适配AKShare 1.17.61的股票数据客户端（移除params参数）"""
    
    def __init__(self):
        logger.info("✅ StockDataAPI初始化完成（适配AKShare 1.17.61）")

    def _format_a_share_code(self, symbol: str) -> str:
        """补全A股代码前缀"""
        symbol = symbol.strip()
        if symbol.startswith(("sh", "sz")):
            return symbol
        if len(symbol) == 6:
            if symbol.startswith("6"):
                return f"sh{symbol}"
            elif symbol.startswith(("0", "3")):
                return f"sz{symbol}"
        return symbol

    def _get_real_stock_price(self, formatted_symbol: str) -> Dict:
        """获取实时数据（移除params参数）"""
        try:
            # 关键修复：1.17.61版本的stock_zh_a_spot不接受任何参数
            stock_df = ak.stock_zh_a_spot()  # 移除params参数
            
            # 验证数据结构
            if "代码" not in stock_df.columns:
                raise ValueError("数据源字段不匹配（旧版本AKShare特征）")
            
            # 匹配目标股票
            target_data = stock_df[stock_df["代码"] == formatted_symbol]
            if target_data.empty:
                raise ValueError(f"未找到代码 {formatted_symbol} 的数据")
            
            # 提取数据
            raw_symbol = formatted_symbol.lstrip("shsz")
            return {
                "symbol": raw_symbol,
                "price": round(float(target_data.iloc[0]["最新价"]), 2),
                "change": round(float(target_data.iloc[0]["涨跌额"]), 2),
                "change_percent": round(float(target_data.iloc[0]["涨跌幅"]), 2),
                "volume": f"{int(target_data.iloc[0]['成交量']):,}",
                "amount": f"{round(float(target_data.iloc[0]['成交额'])/10000, 2)}万",
                "update_time": "实时更新",
                "source": "AKShare(实时数据)"
            }

        except ValueError as ve:
            logger.warning(f"⚠️ 实时数据获取失败: {str(ve)}，切换为模拟数据")
            return self._get_mock_stock_price(formatted_symbol.lstrip("shsz"))
        except Exception as e:
            error_msg = str(e)
            if "<" in error_msg:
                logger.error("❌ 被反爬拦截（旧版本无请求头配置，建议稍后重试）")
            else:
                logger.error(f"❌ 数据请求错误: {str(e)[:100]}")
            return self._get_mock_stock_price(formatted_symbol.lstrip("shsz"))

    def _get_mock_stock_price(self, symbol: str) -> Dict:
        """模拟数据（备用）"""
        mock_db = {
            "AAPL": {"price": 178.72, "change": 2.15, "change_percent": 1.22},
            "MSFT": {"price": 337.69, "change": 1.23, "change_percent": 0.37},
            "TSLA": {"price": 209.98, "change": -3.45, "change_percent": -1.62},
            "600519": {"price": 1689.00, "change": 15.80, "change_percent": 0.94},
            "000858": {"price": 145.20, "change": 2.30, "change_percent": 1.61}
        }
        data = mock_db.get(symbol.upper(), {"price": 100.00, "change": 0.00, "change_percent": 0.00})
        return {
            "symbol": symbol,
            "price": data["price"],
            "change": data["change"],
            "change_percent": data["change_percent"],
            "volume": "1,000,000",
            "amount": "10,000.00万",
            "source": "本地模拟"
        }

    def get_stock_price(self, symbol: str) -> Dict:
        """对外接口"""
        formatted_symbol = self._format_a_share_code(symbol)
        if formatted_symbol.startswith(("sh", "sz")):
            return self._get_real_stock_price(formatted_symbol)
        else:
            return self._get_mock_stock_price(symbol)

    def get_company_info(self, symbol: str) -> Dict:
        """公司信息"""
        company_db = {
            "600519": {"name": "贵州茅台", "industry": "白酒", "market_cap": "2.1万亿"},
            "000858": {"name": "五粮液", "industry": "白酒", "market_cap": "0.7万亿"},
            "AAPL": {"name": "苹果", "industry": "科技", "market_cap": "2.8万亿美元"},
            "TSLA": {"name": "特斯拉", "industry": "新能源汽车", "market_cap": "0.7万亿美元"}
        }
        return company_db.get(symbol.upper(), {"name": f"未知公司({symbol})"})

# 测试
if __name__ == "__main__":
    try:
        api = StockDataAPI()
        for symbol in ["600519", "000858", "AAPL"]:
            print(f"\n查询 {symbol}：")
            print("价格数据：", json.dumps(api.get_stock_price(symbol), indent=2, ensure_ascii=False))
            print("公司信息：", json.dumps(api.get_company_info(symbol), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"程序错误：{e}")
