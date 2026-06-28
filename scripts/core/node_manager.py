import os
import json
import time
import subprocess
import shutil

class NodeManager:
    def __init__(self, config_path="config.json", network="regtest"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.network = network
        self.net_cfg = self.config["networks"][network]
        
        self.bitcoin_cli = self._find_executable(self.config["bitcoin_cli_paths"])
        self.bitcoind = self._find_executable(self.config["bitcoind_paths"])
        self.wallet = self.config["wallet_name"]

    def _find_executable(self, paths):
        # 1. Check given hardcoded paths
        for path in paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        # 2. Check system PATH via shutil.which
        # fallback for 'bitcoind' or 'bitcoin-cli'
        for path in paths:
            exe = shutil.which(path)
            if exe:
                return exe
        
        # 3. If all fails, return the first one hoping it's in PATH anyway, 
        # but warn the user.
        print(f"Warning: Could not find valid executable in {paths}, using default.")
        return paths[-1]

    def run_cli(self, args, check=True):
        cmd = [self.bitcoin_cli, f"-{self.network}"] + args
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return True, res.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()

    def start_node(self):
        # We don't start the node from python in this refactor because 
        # bitcoind might be running as a service or requires specific configs.
        # We will just verify it's running.
        print(f"Checking if {self.network} node is running...")
        success, out = self.run_cli(["getblockchaininfo"])
        if not success:
            raise RuntimeError(f"Node is not responding. Please start bitcoind on {self.network}. Error: {out}")
        print("Node is running.")

    def setup_wallet(self):
        # Load or create wallet
        print(f"Ensuring wallet '{self.wallet}' is loaded...")
        success, out = self.run_cli(["listwallets"])
        if success and self.wallet in out:
            print(f"Wallet '{self.wallet}' already loaded.")
        else:
            print(f"Attempting to load wallet '{self.wallet}'...")
            success, out = self.run_cli(["loadwallet", self.wallet], check=False)
            if not success and "not found" in out.lower():
                print(f"Wallet '{self.wallet}' not found, creating new...")
                success, out = self.run_cli(["createwallet", self.wallet])
                if not success:
                    raise RuntimeError(f"Failed to create wallet: {out}")
            elif not success and "already loaded" not in out.lower():
                # On Signet or if there's a weird error, just try to getbalance to see if it works
                pass

        # Check balance
        success, out = self.run_cli([f"-rpcwallet={self.wallet}", "getbalance"])
        if success:
            balance = float(out)
            print(f"Wallet balance: {balance} BTC")
            if balance < 0.0001 and self.network == "regtest":
                print("Balance is low. Mining 101 blocks to fund wallet...")
                self._mine_blocks(101)
        else:
            print(f"Warning: Failed to get balance: {out}")

    def _mine_blocks(self, count):
        success, addr = self.run_cli([f"-rpcwallet={self.wallet}", "getnewaddress"])
        if success:
            self.run_cli(["generatetoaddress", str(count), addr])
            print(f"Mined {count} blocks to {addr}")
        else:
            print(f"Failed to generate address for mining: {addr}")

    def get_cli_path(self):
        return self.bitcoin_cli
