# CALIBER — On-Chain Signet Execution Guide

> **Validate linked ACS script-path execution on Bitcoin signet with fund safety.**

## 1. Fund Safety: Two-Wallet Strategy

Signet uses real testnet BTC. Each `deploy_linked_acs.go` run **burns** the `fund-sat` amount (sent to P2TR then spent into OP_RETURN). To protect your funds, we use two wallets:

| Wallet | Role | Balance | 
|--------|------|---------|
| `CALIBER1` | **Experiment wallet** | ~0.06 BTC |
| `CALIBER2` | **Vault wallet** | remaining ~0.13 BTC |

### Fund Flow

```
[Existing wallet: 0.19 BTC]
        │
        ├──→ CALIBER1 (0.06 BTC)  ←-- used for experiments
        │
        └──→ CALIBER2 (0.13 BTC)  ←-- vault, sends to CALIBER1 if needed
                                 ←-- receives sweep after experiments
```

### Transfer Between Wallets

```powershell
# CALIBER2 → CALIBER1 (refill if needed)
$addr1 = & "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -rpcwallet=CALIBER1 getnewaddress
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -rpcwallet=CALIBER2 sendtoaddress $addr1 0.01

# CALIBER1 → CALIBER2 (sweep leftovers after experiments)
$addr2 = & "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -rpcwallet=CALIBER2 getnewaddress
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -rpcwallet=CALIBER1 sendtoaddress $addr2 <remaining_balance>
```

## 2. Budget Planning

| Experiment | fund-sat | Runs | Total (sat) | BTC |
|-----------|:--------:|:----:|:-----------:|:---:|
| Single deploy (Table 3) | 3,000,000 | 1 | 3,000,000 | 0.030 |
| Fee profile (Table 4) | 500,000 | 5 | 2,500,000 | 0.025 |
| **Total required** | | **6** | **5,500,000** | **0.055** |
| Contingency (fees) | | | ~500,000 | ~0.005 |
| **Total budget** | | | **6,000,000** | **0.060** |

## 3. Prerequisites

- Signet node synced (check: `getblockchaininfo`)
- Wallet balance: ≥0.06 BTC in CALIBER1

```powershell
# Check sync status
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -datadir="E:\Bitcoin\data" -conf="E:\Bitcoin\bitcoin.conf" getblockchaininfo

# Check budget
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -rpcwallet=CALIBER1 getbalance
```

## 4. Wallet Setup (First Time)

```powershell
# Create experiment and vault wallets
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet createwallet "CALIBER1"
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet createwallet "CALIBER2"

# Fund CALIBER1 with exactly 0.06 BTC
# (send from your existing funded signet wallet)
```

**Important:** Signet wallets must be loaded before use. The deploy script auto-loads with `-try-load-wallet`.

## 5. Single Profile Deploy (Paper Table 3)

Analytical profile: fund=3,000,000 sat, fee=500,000 sat.

```powershell
go run ./scripts/deploy_linked_acs.go -bitcoin-cli "E:\Bitcoin\daemon\bitcoin-cli.exe" -network signet -wallet CALIBER1 -fund-sat 3000000 -fee-sat 500000 -try-load-wallet -max-wait-seconds 600
```

**Key differences from regtest:**
- No auto-mining (must wait for signet blocks)
- Requires `-max-wait-seconds` (default 600s = 10 min)
- Mempool acceptance may take longer

## 6. Fee Profile Campaign (Paper Table 4)

Reduced to 5 fees × 1 seed = 5 runs to conserve budget.

```powershell
.\scripts\signet_fee_profiles.ps1 -BitcoinCli "E:\Bitcoin\daemon\bitcoin-cli.exe" -WalletName CALIBER1 -FundSat 500000
```

**Fee levels:** 250, 500, 1000, 2500, 5000 satoshis.

**Important:** The signet fee profile script's default `FundSat=3,000,000` would exceed budget. We use `FundSat=500,000` which still validates script feasibility while keeping total cost at 5 × 500,000 = 0.025 BTC.

**Output structure:**
```
artifacts/onchain/signet/fee_profiles/
├── fee_250_seed_1.json
├── fee_500_seed_1.json
├── fee_1000_seed_1.json
├── fee_2500_seed_1.json
├── fee_5000_seed_1.json
├── fee_profile_summary.csv
├── fee_profile_summary.json
├── fee_profile_txids.csv
└── fee_profile_txids.json
```

## 7. Post-Experiment Cleanup

```powershell
# Get CALIBER2 deposit address
$vault_addr = & "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -rpcwallet=CALIBER2 getnewaddress

# Sweep remaining CALIBER1 balance
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -rpcwallet=CALIBER1 sendtoaddress $vault_addr <remaining_balance>

# Verify vault received
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -rpcwallet=CALIBER2 getbalance
```

## 8. What Gets Consumed Per Run

Each linked ACS deploy burns:

- **fundValueSat** — full amount sent to P2TR address (cannot be spent elsewhere)
- **Transaction fee** — network fee for the spend tx (typically a few thousand sat)

The spend transaction output:
- `burnValue = fundValueSat - feeSat` → OP_RETURN (permanently unspendable)
- `feeSat` → miner fee (collected by the mining pool that includes the tx)

**There is no recovery path.** The pre-signed template only authorizes the fixed burn+fee outputs.

## 9. Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `wallet not found` | CALIBER1 not created | Run `createwallet "CALIBER1"` |
| `insufficient funds` | Budget too low | Send more from CALIBER2 |
| `mempool rejection` | Fee rate below network policy | Use `-max-burn-btc` with computed value (default handles this) |
| `timeout waiting for funding` | Signet block not mined yet | Increase `-max-wait-seconds` or check `getblockchaininfo` |
| `too-long-mempool-chain` | Unconfirmed parent chain | Deploy waits for prior confirmations; increase `-max-wait-seconds` |
