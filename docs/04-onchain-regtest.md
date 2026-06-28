# CALIBER — On-Chain Regtest Execution Guide

> **Validate linked ACS script-path execution on Bitcoin regtest.**

## 1. Overview

The regtest stage validates that CALIBER's linked Taproot ACS script can be:
1. Funded (send satoshis to the P2TR address)
2. Spent (broadcast a pre-signed witness transaction with burn outputs)
3. Confirmed (mined into a block)

**Key insight:** Each linked ACS deployment burns the `fund-sat` by sending to a Taproot address and spending through the linked leaf into OP_RETURN. On regtest this is free (we mine our own blocks); on signet each burn consumes real testnet BTC.

## 2. Wallet Setup

```powershell
# Create wallet (first time only)
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -regtest -datadir="E:\Bitcoin\data" -conf="E:\Bitcoin\bitcoin.conf" createwallet "CALIBER"

# Fund with 101 blocks (coinbase maturity)
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -regtest -datadir="E:\Bitcoin\data" -conf="E:\Bitcoin\bitcoin.conf" -rpcwallet=CALIBER -generate 101

# Verify balance
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -regtest -datadir="E:\Bitcoin\data" -conf="E:\Bitcoin\bitcoin.conf" -rpcwallet=CALIBER getbalance
```

The `config.json` uses `wallet_name: "CALIBER"` to ensure all scripts target this wallet.

## 3. Single Profile Deploy (Paper Table 3)

Deploys the analytical profile: fund=3,000,000 sat, fee=500,000 sat.

```powershell
go run ./scripts/deploy_linked_acs.go -bitcoin-cli "E:\Bitcoin\daemon\bitcoin-cli.exe" -network regtest -wallet CALIBER -fund-sat 3000000 -fee-sat 500000 -try-load-wallet
```

**What happens (9 steps):**

| Step | Action | Detail |
|------|--------|--------|
| 1/9 | Node check | Verifies regtest node connectivity |
| 2/9 | Key generation | Creates random revocation secret \(r^j_a\), HTLC preimage \(pre_b\), signer keys |
| 3/9 | Funding | Sends `fund-sat` to P2TR address with Taproot 2-leaf script tree |
| 4/9 | Mine | Mines 1 regtest block to confirm funding tx |
| 5/9 | Spend build | Constructs pre-signed linked spend tx with burn + fee outputs |
| 6/9 | Mempool check | Verifies spend tx passes `testmempoolaccept` |
| 7/9 | Broadcast | Sends the signed linked spend transaction |
| 8/9 | Mine | Mines 1 block to confirm spend tx |
| 9/9 | Artifact write | Saves evidence to `artifacts/linked_acs_regtest.json` |

**Output artifact:**
```json
{
  "network": "regtest",
  "wallet": "CALIBER",
  "fundTxid": "<txid>",
  "spendTxid": "<txid>",
  "fundValueSat": 3000000,
  "feeSat": 500000,
  "burnValueSat": 2500000
}
```

## 4. Fee-Profile Campaign (Paper Table 4)

Runs 5 fee levels × 3 seeds = 15 linked ACS deployments.

```powershell
.\scripts\regtest_fee_profiles.ps1 -BitcoinCli "E:\Bitcoin\daemon\bitcoin-cli.exe" -WalletName CALIBER -FundSat 3000000
```

**Fee levels:** 250, 500, 1000, 2500, 5000 satoshis.

**Output structure:**
```
artifacts/onchain/regtest/fee_profiles/
├── fee_250_seed_1.json
├── fee_250_seed_2.json
├── fee_250_seed_3.json
├── fee_500_seed_1.json
├── ...
├── fee_5000_seed_3.json
├── fee_profile_summary.{csv,json}
└── fee_profile_txids.{csv,json}
```

## 5. Variance Data (Plots)

Captures end-to-end latency measurements for visualization.

```powershell
# Runs 100 consecutive linked ACS deploys (config.json: num_runs=100)
uv run scripts/core/orchestrator.py regtest
```

**Outputs:**
- `artifacts/experiments/regtest_variance.csv` — `run_id, timestamp, latency_ms` (100 runs)
- `artifacts/onchain/repeated_onchain_runs.csv` — deployment duration data

**Config-driven:** The orchestrator reads `fund_sat`, `fee_sat`, and `wallet_name` from `config.json` per network. To adjust number of runs, edit `num_runs` in `config.json`.

## 6. Script Architecture

The linked ACS deploy script (`scripts/deploy_linked_acs.go`) constructs:

### Taproot Tree (2 leaves on `out[2]`)

```
Leaf CRAB:   OP_SHA256 <H(r^j_a)> OP_EQUAL
Leaf Linked: OP_SHA256 <H(r^j_a)> OP_EQUALVERIFY
             OP_SHA256 <H(pre_b)> OP_EQUALVERIFY
             <xonly(pkA)> OP_CHECKSIG
             <xonly(pkB)> OP_CHECKSIGADD
             OP_2 OP_EQUAL
```

### Spend Transaction Witness

```
<sig_B> <sig_A> <pre_b> <r^j_a> <linkedLeafScript> <controlBlock>
```

### Outputs

- `burnValue = fund-sat - fee-sat` → OP_RETURN (provably unspendable)
- Miner reward = `fee-sat` via transaction fee (coinbase)

## 7. Deploy Script Flags

The `deploy_linked_acs.go` script supports these flags:

| Flag | Default | Description |
|------|---------|-------------|
| `-bitcoin-cli` | `bitcoin-cli` | Path to bitcoin-cli executable |
| `-network` | `regtest` | Network: regtest or signet |
| `-wallet` | `CALIBER` | Wallet name |
| `-fund-sat` | `3000000` | Funding amount in satoshis |
| `-fee-sat` | `500000` | Miner reward in satoshis |
| `-datadir` | `""` | Bitcoin data directory |
| `-conf` | `""` | Bitcoin config file path |
| `-try-load-wallet` | `true` | Auto-load wallet before RPC calls |
| `-max-wait-seconds` | `120` | Max wait for tx visibility |

## 8. Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `wallet not found` | Wallet not created | Run `createwallet "CALIBER"` first |
| `insufficient funds` | Wallet balance too low | Run `-generate 101` |
| `mempool rejection` | Fee rate too low | Check `-fee-sat` is reasonable (≥250) |
| `connect to server` | Bitcoin Core not running | Start bitcoind with correct config |
