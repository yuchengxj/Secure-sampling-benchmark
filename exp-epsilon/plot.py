import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.gridspec as gridspec

plt.rcParams['font.size'] = 30  # 默认为15
plt.rcParams['axes.titlesize'] = 30  # 默认为大于font.size
plt.rcParams['axes.labelsize'] = 30  # 默认为font.size
plt.rcParams['xtick.labelsize'] = 28  # 默认为font.size
plt.rcParams['ytick.labelsize'] = 28  # 默认为font.size
plt.rcParams['legend.fontsize'] = 20

colors = [
    (75/255, 102/255, 173/255), (98/255, 190/255, 166/255),
    (235/255, 96/255, 70/255), (253/255, 186/255, 107/255),
    (163/255, 6/255, 67/255), (239/255, 138/255, 71/255),
    (30/255, 70/255, 110/255), (82/255, 143/255, 173/255)
]
line_styles = {
    0: ('ODO-Laplace', colors[1], 2),
    1: ('Ostack-Laplace', colors[0], 2),
    2: ('Ostack-Laplace*', colors[3], 2),
    3: ('ODO-Gaussian', colors[4], 2),
    4: ('Ostack-Gaussian', colors[6], 2),
    5: ('DNG-Laplace', colors[2], 2),
    6: ('DNG-Gaussian', colors[5], 2),
    7: ('Transform-Laplace', colors[7], 2),
}
color_map = {v[0]: v[1] for k, v in line_styles.items()}

# 文件夹路径
src_dir = "exp-epsilon/raw_data_epsilon/and"

# 获取both目录下的所有csv文件
csv_files = [f for f in os.listdir(src_dir) if f.endswith('.csv')]
csv_files.sort(key=lambda x: [k for k, v in line_styles.items() if v[0] == x.replace('.csv', '')][0])

# 初始化一个字典，键为CSV文件名，值为读取的DataFrame
dataframes = {}
for file in csv_files:
    filepath = os.path.join(src_dir, file)
    dataframes[file] = pd.read_csv(filepath, index_col=0)

src_dir_new = "exp-epsilon/raw_data_epsilon/bit" # 改为你新数据的目录路径

# 获取新目录下的所有csv文件
csv_files_new = [f for f in os.listdir(src_dir_new) if f.endswith('.csv')]
csv_files_new.sort(key=lambda x: [k for k, v in line_styles.items() if v[0] == x.replace('.csv', '')][0])

# 初始化一个字典，键为CSV文件名，值为读取的DataFrame
dataframes_new = {}
for file in csv_files_new:
    filepath = os.path.join(src_dir_new, file)
    dataframes_new[file] = pd.read_csv(filepath, index_col=0)


# 设置大图的布局
fig = plt.figure(figsize=(30, 12))
gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 0.1])

# 根据数据的行数初始化子图的轴
axes = [fig.add_subplot(gs[i]) for i in range(4)]

df = dataframes[csv_files[0]]

def format_label(value):
    if value == 0:
        return "0"
    exponent = int(np.log10(abs(value)))
    mantissa = value / (10**exponent)
    return f"{mantissa:.1f}e{exponent}"

# 对于数据的每一行，创建一个子图
for row, ax in zip(dataframes[csv_files[0]].index, axes):
    # 存储每个文件中相应行的数据
    row_data = []
    row_data_new = []
    
    for file in csv_files:  # 这里我们遍历已排序的文件列表
        row_data.append(dataframes[file].loc[row])
        row_data_new.append(dataframes_new[file].loc[row])

    # 转换为DataFrame以便于绘图
    df_row_data = pd.DataFrame(row_data, columns=df.columns, index=csv_files)
    df_row_data_new = pd.DataFrame(row_data_new, columns=df.columns, index=csv_files_new)

    df_row_data_new += df_row_data
    # 绘制原始数据
    bars = df_row_data.transpose().plot(kind='bar', ax=ax, legend=False, zorder=3, color=[color_map[file.replace('.csv', '')] for file in csv_files], edgecolor='black', width=0.8)
    bars = df_row_data_new.transpose().plot(kind='bar', ax=ax, legend=False, zorder=2, color=[color_map[file.replace('.csv', '')] for file in csv_files],  hatch="//", edgecolor='black', width=0.8)

    ax.tick_params(axis='x', rotation=0)

    ax.set_facecolor('#eaeaf2')
    ax.grid(color='white', zorder=2)
    ax.set_title(f'$\lambda={row}$')
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_xlabel(f'Privacy Budget $\epsilon$')
    # if (row / 64) % 2 == 1:
    #     ax.set_ylabel('AND gates + random bits')
    ax.set_yscale('log', base=10)


ax_leg = fig.add_subplot(gs[-1, :])  # Make legend span both columns
ax_leg.axis('off')
custom_handles = [plt.Line2D([0], [0], color=value[1], lw=4) for key, value in line_styles.items()]
legend = ax_leg.legend(custom_handles, [value[0] for key, value in line_styles.items()], loc='center', ncol=len(dataframes))
legend.get_frame().set_facecolor('#eaeaf2')

plt.tight_layout()
plt.savefig('exp-epsilon/plots/combined_fig.png', format='png')
plt.savefig('exp-epsilon/plots/combined_fig.eps', format='eps')