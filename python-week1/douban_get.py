import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

# 配置参数
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
BASE_URL = "https://movie.douban.com/top250?start={}&filter="

def extract_genres(info_text):
    """从豆瓣电影信息文本中提取类型"""
    # 清理文本
    cleaned_text = re.sub(r'\s+', ' ', info_text).strip()
    
    # 方案1：提取最后一个斜杠后的内容
    if "/" in cleaned_text:
        last_part = cleaned_text.rsplit("/", 1)[-1].strip()
        genres = re.findall(r'([\u4e00-\u9fa5]{2,})', last_part)
        if genres:
            return genres
    
    # 方案2：匹配特定模式
    match = re.search(r'/([^/]+?)\s*/([^/]+)$', cleaned_text)
    if match:
        genre_str = match.group(2).strip()
        return re.findall(r'([\u4e00-\u9fa5]{2,})', genre_str)
    
    # 方案3：提取所有中文词（备选）
    all_chinese = re.findall(r'([\u4e00-\u9fa5]{2,})', cleaned_text)
    return all_chinese[-2:] if len(all_chinese) >= 2 else all_chinese

def scrape_douban_top100():
    """爬取豆瓣TOP100电影数据"""
    movies = []
    
    # 爬取4页（每页25条，共100条）
    for page in range(0, 100, 25):
        url = BASE_URL.format(page)
        print(f"正在爬取: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # 检查HTTP错误
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select(".item")
            
            for item in items:
                # 提取中文标题（排除英文标题）
                title_elem = item.select_one(".title")
                title = title_elem.text.strip() if title_elem else "未知"
                if not re.search('[\u4e00-\u9fa5]', title):  # 过滤纯英文标题
                    continue
                
                # 提取评分
                rating_elem = item.select_one(".rating_num")
                rating = float(rating_elem.text.strip()) if rating_elem else 0.0
                
                # 提取链接
                link_elem = item.select_one(".hd > a")
                link = link_elem['href'] if link_elem else ""
                
                # 提取信息文本
                info_elem = item.select_one(".bd > p")
                info_text = info_elem.text.strip() if info_elem else ""
                
                # 提取年份
                year_match = re.search(r'(\d{4})', info_text)
                year = year_match.group(1) if year_match else "未知"
                
                # 提取类型
                genres = extract_genres(info_text)
                
                movies.append({
                    'title': title,
                    'rating': rating,
                    'year': year,
                    'genres': ", ".join(genres) if genres else "未知",
                    'link': link
                })
            
            time.sleep(1.5)  # 礼貌性延迟
        
        except Exception as e:
            print(f"爬取失败: {e}")
            continue
    
    return pd.DataFrame(movies)

# 执行爬取
df = scrape_douban_top100()
print(f"成功爬取 {len(df)} 部电影")

# 保存结果
df.to_csv("douban_top100.csv", index=False, encoding='utf-8-sig')
print("数据已保存为 douban_top100.csv")