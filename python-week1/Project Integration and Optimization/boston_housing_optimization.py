# 波士顿房价多项式回归优化 - 修正版
from sklearn.datasets import fetch_california_housing  # 使用加州房价数据集替代
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd

# 加载加州房价数据集
california = fetch_california_housing()
X = pd.DataFrame(california.data, columns=california.feature_names)
y = california.target

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 多项式特征扩展（2次项）
poly = PolynomialFeatures(degree=2, include_bias=False)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# 特征标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_poly)
X_test_scaled = scaler.transform(X_test_poly)

# 使用岭回归（防止过拟合）
model = Ridge(alpha=1.0)
model.fit(X_train_scaled, y_train)

# 评估模型
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"优化后的模型性能:")
print(f"原始特征数量: {X_train.shape[1]}")
print(f"多项式特征数量: {X_train_poly.shape[1]}")
print(f"测试集MSE: {mse:.2f}")
print(f"测试集R²: {r2:.4f}")

# 特征重要性分析
feature_names = poly.get_feature_names_out(california.feature_names)
coef_df = pd.DataFrame({
    'Feature': feature_names,
    'Coefficient': model.coef_
}).sort_values('Coefficient', ascending=False)

print("\n最重要的5个特征:")
print(coef_df.head(5))

# 保存优化后的模型
import joblib
joblib.dump(model, 'optimized_housing_model.pkl')
print("优化后的模型已保存为 'optimized_housing_model.pkl'")