import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

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

# 在原有代码中修改图表保存部分

def save_plot(fig, filename, dpi=120):
    """安全保存图表，避免中文问题"""
    try:
        # 尝试使用PNG格式（支持更好）
        fig.savefig(f"{filename}.png", dpi=dpi, bbox_inches='tight')
        print(f"图表已保存为 {filename}.png")
        
        # 如果需要PDF格式
        # fig.savefig(f"{filename}.pdf", dpi=dpi, bbox_inches='tight')
        # print(f"图表已保存为 {filename}.pdf")
    except Exception as e:
        print(f"保存图表时出错: {e}")
        # 回退方案：保存为SVG格式
        fig.savefig(f"{filename}.svg", format='svg', bbox_inches='tight')
        print(f"图表已保存为 {filename}.svg (SVG格式)")

# ======================
# 2. 加载数据集
# ======================
def load_boston_data():
    """加载波士顿房价数据集"""
    # 由于sklearn移除了boston数据集，我们使用OpenML版本
    boston = fetch_openml(name='boston', version=1, as_frame=True)
    
    # 创建DataFrame
    df = pd.DataFrame(boston.data, columns=boston.feature_names)
    df['PRICE'] = boston.target
    
    print("数据集加载成功!")
    print(f"数据集形状: {df.shape}")
    print("\n前5行数据:")
    print(df.head())
    
    return df

# ======================
# 3. 数据探索报告
# ======================
def explore_data(df):
    """生成数据探索报告"""
    print("\n===== 数据探索报告 =====")
    
    # 创建可视化
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('波士顿房价数据探索', fontsize=16)
    
    # 3.1 目标变量分布
    sns.histplot(df['PRICE'], bins=30, kde=True, ax=axs[0, 0])
    axs[0, 0].set_title('房价分布')
    axs[0, 0].set_xlabel('房价 (千美元)')
    
    # 3.2 关键特征与房价关系
    sns.scatterplot(x='RM', y='PRICE', data=df, ax=axs[0, 1])
    axs[0, 1].set_title('房间数量与房价关系')
    axs[0, 1].set_xlabel('每户平均房间数')
    
    sns.scatterplot(x='LSTAT', y='PRICE', data=df, ax=axs[1, 0])
    axs[1, 0].set_title('低收入人口比例与房价关系')
    axs[1, 0].set_xlabel('低收入人口比例 (%)')
    
    sns.scatterplot(x='PTRATIO', y='PRICE', data=df, ax=axs[1, 1])
    axs[1, 1].set_title('学生-教师比例与房价关系')
    axs[1, 1].set_xlabel('学生-教师比例')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为总标题留空间
    save_plot(fig, 'boston_data_exploration')
    
    return df

# ======================
# 4. 特征工程
# ======================
def preprocess_data(df):
    """数据预处理"""
    print("\n===== 特征工程 =====")
    
    # 1. 分离特征和目标变量
    X = df.drop('PRICE', axis=1)
    y = df['PRICE']
    
    # 2. 特征缩放
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("特征缩放完成!")
    
    # 3. 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    print(f"训练集大小: {X_train.shape[0]} 样本")
    print(f"测试集大小: {X_test.shape[0]} 样本")
    
    return X_train, X_test, y_train, y_test, scaler

# ======================
# 5. 模型训练与评估
# ======================
def train_and_evaluate(X_train, X_test, y_train, y_test):
    """训练并评估线性回归模型"""
    print("\n===== 模型训练与评估 =====")
    
    # 1. 创建并训练模型
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    print(f"截距 (b): {model.intercept_:.2f}")
    
    # 2. 在测试集上评估
    y_pred = model.predict(X_test)
    
    # 3. 计算评估指标
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"均方误差 (MSE): {mse:.2f}")
    print(f"均方根误差 (RMSE): {rmse:.2f}")
    print(f"决定系数 (R²): {r2:.2f}")
    
    # 4. 可视化预测结果
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(y_test, y_pred, alpha=0.6)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    ax.set_title('实际房价 vs 预测房价')
    ax.set_xlabel('实际房价 (千美元)')
    ax.set_ylabel('预测房价 (千美元)')
    ax.grid(True, linestyle='--', alpha=0.3)
    save_plot(fig, 'price_predictions')
    
    # 5. 特征重要性分析
    feature_importance = pd.DataFrame({
        '特征': boston_df.drop('PRICE', axis=1).columns,
        '重要性': model.coef_
    }).sort_values('重要性', ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='重要性', y='特征', data=feature_importance, ax=ax)
    ax.set_title('特征重要性分析')
    save_plot(fig, 'feature_importance')
    
    return model, y_pred, feature_importance

# ======================
# 主程序
# ======================
if __name__ == "__main__":
    # 加载数据
    boston_df = load_boston_data()
    
    # 生成数据探索报告
    boston_df = explore_data(boston_df)
    
    # 执行特征工程
    X_train, X_test, y_train, y_test, scaler = preprocess_data(boston_df)
    
    # 训练和评估模型
    model, y_pred, feature_importance = train_and_evaluate(X_train, X_test, y_train, y_test)
    
    # 打印特征重要性
    print("\n===== 特征重要性排序 =====")
    print(feature_importance)