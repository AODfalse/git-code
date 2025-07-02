# 欺诈检测阈值优化 - 修正版
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split  # 添加缺失的导入
from sklearn.metrics import precision_recall_curve, f1_score, confusion_matrix, classification_report
from sklearn.datasets import make_classification
import pandas as pd
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
# 生成示例数据（实际使用时替换为您的数据集）
# 加载信用卡欺诈数据集
data = pd.read_csv('creditcard.csv')

# 分离特征和目标变量
X = data.drop('Class', axis=1).values
y = data['Class'].values

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 训练模型
model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

# 获取预测概率
y_proba = model.predict_proba(X_test)[:, 1]

# 阈值优化分析
precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)

# 找到最佳F1分数对应的阈值
best_idx = np.argmax(f1_scores[:-1])  # 注意：f1_scores长度比thresholds多1
best_threshold = thresholds[best_idx]
best_f1 = f1_scores[best_idx]

# 结果可视化
plt.figure(figsize=(12, 6))

# 第一张图：阈值优化曲线
plt.subplot(1, 2, 1)
plt.plot(thresholds, precisions[:-1], "b--", label="Precision")
plt.plot(thresholds, recalls[:-1], "g-", label="Recall")
plt.plot(thresholds, f1_scores[:-1], "r-", label="F1")
plt.axvline(x=best_threshold, color='k', linestyle='--', label=f'Best Threshold ({best_threshold:.2f})')
plt.xlabel("Threshold")
plt.ylabel("Score")
plt.legend(loc="best")
plt.title("Threshold Optimization")
plt.grid(True)

# 第二张图：混淆矩阵比较
plt.subplot(1, 2, 2)
y_pred_best = (y_proba >= best_threshold).astype(int)
cm = confusion_matrix(y_test, y_pred_best)

plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title(f"Confusion Matrix (Threshold={best_threshold:.2f})")
plt.colorbar()
plt.xticks([0,1], ['Legit', 'Fraud'])
plt.yticks([0,1], ['Legit', 'Fraud'])

for i in range(2):
    for j in range(2):
        plt.text(j, i, format(cm[i, j], 'd'),
                 horizontalalignment="center",
                 verticalalignment="center",
                 color="white" if cm[i, j] > cm.max()/2 else "black")

plt.tight_layout()
plt.savefig('threshold_optimization.png')
plt.show()

# 生成优化报告
print(f"\n{'='*40}")
print(f"最佳阈值: {best_threshold:.4f}")
print(f"最佳F1分数: {best_f1:.4f}")
print(f"{'='*40}\n")

# 使用最佳阈值的分类报告
print("优化后的分类报告:")
print(classification_report(y_test, y_pred_best))

# 对比默认阈值0.5的性能
print("\n默认阈值(0.5)的分类报告:")
y_pred_default = (y_proba >= 0.5).astype(int)
print(classification_report(y_test, y_pred_default))

# 保存优化结果
with open('threshold_optimization_report.txt', 'w') as f:
    f.write(f"最佳阈值: {best_threshold:.4f}\n")
    f.write(f"最佳F1分数: {best_f1:.4f}\n\n")
    f.write("优化后的分类报告:\n")
    f.write(classification_report(y_test, y_pred_best))
    f.write("\n默认阈值(0.5)的分类报告:\n")
    f.write(classification_report(y_test, y_pred_default))

print("优化报告已保存为 'threshold_optimization_report.txt'")