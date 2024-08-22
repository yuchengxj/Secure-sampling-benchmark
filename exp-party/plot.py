import os
import re
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

plt.rcParams['font.size'] = 32  # 默认为15
plt.rcParams['axes.titlesize'] = 32  # 默认为大于font.size
plt.rcParams['axes.labelsize'] = 32  # 默认为font.size
plt.rcParams['xtick.labelsize'] = 30  # 默认为font.size
plt.rcParams['ytick.labelsize'] = 30  # 默认为font.size
plt.rcParams['legend.fontsize'] = 23

colors = [
    (75/255, 102/255, 173/255), (98/255, 190/255, 166/255),
    (235/255, 96/255, 70/255), (253/255, 186/255, 107/255),
    (163/255, 6/255, 67/255), (239/255, 138/255, 71/255),
    (30/255, 70/255, 110/255), (82/255, 143/255, 173/255)
]
line_styles = {
    'direct_lap.log': ('ODO-Laplace', colors[1], 2),
    'ostack_lap.log': ('Ostack-Laplace', colors[0], 2),
    'periodic_lap.log': ('Ostack-Laplace*', colors[3], 2),
    'direct_gauss.log': ('ODO-Gaussian', colors[4], 2),
    'ostack_gauss.log': ('Ostack-Gaussian', colors[6], 2),
    'dng_lap.log': ('DNG-Laplace', colors[2], 2),
    'dng_gauss.log': ('DNG-Gaussian', colors[5], 2),
}


base_dir = 'exp-party'
subdirs = ['logs-yao', 'logs-bmr', 'logs-bmr-4', 'logs-bmr-5', 'logs-bmr-6', 'logs-bmr-7', 'logs-bmr-8']
subdirs_dic = {'logs-yao':'2', 'logs-bmr':'3', 'logs-bmr-4':'4', 'logs-bmr-5':'5', 'logs-bmr-6':'6', 'logs-bmr-7':'7'}

log_files = ['direct_lap.log', 'ostack_lap.log', 'periodic_lap.log', 'dng_lap.log', 'direct_gauss.log', 'ostack_gauss.log', 'dng_gauss.log', ]

time_data = {log: [] for log in log_files}
data_sent_data = {log: [] for log in log_files}

for log_file in log_files:
    for subdir in subdirs:
        with open(os.path.join(base_dir, subdir, log_file), 'r') as f:
            content = f.read()
            
            pattern = re.compile(r'Running with n=4096 and lambd=128.*?Global data sent = ([\d\.]+(?:[eE][-+]?\d+)?).*?Time = ([\d\.]+) seconds', re.DOTALL)

            match = pattern.search(content)

            if match:
                global_data_sent = float(match.group(1))
                time_value = float(match.group(2))
                
                data_sent_data[log_file].append(global_data_sent)
                time_data[log_file].append(time_value)
            else:
                data_sent_data[log_file].append(0)  # 未找到则设为0
                time_data[log_file].append(0)  # 未找到则设为0

df_time = pd.DataFrame(time_data, index=subdirs)
df_data_sent = pd.DataFrame(data_sent_data, index=subdirs)

fig = plt.figure(figsize=(18, 15))
gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 0.2])
axs = [fig.add_subplot(gs[i]) for i in range(2)]

dataframes = [df_time, df_data_sent]
y_labels = ['time (s)', 'communication (MB)']
width = 0.1
gap = 0  # gap between bars for different log_files

for ax, df, y_label in zip(axs, dataframes, y_labels):
    for idx, log_file in enumerate(log_files):
        label, color, _ = line_styles[log_file]
        ax.bar(
            [x + idx*(width + gap) for x in range(len(subdirs))], 
            df[log_file], 
            width=width, 
            label=label,
            color=color,
            zorder=3,
            edgecolor='black',
            # hatch="//",
        )

    ax.set_xlabel('Number of computing parties')
    ax.set_ylabel(y_label)
    ax.set_xticks([x + (len(log_files) - 1)*(width + gap)/2 for x in range(len(subdirs))])  # center x ticks
    ax.set_xticklabels([2, 3, 4, 5, 6, 7, 8], rotation=0)
    # ax.legend(loc='upper left', bbox_to_anchor=(1,1))
    ax.set_yscale('log', base=10)
    ax.set_facecolor('#eaeaf2')
    ax.grid(color='white', zorder=2)
    for spine in ax.spines.values():
        spine.set_visible(False)

ax_leg = fig.add_subplot(gs[-1, :])  # Make legend span both columns
ax_leg.axis('off')
custom_handles = [plt.Line2D([0], [0], color=value[1], lw=4) for key, value in line_styles.items()]
legend = ax_leg.legend(custom_handles, [value[0] for key, value in line_styles.items()], loc='center', ncol=4)
legend.get_frame().set_facecolor('#eaeaf2')

plt.tight_layout()
plt.savefig('exp-party/time_com_party.png', format='png')
plt.savefig('exp-party/time_com_party.eps', format='eps')
