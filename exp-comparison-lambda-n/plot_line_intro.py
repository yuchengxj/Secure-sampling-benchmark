import re
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

plt.rcParams['font.size'] = 30  
plt.rcParams['axes.titlesize'] = 30  
plt.rcParams['axes.labelsize'] = 30  
plt.rcParams['xtick.labelsize'] = 30  
plt.rcParams['ytick.labelsize'] = 30  
plt.rcParams['legend.fontsize'] = 24

pattern = re.compile(r'Running with n=(\d+) and lambd=(\d+).*?Global data sent = ([\d\.]+(?:[eE][-+]?\d+)?).*?Time = ([\d\.]+) seconds', re.DOTALL)

def extract_data_from_log(file_path):
    with open(file_path, 'r') as f:
        log_content = f.read()
    return pattern.findall(log_content)

output_path = 'exp/plots'
dir = 'exp/logs-bmr'
if not os.path.exists(output_path):
    os.mkdir(output_path)
log_files = ["direct_gauss.log", "direct_lap.log", "dng_gauss.log", "ostack_gauss.log", "ostack_lap.log", "periodic_lap.log", 'dng_lap.log']
log_files = [os.path.join(dir, file) for file in log_files]
data = {}
for file in log_files:
    matches = extract_data_from_log(file)
    for n, lambd, global_data, time in matches:
        lambd, n = int(lambd), int(n)
        if lambd not in data:
            data[lambd] = {}
        if n not in data[lambd]:
            data[lambd][n] = {}
        data[lambd][n][file] = {"global_data": float(global_data), "time": float(time)}

colors = [(75/255, 102/255, 173/255), (98/255, 190/255, 166/255), (235/255, 96/255, 70/255), 
          (253/255, 186/255, 107/255), (163/255, 6/255, 67/255), (239/255, 138/255, 71/255), 
          (30/255, 70/255, 110/255), (82/255, 143/255, 173/255)]

colors = [
    (75/255, 102/255, 173/255),   # Blue
    (98/255, 190/255, 166/255),   # Teal
    (235/255, 96/255, 70/255),    # Red
    (0/255, 149/255, 149/255),    # green
    (163/255, 6/255, 67/255),     # Dark Pink
    (120/255, 70/255, 130/255),   # Purple
    (30/255, 70/255, 110/255),    # Navy
    (82/255, 143/255, 173/255)    # Sky Blue
]

log_files_dict = {
    os.path.join(dir, "direct_lap.log"): ('+--', colors[5], 4, 'ODO-Laplace', 20),
    os.path.join(dir, "ostack_lap.log"): ('^-', colors[0], 4, 'Ostack-Laplace', 20),
    os.path.join(dir, "periodic_lap.log"): ('^-', colors[7], 4, 'Ostack-Laplace*', 20),
    os.path.join(dir, "dng_lap.log"): ('s-', colors[2], 2, 'DNG-Laplace', 10),
    os.path.join(dir, "trans_lap.log"): ('<-', colors[1], 4, 'Trans-Laplace', 20),
    os.path.join(dir, "direct_gauss.log"): ('+-', colors[6], 4, 'ODO-Gaussian', 20),
    os.path.join(dir, "ostack_gauss.log"): ('*-', colors[4], 4, 'Ostack-Gaussian', 20),
    os.path.join(dir, "dng_gauss.log"): ('o-', colors[3], 4, 'DNG-Gaussian', 20),
}

