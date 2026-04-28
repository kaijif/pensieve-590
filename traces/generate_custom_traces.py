import os
import numpy as np

BASE_OUTPUT_DIR = '../test/traces'

def get_out_dir(subfolder):
    d = os.path.join(BASE_OUTPUT_DIR, subfolder)
    if not os.path.exists(d):
        os.makedirs(d)
    return d

def generate_condition_1(num_traces=100, trace_length=320):
    """
    Condition 1 - Satellite-Like (High Throughput, High Latency)
    - Throughput: Gaussian around 80 Mbps, sigma = 20 Mbps
    - Inject 3-5 second near-zero outages every ~90 seconds (beam handoff simulation)
    - RTT: 40 ms (Note: RTT is configured in env.py, not in the trace file)
    - Generate 100 x 320-second traces
    """
    for i in range(num_traces):
        trace_name = 'satellite_{}.txt'.format(i)
        file_path = os.path.join(get_out_dir('cond1'), trace_name)
        
        with open(file_path, 'w') as f:
            time = 0
            while time < trace_length:
                # Normal throughput period (around 90 seconds)
                # We add some randomness to the 90 seconds so it's ~90s
                normal_duration = int(np.random.normal(90, 10))
                normal_duration = max(30, min(150, normal_duration))
                
                for _ in range(normal_duration):
                    if time >= trace_length:
                        break
                    
                    # Gaussian around 80 Mbps, sigma = 20 Mbps
                    bw = np.random.normal(80, 20)
                    # Bound it so it doesn't go below 1 or too crazy high
                    bw = max(1.0, bw)
                    
                    f.write('{} {:.4f}\n'.format(time, bw))
                    time += 1
                
                if time >= trace_length:
                    break
                
                # Outage period (3-5 seconds near-zero)
                outage_duration = np.random.randint(3, 6)
                for _ in range(outage_duration):
                    if time >= trace_length:
                        break
                    
                    bw = np.random.uniform(0.001, 0.05)
                    f.write('{} {:.4f}\n'.format(time, bw))
                    time += 1

def generate_condition_2(num_traces=5, trace_length=300):
    """
    Condition 2 - Bursty / Competing-Flow Wi-Fi
    - Alternate between 8 Mbps and 0.5 Mbps every 5-15 seconds (geometric hold time)
    - Add Gaussian noise within each phase (sigma = 10% of phase mean)
    """
    for i in range(num_traces):
        trace_name = 'bursty_wifi_{}.txt'.format(i)
        file_path = os.path.join(get_out_dir('cond2'), trace_name)
        
        with open(file_path, 'w') as f:
            time = 0
            state = 8.0 # start at 8 Mbps
            while time < trace_length:
                # Geometric hold time with mean ~10, bounded between 5 and 15
                hold_time = np.random.geometric(p=0.1)
                hold_time = max(5, min(15, hold_time))
                
                # Generate values for each second in this phase
                for _ in range(hold_time):
                    if time >= trace_length:
                        break
                    
                    # Add Gaussian noise (sigma = 10% of phase mean)
                    noise = np.random.normal(0, 0.1 * state)
                    
                    # Bandwidth in Mbit/sec, ensuring it stays positive
                    bw = max(0.1, state + noise)
                    
                    # Format: [time_stamp (sec), throughput (Mbit/sec)]
                    f.write('{} {:.4f}\n'.format(time, bw))
                    time += 1
                
                # Switch state for next phase
                state = 0.5 if state == 8.0 else 8.0

def generate_condition_3(num_traces=5, trace_length=300):
    """
    Condition 3 - Degraded / Sub-0.2 Mbps
    - Sustained throughput: 0.05-0.15 Mbps, occasionally dipping to near-zero
    """
    for i in range(num_traces):
        trace_name = 'degraded_{}.txt'.format(i)
        file_path = os.path.join(get_out_dir('cond3'), trace_name)
        
        with open(file_path, 'w') as f:
            time = 0
            # Sustained throughput is drawn uniformly from 0.05 to 0.15 for this trace
            base_mean = np.random.uniform(0.05, 0.15)
            
            while time < trace_length:
                # 10% chance to enter a 'dip' phase where throughput drops to near-zero
                is_dip = np.random.random() < 0.1
                
                if is_dip:
                    # Dip lasts for a short duration, e.g., 1-3 seconds
                    dip_duration = np.random.randint(1, 4)
                    for _ in range(dip_duration):
                        if time >= trace_length:
                            break
                        # Near-zero throughput
                        bw = np.random.uniform(0.001, 0.02)
                        f.write('{} {:.4f}\n'.format(time, bw))
                        time += 1
                else:
                    # Normal degraded flow duration
                    normal_duration = np.random.randint(5, 15)
                    for _ in range(normal_duration):
                        if time >= trace_length:
                            break
                        # Minor noise around the sustained baseline
                        noise = np.random.normal(0, 0.02)
                        bw = max(0.01, base_mean + noise)
                        f.write('{} {:.4f}\n'.format(time, bw))
                        time += 1

if __name__ == '__main__':
    print("Generating Condition 1 (Satellite-Like) traces in {}/cond1...".format(BASE_OUTPUT_DIR))
    generate_condition_1(num_traces=20, trace_length=320)

    print("Generating Condition 2 (Bursty Wi-Fi) traces in {}/cond2...".format(BASE_OUTPUT_DIR))
    generate_condition_2(num_traces=20, trace_length=300)
    
    print("Generating Condition 3 (Degraded) traces in {}/cond3...".format(BASE_OUTPUT_DIR))
    generate_condition_3(num_traces=20, trace_length=300)
    
    print("Traces generated successfully.")
