import os
import json
import time
import subprocess
import csv
import sys
from datetime import datetime
from node_manager import NodeManager

def run_experiment(network="regtest"):
    # Load config and start node manager
    manager = NodeManager("config.json", network)
    try:
        manager.start_node()
        manager.setup_wallet()
    except Exception as e:
        print(f"Node setup failed: {e}")
        return

    config = manager.config
    net_cfg = manager.net_cfg
    
    NUM_RUNS = config["num_runs"]
    ARTIFACT_DIR = "artifacts/experiments"
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    
    csv_filename = f"{network}_variance.csv"
    CSV_PATH = os.path.join(ARTIFACT_DIR, csv_filename)
    
    # Write CSV Header
    with open(CSV_PATH, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "timestamp", "latency_ms"])

    print(f"=== Starting {NUM_RUNS} Linked ACS Runs on {network.upper()} ===")
    
    base_cmd = [
        "go", "run", "./scripts/deploy_linked_acs.go",
        "-bitcoin-cli", manager.get_cli_path(),
        "-network", network,
        "-wallet", manager.wallet,
        "-fund-sat", str(net_cfg["fund_sat"]),
        "-fee-sat", str(net_cfg["fee_sat"])
    ]
    
    if net_cfg.get("auto_mine"):
        base_cmd.append("-auto-mine-regtest")
    if net_cfg.get("max_wait_seconds"):
        base_cmd.extend(["-max-wait-seconds", str(net_cfg["max_wait_seconds"])])

    for i in range(1, NUM_RUNS + 1):
        print(f"--- Run {i}/{NUM_RUNS} ---")
        start_time = time.time()
        
        try:
            res = subprocess.run(base_cmd, capture_output=True, text=True, check=True)
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # ms
            
            with open(CSV_PATH, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([i, datetime.now().isoformat(), round(latency, 2)])
                
            print(f"Success! Latency: {latency:.2f} ms")
        except subprocess.CalledProcessError as e:
            print(f"Run {i} failed!")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            break

if __name__ == "__main__":
    network = "regtest"
    if len(sys.argv) > 1:
        network = sys.argv[1].lower()
    run_experiment(network)
