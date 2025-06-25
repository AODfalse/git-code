import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns

# 示例数据
y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 0])
y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 0])

# 计算混淆矩阵
cm = confusion_matrix(y_true, y_pred)

# 可视化混淆矩阵
plt.figure(figsize=(6, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Predicted 0', 'Predicted 1'],
            yticklabels=['Actual 0', 'Actual 1'])
plt.title('Confusion Matrix')
plt.show()

# 自定义评估函数
def custom_metrics(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) != 0 else 0
    recall = tp / (tp + fn) if (tp + fn) != 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'false_positive_rate': fp / (fp + tn) if (fp + tn) != 0 else 0,
        'false_negative_rate': fn / (fn + tp) if (fn + tp) != 0 else 0
    }

# 使用自定义评估函数
metrics = custom_metrics(y_true, y_pred)
print("Custom Metrics:")
for k, v in metrics.items():
    print(f"{k}: {v:.4f}")

# 对比sklearn的分类报告
print("\nClassification Report:")
print(classification_report(y_true, y_pred))

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score, auc

# 生成示例数据
X, y = make_classification(n_samples=1000, n_classes=2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 训练模型
model = LogisticRegression()
model.fit(X_train, y_train)

# 预测概率
y_scores = model.predict_proba(X_test)[:, 1]

# 计算ROC曲线
fpr, tpr, thresholds = roc_curve(y_test, y_scores)
roc_auc = auc(fpr, tpr)

# 绘制ROC曲线
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()

# 计算AUC值
print(f"AUC Score: {roc_auc_score(y_test, y_scores):.4f}")

# 多类别ROC曲线示例
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC

# 生成多类数据
X, y = make_classification(n_samples=1000, n_classes=3, n_informative=3, random_state=42)
y = label_binarize(y, classes=[0, 1, 2])
n_classes = y.shape[1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 训练模型
classifier = OneVsRestClassifier(SVC(probability=True, random_state=42))
classifier.fit(X_train, y_train)
y_score = classifier.predict_proba(X_test)

# 计算每个类的ROC曲线和AUC
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# 绘制多类ROC曲线
plt.figure(figsize=(8, 6))
colors = ['blue', 'red', 'green']
for i, color in zip(range(n_classes), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label=f'Class {i} (AUC = {roc_auc[i]:.2f})')

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Multi-class ROC Curve')
plt.legend(loc="lower right")
plt.show()

from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

# 加载数据
iris = load_iris()
X, y = iris.data, iris.target

# 基础交叉验证
rf = RandomForestClassifier(random_state=42)
cv_scores = cross_val_score(rf, X, y, cv=5, scoring='accuracy')

print("Basic Cross-Validation Scores:", cv_scores)
print(f"Mean CV Accuracy: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores):.4f})")

# 使用不同的交叉验证策略
kf = KFold(n_splits=5, shuffle=True, random_state=42)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

kf_scores = cross_val_score(rf, X, y, cv=kf, scoring='accuracy')
skf_scores = cross_val_score(rf, X, y, cv=skf, scoring='accuracy')

print("\nKFold CV Scores:", kf_scores)
print(f"Mean KFold Accuracy: {np.mean(kf_scores):.4f}")

print("\nStratifiedKFold CV Scores:", skf_scores)
print(f"Mean StratifiedKFold Accuracy: {np.mean(skf_scores):.4f}")

# 使用交叉验证进行模型选择
svc = SVC(probability=True, random_state=42)
rf = RandomForestClassifier(random_state=42)

svc_scores = cross_val_score(svc, X, y, cv=5, scoring='accuracy')
rf_scores = cross_val_score(rf, X, y, cv=5, scoring='accuracy')

print("\nModel Comparison:")
print(f"SVC Mean Accuracy: {np.mean(svc_scores):.4f}")
print(f"Random Forest Mean Accuracy: {np.mean(rf_scores):.4f}")

# 使用GridSearchCV进行超参数调优
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 5, 10],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(RandomForestClassifier(random_state=42),
                          param_grid=param_grid,
                          cv=5,
                          scoring='accuracy',
                          n_jobs=-1)

grid_search.fit(X, y)

print("\nGrid Search Results:")
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best CV Accuracy: {grid_search.best_score_:.4f}")

# 生成模型优化报告
best_model = grid_search.best_estimator_
final_scores = cross_val_score(best_model, X, y, cv=5, scoring='accuracy')

print("\nOptimized Model Report:")
print(f"Final CV Scores: {final_scores}")
print(f"Mean Accuracy: {np.mean(final_scores):.4f} (+/- {np.std(final_scores):.4f})")
print(f"Best Model Parameters: {best_model.get_params()}")