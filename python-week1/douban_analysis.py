import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
#df = pd.read_csv("douban_top100.csv")
df = pd.read_csv("douban_top100.csv", dtype={'genres': str})

# 处理年份异常值
df['year'] = df['year'].apply(lambda x: x if 1900 < int(x) < 2025 else "未知")

# 评分标准化
df['rating_bin'] = pd.cut(df['rating'], bins=[8, 8.5, 9, 9.5, 10], 
                        labels=['8-8.5', '8.5-9', '9-9.5', '9.5-10'])
# 1. 评分分布直方图
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)  # 左图

# 按0.5分区间统计
bins = [i/2 for i in range(16, 22)]  # 8.0~10.5分区间
plt.hist(df['rating'], bins=bins, color='skyblue', edgecolor='black', alpha=0.8)

plt.title('豆瓣TOP100电影评分分布', fontsize=14)
plt.xlabel('评分', fontsize=12)
plt.ylabel('电影数量', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 添加统计标签
for i in range(len(bins)-1):
    count = len(df[(df['rating'] >= bins[i]) & (df['rating'] < bins[i+1])])
    plt.text((bins[i]+bins[i+1])/2, count+0.5, str(count), 
             ha='center', fontsize=10)

# 2. 类型分析（右图）
plt.subplot(1, 2, 2)  # 右图

# 展开电影类型
genres_list = df['genres'].str.split(', ').explode()
top_genres = genres_list.value_counts().head(5)

# 饼图
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0']
plt.pie(top_genres, labels=top_genres.index, autopct='%1.1f%%',
        colors=colors, startangle=90, wedgeprops={'edgecolor':'black'})
plt.title('电影类型分布(Top5)', fontsize=14)

# 整体调整
plt.tight_layout()
plt.savefig('douban_analysis.png', dpi=120, bbox_inches='tight')
print("可视化图表已保存为 douban_analysis.png")

# 3. 高级分析：年度评分趋势
plt.figure(figsize=(10, 5))
sns.lineplot(x='year', y='rating', data=df, 
             estimator='mean', errorbar=None, marker='o', linewidth=2.5)
plt.title('TOP100电影年度平均评分趋势', fontsize=14)
plt.xlabel('年份', fontsize=12)
plt.ylabel('平均评分', fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.3)
plt.savefig('yearly_rating_trend.png', dpi=120, bbox_inches='tight')