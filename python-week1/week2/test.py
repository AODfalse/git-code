from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 获取环境变量值
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    print("请设置DEEPSEEK_API_KEY环境变量")
    
else:
    print("结果: normal")
    print(f"当前DEEPSEEK_API_KEY的值: {deepseek_api_key}")  # 使用f-string正确格式化输出

import akshare as ak
ak.set_options({"requests_kwargs": {"headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}}})
df = ak.stock_zh_a_spot_sina()
print(df[df['代码'] == 'sh600519'])  # 查看贵州茅台数据
