import os
import subprocess

ARTIFACTS_DIR = "artifacts/experiments"

def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Success!")
    except subprocess.CalledProcessError as e:
        print(f"Failed! {e}")

def generate_all():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    # Run the core go experiment runners
    go_scripts = [
        ["go", "run", "./cmd/experiment_runner"],
        ["go", "run", "./cmd/coalition_eval"],
        ["go", "run", "./cmd/experiment_runner_m2"],
        # Note: onchain_orchestrator requires active bitcoind, which orchestrator.py will handle via deploy_linked_acs.go
    ]
    
    for script in go_scripts:
        run_cmd(script)
        
    print("Go data generation complete.")

if __name__ == "__main__":
    generate_all()
