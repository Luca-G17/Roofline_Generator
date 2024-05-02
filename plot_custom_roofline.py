import os
import json
import numpy as np
import matplotlib.pyplot as plt
import time
import subprocess
import signal

def generate_roofline_data(dirname):
    devnull = open('/dev/null', 'w')
    rank_dirs = os.listdir(dirname)
    for rank in rank_dirs:
        p = subprocess.Popen(["advixe-gui", f"{dirname}/{rank}"], stdout=devnull)
        time.sleep(5)
        pid = p.pid
        os.kill(pid, signal.SIGINT)

def average_roofline_data(dirname):
    rank_dirs = os.listdir(dirname)
    rank_data = [ f'{dirname}/{dir}/roofline.data' for dir in rank_dirs if os.path.isdir(f'{dirname}/{dir}')]
    data = []
    for rank in rank_data:
        with open(rank, 'r') as f:
            JSON = json.load(f)
            data.append([[loop['x'], loop['y']] for loop in JSON['loops'] if 'timestep' in loop['name']][0])
    
    return np.mean(np.array(data), axis=0)

def roofline_chart(memory_roofs, compute_roofs, data_points, point_labels):
    # Intersect with L1 roof
    compute_roof_bounds = [roof[1] / memory_roofs[0][1] for roof in compute_roofs]

    # Intersect with SP Vector FMA roof
    memory_roof_bounds = [compute_roofs[0][1] / roof[1] for roof in memory_roofs]

    for i, bound in enumerate(compute_roof_bounds):
        xs = np.linspace(bound, 20, 2)
        ys = np.ones(len(xs)) * compute_roofs[i][1]    
        plt.text(17, compute_roofs[i][1], f'{compute_roofs[i][0]}\n{compute_roofs[i][1]} GFLOPS')
        plt.plot(xs, ys, c='b', linestyle='dashed', label='_nolegend_')

    for i, bound in enumerate(memory_roof_bounds):
        xs = np.linspace(0, bound, 2)
        ys = xs * memory_roofs[i][1]
        offset = 0
        if len(memory_roof_bounds) - 1 == i:
            offset = 130
        plt.text(min(bound, 7), ys[-1] + 15 - offset, memory_roofs[i][0])
        plt.plot(xs, ys, c='g', linestyle='dashed', label='_nolegend_')

    plt.grid()
    for i in range(len(data_points)):
        point = data_points[i]
        plt.scatter(10 ** point[0], 10 ** point[1], s=30, zorder=10, label=point_labels[i])
    
    plt.ylim((0.01, 400))
    plt.xlim((0.01, 15))
    plt.yscale('log')
    plt.xscale('log')
    plt.subplots_adjust(wspace=0.2, hspace=0.2, top=0.88, bottom=0.11, left=0.125, right=0.779)
    plt.xlabel('Arithmetic Intensity FLOP/Byte')
    plt.ylabel('GFLOPS')

    memory_bandwidth_label = ''
    for roof in memory_roofs:
        memory_bandwidth_label += f'{roof[0]} - {roof[1]:.2f}GB/s\n'

    plt.text(17, 0.10, memory_bandwidth_label)
    plt.legend()
    plt.show()

memory_roofs = [
    ['L1', 276.62],
    ['L2', 75.70],
    ['L3', 34.94],
    ['DRAM', 12.87]
]

compute_roofs = [
    ['SP Vector FMA', 178.16],
    ['SP Vector Add', 22.32],
    ['SP Scalar Add', 2.8]
]

data = [
    average_roofline_data('single_rank'),
    average_roofline_data('baseline_ranks'),
    average_roofline_data('single_rank_1024'),
    average_roofline_data('baseline_rank_1024')
]

labels = [
    '2048 - Single Core', 
    '2048 - Rank Average - 56 Core (2x Nodes)',
    '1024 - Single Core',  
    '1024 - Rank Average - 56 Core (2x Nodes)'
]

roofline_chart(memory_roofs, compute_roofs, np.array(data), labels)

# generate_roofline_data('baseline_rank_1024')