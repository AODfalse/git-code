import os
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm  # 导入字体管理模块
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 要比较的样式
styles = [
'Solarize_Light2', '_classic_test_patch', '_mpl-gallery', '_mpl-gallery-nogrid', 'bmh', 'classic', 'dark_background', 'fast', 'fivethirtyeight', 'ggplot', 'grayscale', 'petroff10', 'seaborn-v0_8', 'seaborn-v0_8-bright', 'seaborn-v0_8-colorblind', 'seaborn-v0_8-dark', 'seaborn-v0_8-dark-palette', 'seaborn-v0_8-darkgrid', 'seaborn-v0_8-deep', 'seaborn-v0_8-muted', 'seaborn-v0_8-notebook', 'seaborn-v0_8-paper', 'seaborn-v0_8-pastel', 'seaborn-v0_8-poster', 'seaborn-v0_8-talk', 'seaborn-v0_8-ticks', 'seaborn-v0_8-white', 'seaborn-v0_8-whitegrid', 'tableau-colorblind10'
]

# 创建比较图表
fig, axs = plt.subplots(15, 2, figsize=(10, 12))

for i, style in enumerate(styles):
    plt.style.use(style)
    ax = axs[i//2, i%2]
    
    # 绘制示例图表
    ax.plot(x, y, label='sin(x)')
    ax.scatter(x[::10], y[::10], color='red', label='采样点')
    ax.set_title(f'Style: {style}', fontsize=10)
    ax.set_xlabel('X轴')
    ax.set_ylabel('Y轴')
    ax.legend()
    ax.grid(True)

plt.suptitle('Matplotlib 样式比较', fontsize=16)
plt.savefig('style_comparison.png', dpi=120)
plt.show()