def plot_appendix():
    lambd = 64
    fig = plt.figure(figsize=(32, 6))
    gs = gridspec.GridSpec(1, 3, height_ratios=[1], width_ratios=[2, 2, 2])
    y_map = {'global_data': 'communication (MB)', 'time': 'time (s)', 'and':'AND gates'}
    y_axis = ['time', 'global_data']
    new_log_files = log_files.copy()
    import pickle
    with open('exp/logs-bmr/data-and.pkl', 'rb') as f:
        new_data = pickle.load(f)
    new_log_files.append('exp/logs-bmr/trans_lap.log')
    ax = fig.add_subplot(gs[0, 0])
    for file in new_log_files:
        linestyle, color, linewidth, name, markersize = log_files_dict[file]
        x_values = [4, 6, 8, 10, 12]  # log2 values
        y_values = [new_data[lambd][n][file] for n in [16, 64, 256, 1024, 4096]]
        z = 5 if name == 'DNG-Laplace' else 4
        ax.plot(x_values, y_values, linestyle, linewidth=linewidth, color=color, label=file.split(".")[0], markersize=markersize, zorder=z)
        ax.set_facecolor('#eaeaf2')
        ax.grid(color='white')
        ax.set_yscale('log', base=10)
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        ax.set_xlabel('Number of Samples $n$')
        ax.grid(True)
        ax.set_ylabel('AND gates')

        ax.set_xticks(x_values)
        ax.set_xticklabels([f'$2^{{ {x} }}$' for x in x_values])

    for index, y in enumerate(y_axis):
        ax = fig.add_subplot(gs[0, index+1])
        for file in log_files:
            linestyle, color, linewidth, name, markersize = log_files_dict[file]
            x_values = [4, 6, 8, 10, 12]  # log2 values
            y_values = [data[lambd][n][file][y] for n in [16, 64, 256, 1024, 4096]]
            z = 5 if name == 'DNG-Laplace' else 4
            ax.plot(x_values, y_values, linestyle, linewidth=linewidth, color=color, label=file.split(".")[0] if index == 0 else "", markersize=markersize, zorder=z)
        
            ax.set_facecolor('#eaeaf2')
            ax.grid(color='white')
            ax.set_yscale('log', base=10)
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            ax.set_xlabel('Number of Samples $n$')
            ax.grid(True)
            ax.set_ylabel(y_map[y])

            ax.set_xticks(x_values)
            ax.set_xticklabels([f'$2^{{ {x} }}$' for x in x_values])

    fig.tight_layout()
    save_path = os.path.join(output_path, f'combined_appendix.eps')
    fig.savefig(save_path, format='eps')
    save_path = os.path.join(output_path, f'combined_appendix.png')
    fig.savefig(save_path, format='png')

    plt.close()

    

