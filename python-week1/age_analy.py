import os
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm  # 导入字体管理模块

# 1. 检查并设置中文字体
def setup_chinese_font():
    """设置中文字体支持"""
    # 获取系统中所有可用字体
    font_list = [f.name for f in fm.fontManager.ttflist]
    
    # 尝试多种常见中文字体
    chinese_fonts = [
        'SimHei', 'Microsoft YaHei', 'KaiTi', 'Arial Unicode MS',
        'PingFang SC', 'Heiti SC', 'STHeiti', 'Songti SC', 'WenQuanYi Micro Hei',
        'Noto Sans CJK SC', 'Droid Sans Fallback'
    ]
    
    # 查找系统可用的中文字体
    available_fonts = []
    for font in chinese_fonts:
        if any(f.lower() == font.lower() for f in font_list):
            available_fonts.append(font)
    
    # 设置字体
    if available_fonts:
        # 使用找到的第一个可用中文字体
        selected_font = available_fonts[0]
        plt.rcParams['font.sans-serif'] = [selected_font]
        print(f"✅ 已设置中文字体: {selected_font}")
    else:
        # 如果找不到中文字体，尝试添加字体路径
        try:
            # 尝试使用思源黑体（开源字体）
            font_path = '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'  # Linux路径
            if not os.path.exists(font_path):
                font_path = 'C:/Windows/Fonts/msyh.ttc'  # Windows路径
            
            if os.path.exists(font_path):
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = font_prop.get_name()
                print(f"✅ 通过路径加载中文字体: {font_path}")
            else:
                print("⚠️ 未找到系统中文字体，图表中文可能显示为方块")
        except:
            print("⚠️ 字体设置失败，图表中文可能显示为方块")
    
    # 确保正确显示负号
    plt.rcParams['axes.unicode_minus'] = False

# 执行字体设置
setup_chinese_font()


# ======================
# 第一部分：创建示例数据集
# ======================
# 如果还没有数据集，可以创建模拟数据
def create_titanic_dataset(num_rows=100):
    """创建泰坦尼克号模拟数据集"""
    np.random.seed(42)  # 确保结果可复现
    
    data = {
        'PassengerId': range(1, num_rows+1),
        'Survived': np.random.randint(0, 2, num_rows),
        'Pclass': np.random.choice([1, 2, 3], num_rows, p=[0.2, 0.3, 0.5]),
        'Name': [f'Passenger {i}' for i in range(1, num_rows+1)],
        'Sex': np.random.choice(['male', 'female'], num_rows, p=[0.65, 0.35]),
        'Age': np.where(np.random.random(num_rows) > 0.25, 
                      np.random.normal(loc=30, scale=15, size=num_rows).clip(0.1, 80), 
                      np.nan),  # 25%缺失值
        'SibSp': np.random.randint(0, 5, num_rows),
        'Parch': np.random.randint(0, 4, num_rows),
        'Fare': np.round(np.random.uniform(5, 300, num_rows), 2)
    }
    
    # 确保年龄为浮点数
    data['Age'] = data['Age'].astype(float)
    
    # 添加一些异常值
    outlier_indices = np.random.choice(num_rows, size=5, replace=False)
    for i in outlier_indices:
        data['Age'][i] = np.random.choice([-5, 100, 150])
    
    return pd.DataFrame(data)

# 创建数据集
df = create_titanic_dataset(300)  # 创建300行数据
print("数据集创建成功!")
print(f"数据集形状: {df.shape}")
print(f"原始年龄缺失值数量: {df['Age'].isnull().sum()}")

