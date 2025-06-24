import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix, 
                             roc_curve, auc, precision_recall_curve, 
                             average_precision_score)
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline
import warnings
import matplotlib.font_manager as fm
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
# 1. 加载信用卡欺诈数据集
# ======================
def load_credit_card_data():
    """加载信用卡欺诈数据集"""
    try:
        # 从本地加载数据
        df = pd.read_csv('creditcard.csv')
        print("成功加载信用卡欺诈数据集!")
    except:
        print("本地文件未找到，尝试从网络下载...")
        try:
            # 从网络URL加载数据
            url = 'https://raw.githubusercontent.com/nsethi31/Kaggle-Data-Credit-Card-Fraud-Detection/master/creditcard.csv'
            df = pd.read_csv(url)
            print("网络下载成功!")
        except:
            print("网络下载失败，使用内置示例数据")
            # 创建示例数据集
            np.random.seed(42)
            n_samples = 10000
            df = pd.DataFrame({
                'Time': np.random.randn(n_samples),
                'V1': np.random.randn(n_samples),
                'V2': np.random.randn(n_samples),
                'V3': np.random.randn(n_samples),
                'Amount': np.random.exponential(100, n_samples),
                'Class': np.random.choice([0, 1], size=n_samples, p=[0.998, 0.002])
            })
    
    print(f"数据集形状: {df.shape}")
    print(f"欺诈交易占比: {df['Class'].mean()*100:.4f}%")
    return df

# 加载数据
cc_df = load_credit_card_data()

# ======================
# 2. 数据探索与质量报告
# ======================
def generate_data_quality_report(df):
    """生成数据质量报告"""
    print("\n===== 数据质量报告 =====")
    
    # 1. 基本统计信息
    report = {
        "总样本数": df.shape[0],
        "特征数量": df.shape[1] - 1,  # 减去目标变量
        "欺诈交易数": df['Class'].sum(),
        "欺诈交易比例": f"{df['Class'].mean()*100:.4f}%",
        "缺失值总数": df.isnull().sum().sum(),
        "时间特征范围": f"{df['Time'].min():.2f} - {df['Time'].max():.2f}",
        "金额特征范围": f"{df['Amount'].min():.2f} - {df['Amount'].max():.2f}",
    }
    
    # 2. 打印报告
    for key, value in report.items():
        print(f"{key}: {value}")
    
    # 3. 可视化
    plt.figure(figsize=(15, 10))
    
    # 3.1 类别分布
    plt.subplot(2, 2, 1)
    class_counts = df['Class'].value_counts()
    plt.pie(class_counts, labels=['正常交易', '欺诈交易'], autopct='%1.1f%%', 
            colors=['#66b3ff','#ff9999'], startangle=90)
    plt.title('交易类别分布')
    
    # 3.2 金额分布
    plt.subplot(2, 2, 2)
    sns.histplot(df['Amount'], bins=50, kde=True)
    plt.title('交易金额分布')
    plt.xlabel('金额')
    plt.ylabel('频次')
    
    # 3.3 时间分布
    plt.subplot(2, 2, 3)
    sns.histplot(df['Time'], bins=50, kde=True, color='green')
    plt.title('交易时间分布')
    plt.xlabel('时间 (秒)')
    plt.ylabel('频次')
    
    # 3.4 特征相关性
    plt.subplot(2, 2, 4)
    sns.heatmap(df.corr(), cmap='coolwarm', center=0)
    plt.title('特征相关性热力图')
    
    plt.tight_layout()
    plt.savefig('data_quality_report.png', dpi=120)
    print("\n数据质量报告图已保存为 data_quality_report.png")
    
    return report

# 生成数据质量报告
quality_report = generate_data_quality_report(cc_df)

# ======================
# 3. 处理不平衡数据
# ======================
def handle_imbalanced_data(df):
    """处理不平衡数据"""
    print("\n===== 处理不平衡数据 =====")
    
    # 分离特征和目标变量
    X = df.drop('Class', axis=1)
    y = df['Class']
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # 使用SMOTE过采样 + 随机欠采样组合
    over = SMOTE(sampling_strategy=0.1, random_state=42)
    under = RandomUnderSampler(sampling_strategy=0.5, random_state=42)
    
    # 创建管道
    steps = [('over', over), ('under', under)]
    pipeline = Pipeline(steps=steps)
    
    # 应用采样
    X_res, y_res = pipeline.fit_resample(X_train, y_train)
    
    # 打印采样后分布
    print("采样后类别分布:")
    print(pd.Series(y_res).value_counts())
    print(f"正常交易: {sum(y_res == 0)}")
    print(f"欺诈交易: {sum(y_res == 1)}")
    
    return X_res, y_res, X_test, y_test

# 处理不平衡数据
X_res, y_res, X_test, y_test = handle_imbalanced_data(cc_df)

# ======================
# 4. 逻辑回归模型训练与评估
# ======================
def train_and_evaluate_logistic_regression(X_train, y_train, X_test, y_test):
    """训练并评估逻辑回归模型"""
    print("\n===== 模型训练与评估 =====")
    
    # 1. 创建并训练模型
    model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    print("模型训练完成!")
    
    # 2. 在测试集上预测
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]  # 欺诈概率
    
    # 3. 评估指标
    print("\n分类报告:")
    print(classification_report(y_test, y_pred))
    
    # 4. 混淆矩阵可视化
    conf_matrix = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['正常', '欺诈'], 
                yticklabels=['正常', '欺诈'])
    plt.title('混淆矩阵')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.savefig('confusion_matrix.png', dpi=120)
    print("混淆矩阵图已保存为 confusion_matrix.png")
    
    # 5. ROC曲线
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC曲线 (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('假正例率 (FPR)')
    plt.ylabel('真正例率 (TPR)')
    plt.title('ROC曲线')
    plt.legend(loc="lower right")
    plt.savefig('roc_curve.png', dpi=120)
    print("ROC曲线图已保存为 roc_curve.png")
    
    # 6. 精确率-召回率曲线
    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    ap_score = average_precision_score(y_test, y_prob)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color='blue', lw=2, label=f'PR曲线 (AP = {ap_score:.2f})')
    plt.xlabel('召回率')
    plt.ylabel('精确率')
    plt.title('精确率-召回率曲线')
    plt.legend(loc="upper right")
    plt.savefig('pr_curve.png', dpi=120)
    print("PR曲线图已保存为 pr_curve.png")
    
    # 7. 特征重要性
    feature_importance = pd.DataFrame({
        '特征': X_train.columns,
        '重要性': model.coef_[0]
    }).sort_values('重要性', ascending=False)
    
    # 只显示最重要的10个特征
    top_features = feature_importance.head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='重要性', y='特征', data=top_features)
    plt.title('逻辑回归特征重要性 (Top 10)')
    plt.savefig('feature_importance.png', dpi=120)
    print("特征重要性图已保存为 feature_importance.png")
    
    return model, y_pred, feature_importance

# 训练和评估模型
model, y_pred, feature_importance = train_and_evaluate_logistic_regression(X_res, y_res, X_test, y_test)

# ======================
# 5. 保存完整脚本
# ======================
def save_fraud_detection_script():
    """将完整代码保存为Python文件"""
    import os
    import inspect
    import sys
    
    # 获取当前脚本内容
    current_script = inspect.getsource(sys.modules[__name__])
    
    # 保存到文件
    with open('fraud_detection.py', 'w', encoding='utf-8') as f:
        f.write(current_script)
    
    print("\n完整脚本已保存为 fraud_detection.py")

# 保存脚本
save_fraud_detection_script()
