import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
file_path = r"E:\downlaod\git-code\python-week1\titanic_subset.csv"
# ===== 数据加载 =====
# 从网络加载精简数据集（100行）
#url = "https://gist.githubusercontent.com/yourname/raw/titanic_subset.csv"
if not os.path.exists(file_path):
    print("正在下载数据集...")    
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    response = requests.get(url)
    with open("titanic_subset.csv", "wb") as f:
        f.write(response.content)
    print("数据集下载完成!")

# ===== 数据加载 =====
try:
    # 添加错误处理
    df = pd.read_csv(file_path)
    print("数据集加载成功!")
except Exception as e:
    print(f"文件加载失败: {e}")
    print("当前目录:", os.getcwd())
    print("目录内容:", os.listdir())
    exit()
df = pd.read_csv(file_path)  # 假设数据集已下载到本地

# ===== 数据探索 =====
print("===== 原始数据预览 =====")
print(df) # 显示前5行
print("\n数据形状:", df.shape)
print("\n缺失值统计:")
print(df.isnull().sum())

# 检查原缺失行的年龄值
original_missing = df[df['Age'].isnull()].index
print("原缺失年龄的乘客现年龄值:")
print(df.loc[original_missing, ['Name', 'Age']])

print("年龄分布统计:")
print(df['Age'].describe())

# ===== 缺失值处理 =====
# 任务1：用中位数填充年龄缺失值
# TODO → 计算年龄中位数并填充
#median_age = df['Age'].median()  # 计算中位数
#df['Age'] = df['Age'].fillna(median_age)   # 填充缺失值

# 任务2：用众数填充登船港口缺失值
# TODO → 找到Embarked列最常见的值
#embarked_mode = df['Embarked'].mode()[0]  # 计算众数
#df['Embarked'] = df['Embarked'].fillna(embarked_mode) # 填充缺失值

# 挑战1：按性别分组填充年龄
print("按性别分组填充年龄:")
male_median = df[df['Sex']=='male']['Age'].median()
female_median = df[df['Sex']=='female']['Age'].median()
df.loc[(df['Sex']=='male') & (df['Age'].isnull()), 'Age'] = male_median
df.loc[(df['Sex']=='female') & (df['Age'].isnull()), 'Age'] = female_median
print("按性别分组填充年龄:end")
# 挑战2：可视化年龄分布
print("可视化年龄分布:")
df['Age'].hist(bins=20)
plt.title('Age Distribution After Cleaning')
plt.savefig('age_distribution.png')
print("可视化年龄分布:end")

# ===== 结果验证 =====
print("\n===== 清洗后数据 =====")
print("年龄缺失值:", df['Age'].isnull().sum())
print("登船港口缺失值:", df['Embarked'].isnull().sum())

# ===== 保存结果 =====
df.to_csv("titanic_clean.csv", index=False)
print("\n清洗后的数据已保存为 titanic_clean.csv")