def plot_combined(y_axis):
    y_map = {'global_data': 'communication (MB)', 'time': 'time (s)', 'and':'AND gates'}
    lambd_values = [128, 256, 512]
    fig = plt.figure(figsize=(32, 6))
    gs = gridspec.GridSpec(1, 3, height_ratios=[1], width_ratios=[2, 2, 2])
    if y_axis == 'and':
        new_log_files = log_files.copy()
        import pickle
        with open('exp/logs-bmr/data-and.pkl', 'rb') as f:
            new_data = pickle.load(f)

        new_log_files.append('exp/logs-bmr/trans_lap.log')
        for index, lambd in enumerate(lambd_values):
            ax = fig.add_subplot(gs[0, index])
            for file in new_log_files:
                linestyle, color, linewidth, name, markersize = log_files_dict[file]
                x_values = [4, 6, 8, 10, 12]  # log2 values
                y_values = [new_data[lambd][n][file] for n in [16, 64, 256, 1024, 4096]]
                z = 5 if name == 'DNG-Laplace' else 4
                ax.plot(x_values, y_values, linestyle, linewidth=linewidth, color=color, label=file.split(".")[0] if index == 0 else "", markersize=markersize, zorder=z)
                ax.set_facecolor('#eaeaf2')
                ax.grid(color='white')
                ax.set_yscale('log', base=10)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                
                ax.set_xlabel('Number of Samples $n$')
                ax.grid(True)
                if index == 0:
                    ax.set_ylabel(y_map[y_axis])
                # else:
                #     ax.yaxis.set_tick_params(width=0)  # Hide y-axis ticks
                #     ax.yaxis.set_ticklabels([])        # Hide y-axis tick labels
                ax.set_xticks(x_values)
                ax.set_xticklabels([f'$2^{{ {x} }}$' for x in x_values])
                plt.title(f'$\lambda={lambd}$')
    else:
        for index, lambd in enumerate(lambd_values):
            ax = fig.add_subplot(gs[0, index])
            for file in log_files:
                linestyle, color, linewidth, name, markersize = log_files_dict[file]
                x_values = [4, 6, 8, 10, 12]  # log2 values
                y_values = [data[lambd][n][file][y_axis] for n in [16, 64, 256, 1024, 4096]]
                z = 5 if name == 'DNG-Laplace' else 4
                ax.plot(x_values, y_values, linestyle, linewidth=linewidth, color=color, label=file.split(".")[0] if index == 0 else "", markersize=markersize, zorder=z)
            
                ax.set_facecolor('#eaeaf2')
                ax.grid(color='white')
                ax.set_yscale('log', base=10)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                
                ax.set_xlabel('Number of Samples $n$')
                ax.grid(True)
                if index == 0:
                    ax.set_ylabel(y_map[y_axis])

                ax.set_xticks(x_values)
                ax.set_xticklabels([f'$2^{{ {x} }}$' for x in x_values])
                plt.title(f'$\lambda={lambd}$')

    fig.tight_layout()
    save_path = os.path.join(output_path, f'combined_{y_axis}.eps')
    fig.savefig(save_path, format='eps')
    save_path = os.path.join(output_path, f'combined_{y_axis}.png')
    fig.savefig(save_path, format='png')

    plt.close()

    fig_leg = plt.figure(figsize=(32, 1)) 

    ax_leg = fig_leg.add_subplot(111) 

    for file, style in log_files_dict.items():
        linestyle, color, linewidth, name, markersize = style
        ax_leg.plot([], [], linestyle, linewidth=linewidth, color=color, label=name)

    ax_leg.axis('off') 
    legend = ax_leg.legend(loc='center', ncol=8)
    legend.get_frame().set_facecolor('#eaeaf2')
    legend.get_frame().set_edgecolor('none')

    fig_leg.tight_layout()
    fig_leg.savefig("legend.png", bbox_inches='tight')  
    save_path = os.path.join(output_path, f'legend.eps')
    fig_leg.savefig(save_path, format='eps')
    save_path = os.path.join(output_path, f'legend.png')
    fig_leg.savefig(save_path, format='png')


def plot_lambd_vs_time():
    fig, ax = plt.subplots(figsize=(16, 9))
    
    log_files_to_plot = ["direct_lap.log", "ostack_lap.log", "direct_gauss.log", "ostack_gauss.log"]
    log_files_to_plot = [os.path.join(dir, file) for file in log_files_to_plot]

    plot_styles = {
        os.path.join(dir, "direct_lap.log"): ('+--', colors[5], 4, 'ODO-Laplace', 20),
        os.path.join(dir, "ostack_lap.log"): ('^-', colors[0], 4, 'Ostack-Laplace', 20),
        os.path.join(dir, "direct_gauss.log"): ('+-', colors[6], 4, 'ODO-Gaussian', 20),
        os.path.join(dir, "ostack_gauss.log"): ('*-', colors[4], 4, 'Ostack-Gaussian', 20),
    }

    n_value = 4096  
    lambd_values = [64, 128, 256, 512] 

    for file in log_files_to_plot:
        linestyle, color, linewidth, name, markersize = plot_styles[file]
        x_values = [lambd for lambd in sorted(data.keys()) if lambd in lambd_values]
        y_values = [data[lambd][n_value][file]["time"] for lambd in x_values if n_value in data[lambd]]

        ax.plot(x_values, y_values, linestyle, linewidth=linewidth, color=color, label=name, markersize=markersize)

    ax.set_facecolor('#eaeaf2')  
    ax.grid(color='white', which="both", ls="--")  
    ax.set_xscale('log', base=2) 

    ax.set_xticks(lambd_values)  
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())  

    for spine in ax.spines.values():  
        spine.set_visible(False)

    ax.set_xlabel('Security Parameter $\lambda$')
    ax.set_ylabel('Time (s)')

    ax.legend()

    plt.savefig('exp/plots/intro.png', format='png')
    plt.savefig('exp/plots/intro.eps', format='eps')

    plt.show()

plot_lambd_vs_time()
