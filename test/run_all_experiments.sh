#!/bin/bash

# Setup
echo "Creating results directories..."
mkdir -p experiment_results/cond1/rl experiment_results/cond1/mpc
mkdir -p experiment_results/cond2/rl experiment_results/cond2/mpc
mkdir -p experiment_results/cond3/rl experiment_results/cond3/mpc

# Generate video size chunks if they don't exist
if [ ! -f "video_size_0" ]; then
    echo "Generating video sizes..."
    python get_video_sizes.py
fi

# Generate traces
echo "Generating custom traces..."
python ../traces/generate_custom_traces.py

# Run conditions
for cond in cond1 cond2 cond3; do
    echo "=========================================="
    echo "Running experiments for $cond..."
    echo "=========================================="
    
    export TRACE_DIR="./traces/$cond/"
    
    # Run Pensieve (RL)
    echo "Running Pensieve on $cond..."
    python rl_no_training.py
    mv results/log_sim_rl_* experiment_results/$cond/rl/
    
    # Run robustMPC
    echo "Running robustMPC on $cond..."
    python mpc.py
    mv results/log_sim_mpc_* experiment_results/$cond/mpc/
done

echo "=========================================="
echo "Experiments completed for custom conditions."
echo "Results are stored in test/experiment_results/"
echo "Note: To run on FCC baseline traces, ensure they are placed in test/traces/fcc/ and run them manually using TRACE_DIR=./traces/fcc/."
