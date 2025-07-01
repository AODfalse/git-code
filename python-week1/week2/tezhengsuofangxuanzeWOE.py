import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.datasets import load_breast_cancer

# 加载数据
data = load_breast_cancer()
X = data.data
y = data.target
feature_names = data.feature_names

# 选择两个特征进行可视化
feature1 = 0  # 'mean radius'
feature2 = 1  # 'mean texture'

# 原始数据
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.scatter(X[:, feature1], X[:, feature2], c=y, cmap='coolwarm')
plt.title('Original Data')
plt.xlabel(feature_names[feature1])
plt.ylabel(feature_names[feature2])

# StandardScaler
scaler_std = StandardScaler()
X_std = scaler_std.fit_transform(X)
plt.subplot(1, 3, 2)
plt.scatter(X_std[:, feature1], X_std[:, feature2], c=y, cmap='coolwarm')
plt.title('StandardScaler')
plt.xlabel(feature_names[feature1])
plt.ylabel(feature_names[feature2])

# MinMaxScaler
scaler_minmax = MinMaxScaler()
X_minmax = scaler_minmax.fit_transform(X)
plt.subplot(1, 3, 3)
plt.scatter(X_minmax[:, feature1], X_minmax[:, feature2], c=y, cmap='coolwarm')
plt.title('MinMaxScaler')
plt.xlabel(feature_names[feature1])
plt.ylabel(feature_names[feature2])

plt.tight_layout()
plt.savefig('scaling_comparison.png')  # 保存缩放效果对比图
plt.show()

from sklearn.feature_selection import SelectKBest, RFE, f_classif
from sklearn.ensemble import RandomForestClassifier

# 创建DataFrame便于查看
df = pd.DataFrame(X, columns=feature_names)

# SelectKBest
selector_kbest = SelectKBest(score_func=f_classif, k=10)
X_kbest = selector_kbest.fit_transform(X, y)
selected_features_kbest = df.columns[selector_kbest.get_support()]
scores_kbest = selector_kbest.scores_

print("SelectKBest选出的特征:", selected_features_kbest)
print("特征得分:", sorted(zip(feature_names, scores_kbest), key=lambda x: x[1], reverse=True))

# RFE (递归特征消除)
estimator = RandomForestClassifier(random_state=42)
selector_rfe = RFE(estimator, n_features_to_select=10, step=1)
X_rfe = selector_rfe.fit_transform(X, y)
selected_features_rfe = df.columns[selector_rfe.get_support()]
ranking_rfe = selector_rfe.ranking_

print("\nRFE选出的特征:", selected_features_rfe)
print("特征排名:", sorted(zip(feature_names, ranking_rfe), key=lambda x: x[1]))

# 可视化特征重要性
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.barh(feature_names, scores_kbest)
plt.title('SelectKBest Feature Scores')

plt.subplot(1, 2, 2)
plt.barh(feature_names, ranking_rfe)
plt.title('RFE Feature Rankings')
plt.tight_layout()
plt.savefig('feature_selection.png')  # 保存特征重要性排序图
plt.show()


from sklearn.preprocessing import KBinsDiscretizer
from scipy import stats
import numpy as np

# 创建示例数据 (年龄和收入)
np.random.seed(42)
age = np.random.randint(18, 70, size=500)
income = np.random.exponential(scale=50000, size=500).astype(int) + 20000
target = np.random.binomial(1, 0.3 + age/200 - income/1000000, size=500)

# 创建DataFrame
df = pd.DataFrame({'age': age, 'income': income, 'target': target})

# 等宽分箱
df['age_bin_eqw'] = pd.cut(df['age'], bins=5, labels=False)
df['income_bin_eqw'] = pd.cut(df['income'], bins=5, labels=False)

# 等频分箱
df['age_bin_eqf'] = pd.qcut(df['age'], q=5, labels=False, duplicates='drop')
df['income_bin_eqf'] = pd.qcut(df['income'], q=5, labels=False, duplicates='drop')

# WOE (Weight of Evidence) 编码
def woe_encoding(df, feature, target):
    total_good = df[target].sum()
    total_bad = len(df) - total_good
    
    woe_dict = {}
    iv = 0
    
    for category in df[feature].unique():
        good = df[(df[feature] == category) & (df[target] == 1)].shape[0]
        bad = df[(df[feature] == category) & (df[target] == 0)].shape[0]
        
        # 避免除以0
        good = max(good, 0.5)
        bad = max(bad, 0.5)
        
        p_good = good / total_good
        p_bad = bad / total_bad
        
        woe = np.log(p_good / p_bad)
        woe_dict[category] = woe
        
        iv += (p_good - p_bad) * woe
    
    df[f'{feature}_woe'] = df[feature].map(woe_dict)
    return df, iv

# 对等频分箱后的年龄进行WOE编码
df, iv_age = woe_encoding(df, 'age_bin_eqf', 'target')
print(f"Age IV (Information Value): {iv_age:.4f}")

# 对等频分箱后的收入进行WOE编码
df, iv_income = woe_encoding(df, 'income_bin_eqf', 'target')
print(f"Income IV: {iv_income:.4f}")

# 可视化分箱效果
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.hist(df['age'], bins=20)
plt.title('Original Age Distribution')

plt.subplot(1, 3, 2)
df['age_bin_eqf'].value_counts().sort_index().plot(kind='bar')
plt.title('Age Equal Frequency Binning')

plt.subplot(1, 3, 3)
df.groupby('age_bin_eqf')['age'].mean().plot(kind='bar')
plt.title('Mean Age per Bin')

plt.tight_layout()
plt.savefig('binning_example.png')  # 保存分箱效果图
plt.show()

# 保存分箱后的数据集
df.to_csv('binned_dataset.csv', index=False)