# =================================
# 第二部分：按性别分组填充年龄缺失值
# =================================
def fill_age_by_sex(df):
    """按性别分组填充年龄缺失值"""
    print("\n===== 按性别分组填充年龄 =====")
    
    # 1. 计算男性和女性的年龄中位数
    male_median = df.loc[df['Sex'] == 'male', 'Age'].median()
    female_median = df.loc[df['Sex'] == 'female', 'Age'].median()
    
    print(f"男性年龄中位数: {male_median:.1f}岁")
    print(f"女性年龄中位数: {female_median:.1f}岁")
    
    # 2. 填充缺失值
    # 男性缺失值
    male_mask = (df['Sex'] == 'male') & (df['Age'].isnull())
    df.loc[male_mask, 'Age'] = male_median
    
    # 女性缺失值
    female_mask = (df['Sex'] == 'female') & (df['Age'].isnull())
    df.loc[female_mask, 'Age'] = female_median
    
    # 3. 验证结果
    print(f"填充后年龄缺失值数量: {df['Age'].isnull().sum()}")
    
    # 4. 添加年龄分组信息
    bins = [0, 12, 18, 30, 50, 100]
    labels = ['儿童', '青少年', '青年', '中年', '老年']
    df['AgeGroup'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    
    return df

# 执行填充
df = fill_age_by_sex(df)

# =================================
# 第三部分：可视化年龄分布
# =================================
def visualize_age_distribution(df, save_path='age_distribution.png'):
    """可视化年龄分布并保存结果"""
    print("\n===== 可视化年龄分布 =====")
    
    # 设置图表风格
    plt.style.use('tableau-colorblind10')
    plt.figure(figsize=(12, 8))
    
    # 1. 创建子图布局
    ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
    ax2 = plt.subplot2grid((2, 2), (1, 0))
    ax3 = plt.subplot2grid((2, 2), (1, 1))
    
    # 2. 主图：年龄直方图 + KDE
    sns.histplot(df['Age'], bins=30, kde=True, color='skyblue', ax=ax1)
    ax1.set_title('乘客年龄分布', fontsize=14, fontweight='bold')
    ax1.set_xlabel('年龄', fontsize=12)
    ax1.set_ylabel('乘客数量', fontsize=12)
    ax1.axvline(df['Age'].mean(), color='red', linestyle='--', label=f'平均年龄: {df["Age"].mean():.1f}岁')
    ax1.axvline(df['Age'].median(), color='green', linestyle='--', label=f'中位年龄: {df["Age"].median():.1f}岁')
    ax1.legend()
    
    # 3. 子图1：按性别分组箱线图
    sns.boxplot(x='Sex', y='Age', data=df, palette='pastel', ax=ax2)
    ax2.set_title('性别年龄分布比较', fontsize=12)
    ax2.set_xlabel('性别', fontsize=10)
    ax2.set_ylabel('年龄', fontsize=10)
    
    # 4. 子图2：按年龄分组统计
    age_group_counts = df['AgeGroup'].value_counts().sort_index()
    colors = plt.cm.Pastel1(range(len(age_group_counts)))
    age_group_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax3, colors=colors, 
                         textprops={'fontsize': 9}, startangle=90)
    ax3.set_title('乘客年龄段分布', fontsize=12)
    ax3.set_ylabel('')  # 隐藏默认的ylabel
    
    # 5. 添加整体标题
    plt.suptitle('泰坦尼克号乘客年龄分析', fontsize=16, fontweight='bold', y=0.95)
    
    # 6. 调整布局并保存
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # 为总标题留空间
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"图表已保存至: {save_path}")
    
    # 显示图表
    plt.show()
    
    # 7. 返回统计信息
    age_stats = {
        'mean': df['Age'].mean(),
        'median': df['Age'].median(),
        'std': df['Age'].std(),
        'min': df['Age'].min(),
        'max': df['Age'].max()
    }
    print("\n年龄统计摘要:")
    for stat, value in age_stats.items():
        print(f"{stat}: {value:.2f}")
    
    return age_stats

# 执行可视化
age_stats = visualize_age_distribution(df)

# =================================
# 第四部分：分析年龄与其他因素的关系
# =================================
def analyze_age_relationships(df):
    """分析年龄与其他因素的关系"""
    print("\n===== 年龄与其他因素的关系分析 =====")
    
    # 1. 年龄与票价的关系
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Age', y='Fare', data=df, hue='Sex', palette='viridis', alpha=0.7)
    plt.title('年龄与票价的关系', fontsize=14)
    plt.xlabel('年龄', fontsize=12)
    plt.ylabel('票价', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.savefig('age_vs_fare.png', dpi=120)
    print("年龄与票价关系图已保存")
    
    # 2. 年龄与舱位等级的关系
    plt.figure(figsize=(10, 6))
    sns.violinplot(x='Pclass', y='Age', data=df, palette='Set2', inner='quartile')
    plt.title('不同舱位等级的年龄分布', fontsize=14)
    plt.xlabel('舱位等级', fontsize=12)
    plt.ylabel('年龄', fontsize=12)
    plt.savefig('age_vs_class.png', dpi=120)
    print("年龄与舱位等级关系图已保存")
    
    # 3. 年龄与生存率的关系
    df['SurvivedLabel'] = df['Survived'].map({0: '未幸存', 1: '幸存'})
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='SurvivedLabel', y='Age', data=df, palette='Set3')
    plt.title('幸存者与未幸存者的年龄分布', fontsize=14)
    plt.xlabel('生存状态', fontsize=12)
    plt.ylabel('年龄', fontsize=12)
    plt.savefig('age_vs_survival.png', dpi=120)
    print("年龄与生存率关系图已保存")
    
    # 4. 年龄分组与生存率
    survival_rate_by_age = df.groupby('AgeGroup')['Survived'].mean().reset_index()
    survival_rate_by_age.columns = ['AgeGroup', 'SurvivalRate']
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='AgeGroup', y='SurvivalRate', data=survival_rate_by_age, palette='coolwarm')
    plt.title('不同年龄段生存率', fontsize=14)
    plt.xlabel('年龄段', fontsize=12)
    plt.ylabel('生存率', fontsize=12)
    plt.ylim(0, 1)
    plt.savefig('survival_by_age_group.png', dpi=120)
    print("年龄段生存率图已保存")
    
    # 5. 返回分析结果
    return {
        'corr_age_fare': df[['Age', 'Fare']].corr().iloc[0, 1],
        'mean_age_by_class': df.groupby('Pclass')['Age'].mean().to_dict(),
        'survival_rate_by_age_group': survival_rate_by_age.set_index('AgeGroup')['SurvivalRate'].to_dict()
    }

# 执行关系分析
relationship_results = analyze_age_relationships(df)

# 打印最终结果摘要
print("\n===== 分析结果摘要 =====")
print(f"年龄与票价相关性: {relationship_results['corr_age_fare']:.3f}")
print("不同舱位等级的平均年龄:")
for pclass, age in relationship_results['mean_age_by_class'].items():
    print(f"  {pclass}等舱: {age:.1f}岁")
print("\n不同年龄段生存率:")
for age_group, rate in relationship_results['survival_rate_by_age_group'].items():
    print(f"  {age_group}: {rate:.2%}")