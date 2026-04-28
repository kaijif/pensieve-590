import os
import numpy as np
import matplotlib
matplotlib.use('Agg') # use non-interactive backend
import matplotlib.pyplot as plt

RESULTS_DIR = 'experiment_results'
CHARTS_DIR = 'charts'

if not os.path.exists(CHARTS_DIR):
    os.makedirs(CHARTS_DIR)
CONDITIONS = ['cond1', 'cond2', 'cond3']
COND_LABELS = ['Satellite', 'Bursty Wi-Fi', 'Degraded']
ALGOS = ['mpc', 'rl']
ALGO_LABELS = {'mpc': 'robustMPC', 'rl': 'Pensieve'}
COLORS = {'mpc': 'blue', 'rl': 'red'}

def parse_logs(cond, algo):
    log_dir = os.path.join(RESULTS_DIR, cond, algo)
    traces = []
    try:
        files = os.listdir(log_dir)
    except OSError:
        return {}
    
    for filename in files:
        if not filename.startswith('log_sim_'):
            continue
        trace_name = filename.split('_', 3)[-1]
        
        time_stamp = []
        bit_rate = []
        reward = []
        
        with open(os.path.join(log_dir, filename), 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 7:
                    time_stamp.append(float(parts[0]))
                    bit_rate.append(float(parts[1]))
                    reward.append(float(parts[6]))
        if reward:
            time_stamp = np.array(time_stamp)
            time_stamp -= time_stamp[0]
            traces.append({
                'name': trace_name,
                'total_reward': np.sum(reward),
                'time_stamp': time_stamp,
                'bit_rate': bit_rate
            })
    return traces

def plot_cdfs():
    for idx, cond in enumerate(CONDITIONS):
        plt.figure(figsize=(6, 4))
        for algo in ALGOS:
            traces = parse_logs(cond, algo)
            if not traces:
                continue
            rewards = [t['total_reward'] for t in traces]
            rewards.sort()
            
            # Compute CDF
            p = 1. * np.arange(len(rewards)) / (len(rewards) - 1)
            plt.plot(rewards, p, label=ALGO_LABELS[algo], color=COLORS[algo], linewidth=2)
            
        plt.title('QoE CDF: {}'.format(COND_LABELS[idx]), fontsize=14)
        plt.xlabel('Average QoE (Total Reward)', fontsize=12)
        plt.ylabel('CDF', fontsize=12)
        plt.legend(loc='lower right')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, 'cdf_{}.png'.format(cond)))
        plt.close()

def plot_summary_bar():
    pensieve_norm = []
    mpc_norm = []
    
    for cond in CONDITIONS:
        mpc_traces = parse_logs(cond, 'mpc')
        rl_traces = parse_logs(cond, 'rl')
        
        mpc_avg = np.mean([t['total_reward'] for t in mpc_traces]) if mpc_traces else 1.0
        rl_avg = np.mean([t['total_reward'] for t in rl_traces]) if rl_traces else 1.0
        # Append raw averages instead of normalizing
        mpc_norm.append(mpc_avg)
        pensieve_norm.append(rl_avg)
        
    x = np.arange(len(CONDITIONS))
    width = 0.35
    
    plt.figure(figsize=(8, 5))
    plt.bar(x - width/2, mpc_norm, width, label='robustMPC', color=COLORS['mpc'])
    plt.bar(x + width/2, pensieve_norm, width, label='Pensieve', color=COLORS['rl'])
    
    plt.ylabel('Average QoE (Raw Reward)', fontsize=12)
    plt.title('Performance Summary Across Conditions', fontsize=14)
    plt.xticks(x, COND_LABELS, fontsize=12)
    plt.legend()
    plt.yscale('symlog')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'summary_bar.png'))
    plt.close()

def plot_qualitative_trace():
    for idx, cond in enumerate(CONDITIONS):
        # Find a trace that both algos ran on
        rl_traces = parse_logs(cond, 'rl')
        mpc_traces = parse_logs(cond, 'mpc')
        
        if not rl_traces or not mpc_traces:
            continue
            
        # Just take the first trace name from RL
        target_trace = rl_traces[0]['name']
        
        rl_data = next((t for t in rl_traces if t['name'] == target_trace), None)
        mpc_data = next((t for t in mpc_traces if t['name'] == target_trace), None)
        
        if not rl_data or not mpc_data:
            continue
            
        plt.figure(figsize=(10, 5))
        
        # Plot Pensieve
        plt.plot(range(1, len(rl_data['bit_rate']) + 1), rl_data['bit_rate'], label='Pensieve', color=COLORS['rl'], drawstyle='steps-post', linewidth=2, alpha=0.8)
        
        # Plot robustMPC
        plt.plot(range(1, len(mpc_data['bit_rate']) + 1), mpc_data['bit_rate'], label='robustMPC', color=COLORS['mpc'], drawstyle='steps-post', linewidth=2, linestyle='--', alpha=0.8)
        
        plt.title('Bitrate over Time ({}) - Trace: {}'.format(COND_LABELS[idx], target_trace), fontsize=14)
        plt.xlabel('Video Chunk Index', fontsize=12)
        plt.ylabel('Bitrate (Kbps)', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, 'qualitative_{}.png'.format(cond)))
        plt.close()
if __name__ == '__main__':
    print("Generating CDF plots...")
    plot_cdfs()
    
    print("Generating summary bar chart...")
    plot_summary_bar()
    
    print("Generating qualitative trace plot...")
    plot_qualitative_trace()
    
    print("All plots generated successfully!")
