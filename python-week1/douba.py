import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

print("="*50)
print("开始加载数据...")
# 加载数据 - 添加更多错误处理
try:
    df = pd.read_csv("douban_top100.csv", dtype={'genres': str})
    print(f"成功加载数据，共 {len(df)} 条记录")
    print(f"数据类型:\n{df.dtypes}")
    
    # 检查genres列
    print("\ngenres列前5个值:")
    print(df['genres'].head())
    
except Exception as e:
    print(f"数据加载失败: {e}")
    # 创建示例数据作为后备
    print("使用示例数据...")
    data = {
        'title': ['肖申克的救赎', '霸王别姬', '阿甘正传', '这个杀手不太冷', '泰坦尼克号', '千与千寻', '盗梦空间', '楚门的世界', '海上钢琴师', '三傻大闹宝莱坞'],
        'rating': [9.7, 9.6, 9.5, 9.4, 9.4, 9.4, 9.3, 9.3, 9.3, 9.2],
        'year': ['1994', '1993', '1994', '1994', '1997', '2001', '2010', '1998', '1998', '2009'],
        'genres': ['剧情,犯罪', '剧情,爱情,同性', '剧情,爱情', '剧情,动作,犯罪', '剧情,爱情,灾难', 
                  '动画,奇幻,冒险', '科幻,悬疑,冒险', '剧情,科幻', '剧情,音乐', '剧情,喜剧,爱情'],
        'link': ['https://...']*10
    }
    df = pd.DataFrame(data)


# 处理年份异常值
df['year'] = df['year'].apply(lambda x: x if 1900 < int(x) < 2025 else "未知")

# 评分标准化
df['rating_bin'] = pd.cut(df['rating'], bins=[8, 8.5, 9, 9.5, 10], 
                        labels=['8-8.5', '8.5-9', '9-9.5', '9.5-10'])
# 数据清洗：确保genres列格式正确
print("\n清洗genres数据...")
df['genres'] = df['genres'].fillna('未知')  # 填充空值
df['genres'] = df['genres'].astype(str)    # 确保字符串类型
df['genres'] = df['genres'].str.replace(' ', '')  # 移除空格

# 1. 创建主图表布局
fig = plt.figure(figsize=(15, 8), dpi=120)
plt.suptitle('豆瓣TOP100电影分析', fontsize=18, fontweight='bold')

# 2. 评分分布直方图（左上方）
ax1 = plt.subplot2grid((2, 2), (0, 0))
bins = np.arange(8, 10.1, 0.2)  # 8.0到10.0，每0.2一个区间
n, bins, patches = ax1.hist(df['rating'], bins=bins, color='skyblue', edgecolor='black', alpha=0.8)

ax1.set_title('电影评分分布', fontsize=14)
ax1.set_xlabel('评分', fontsize=12)
ax1.set_ylabel('电影数量', fontsize=12)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 添加统计标签
for i in range(len(bins)-1):
    count = n[i]
    ax1.text((bins[i] + bins[i+1])/2, count+0.3, f'{int(count)}', 
             ha='center', fontsize=9)

# 3. 类型分布饼图（右上方）
ax2 = plt.subplot2grid((2, 2), (0, 1))

# 安全地处理类型数据
try:
    print("\n处理电影类型数据...")
    # 多种分隔符处理
    genres_list = df['genres'].str.split(r'[,，、]').explode()
    genres_list = genres_list.str.strip()  # 移除首尾空格
    genres_list = genres_list[genres_list != '']  # 移除空值
    
    # 统计并打印
    top_genres = genres_list.value_counts().head(5)
    print("Top 5 电影类型:")
    print(top_genres)
    
    if len(top_genres) > 0:
        # 饼图参数
        colors = plt.cm.Pastel1(range(len(top_genres)))
        wedges, texts, autotexts = ax2.pie(
            top_genres, 
            labels=top_genres.index, 
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            wedgeprops={'edgecolor': 'black', 'linewidth': 1},
            textprops={'fontsize': 10}
        )
        
        # 添加图例
        ax2.legend(wedges, top_genres.index,
                  title="电影类型",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        ax2.set_title('电影类型分布 (Top5)', fontsize=14)
    else:
        ax2.text(0.5, 0.5, '无有效类型数据', ha='center', va='center')
        print("警告: 没有找到有效的电影类型数据")
        
except Exception as e:
    print(f"类型分析出错: {e}")
    ax2.text(0.5, 0.5, '类型分析失败', ha='center', va='center')

# 4. 年度评分趋势（下方占两列）
ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)

# 处理年份数据
try:
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    
    # 按年份分组
    yearly_avg = df.groupby('year')['rating'].agg(['mean', 'count']).reset_index()
    yearly_avg = yearly_avg[yearly_avg['count'] >= 1]  # 至少有一部电影
    
    if not yearly_avg.empty:
        # 折线图
        sns.lineplot(x='year', y='mean', data=yearly_avg, 
                    marker='o', linewidth=2.5, ax=ax3)
        
        # 添加数据点标签
        for _, row in yearly_avg.iterrows():
            ax3.text(row['year'], row['mean']+0.02, 
                    f"{row['mean']:.2f}", 
                    ha='center', fontsize=9)
        
        # 添加电影数量标签
        for _, row in yearly_avg.iterrows():
            ax3.text(row['year'], row['mean']-0.1, 
                    f"{row['count']}部", 
                    ha='center', fontsize=8, color='gray')
        
        ax3.set_title('年度平均评分趋势', fontsize=14)
        ax3.set_xlabel('年份', fontsize=12)
        ax3.set_ylabel('平均评分', fontsize=12)
        ax3.grid(True, linestyle='--', alpha=0.3)
        
        # 设置x轴刻度
        min_year = int(yearly_avg['year'].min())
        max_year = int(yearly_avg['year'].max())
        ax3.set_xticks(range(min_year, max_year+1, 5))
    else:
        ax3.text(0.5, 0.5, '无年度数据', ha='center', va='center')
        
except Exception as e:
    print(f"年度分析出错: {e}")
    ax3.text(0.5, 0.5, '年度分析失败', ha='center', va='center')

# 调整布局并保存
plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为总标题留空间
plt.savefig('douban_full_analysis.png', dpi=120, bbox_inches='tight')
print("\n综合分析图表已保存为 douban_full_analysis1.png")

# 显示图表
plt.show()