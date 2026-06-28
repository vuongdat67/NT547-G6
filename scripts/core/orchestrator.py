import os
import json
import time
import subprocess
import csv
import sys
from datetime import datetime
from node_manager import NodeManager


def run_experiment(network="regtest"):
    manager = NodeManager("config.json", network)
    try:
        manager.start_node()
        manager.setup_wallet()
    except Exception as e:
        print(f"Node setup failed: {e}")
        return

    config = manager.config
    net_cfg = manager.net_cfg
    num_runs = config["num_runs"]
    wallet_name = net_cfg.get("wallet_name", manager.wallet)

    ARTIFACT_DIR = "artifacts/experiments"
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    csv_filename = f"{network}_variance.csv"
    CSV_PATH = os.path.join(ARTIFACT_DIR, csv_filename)

    artifact_json = f"artifacts/linked_acs_{network}.json"

    # Header with spend_vbytes
    with open(CSV_PATH, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "timestamp", "latency_ms", "spend_vbytes"])

    print(f"=== Starting {num_runs} Linked ACS Runs on {network.upper()} ===")
    print(f"    Wallet: {wallet_name}")
    print(f"    Fund: {net_cfg['fund_sat']} sat, Fee: {net_cfg['fee_sat']} sat")

    base_cmd = [
        "go", "run", "./scripts/deploy_linked_acs.go",
        "-bitcoin-cli", manager.get_cli_path(),
        "-network", network,
        "-wallet", wallet_name,
        "-fund-sat", str(net_cfg["fund_sat"]),
        "-fee-sat", str(net_cfg["fee_sat"]),
    ]

    if network == "regtest" and net_cfg.get("auto_mine", True):
        base_cmd.append("-auto-mine-regtest")
    if net_cfg.get("max_wait_seconds"):
        base_cmd.extend(["-max-wait-seconds", str(net_cfg["max_wait_seconds"])])

    cli_path = manager.get_cli_path()
    successes = 0
    failures = 0
    total_vbytes = 0

    for i in range(1, num_runs + 1):
        print(f"--- Run {i}/{num_runs} ---")
        start_time = time.time()

        try:
            res = subprocess.run(base_cmd, capture_output=True, text=True, check=True)
            end_time = time.time()
            latency = (end_time - start_time) * 1000

            # Read spendTxid from artifact to get vbytes via bitcoin-cli
            spend_vbytes = 0
            if os.path.exists(artifact_json):
                try:
                    with open(artifact_json, "r") as f:
                        art = json.load(f)
                    spend_txid = art.get("spendTxid", "")
                    if spend_txid:
                        # getrawtransaction needs -rpcwallet on pruned nodes
                        args = ["-regtest" if network == "regtest" else "-signet",
                                f"-rpcwallet={wallet_name}",
                                "getrawtransaction", spend_txid, "true"]
                        cli_cmd = [cli_path] + args
                        tx_res = subprocess.run(cli_cmd, capture_output=True, text=True)
                        if tx_res.returncode == 0:
                            tx_info = json.loads(tx_res.stdout)
                            spend_vbytes = tx_info.get("vsize", 0)
                except Exception:
                    pass

            with open(CSV_PATH, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([i, datetime.now().isoformat(), round(latency, 2), spend_vbytes])

            successes += 1
            total_vbytes += spend_vbytes
            print(f"  OK ({latency:.0f} ms, {spend_vbytes} vB)")

        except subprocess.CalledProcessError as e:
            failures += 1
            print(f"  FAIL: {e.stderr[-200:] if e.stderr else 'unknown'}")

    print(f"\n=== Summary ===")
    print(f"  Total: {num_runs}, Success: {successes}, Failures: {failures}")
    avg_vb = total_vbytes // max(successes, 1)
    print(f"  Avg vB: {avg_vb}")
    print(f"  CSV: {CSV_PATH}")


if __name__ == "__main__":
    network = "regtest"
    if len(sys.argv) > 1:
        network = sys.argv[1].lower()
    run_experiment(network)
