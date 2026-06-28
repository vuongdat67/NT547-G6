# CALIBER — Quick Start

> **Reproduce all analytical and publication artifacts from scratch in minimal steps.**

This guide assumes a working Go 1.23+ toolchain and, for on-chain stages, a Bitcoin Core node running on regtest.

## Prerequisites

- Go 1.23+
- Python 3.11+ (via `uv`)
- Bitcoin Core 27+ (for on-chain stages)
  - Regtest node running (no sync needed)
  - Signet node synced (for signet stage)

## 1. Minimal Pipeline (Analytical-only, ~30s)

No Bitcoin node required. Generates all payoff tables, parameter sweeps, timelines, baselines, and publication figures.

```powershell
cd E:\NT547-G6

# Step 1: Run unit tests
go test ./...

# Step 2: Generate analytical experiments
go run ./cmd/experiment_runner

# Step 3: Parameter sensitivity (M2 variant)
go run ./cmd/experiment_runner_m2

# Step 4: Evaluation report
go run ./cmd/eval_report

# Step 5: Publication assets (LaTeX tables + SVG figures)
go run ./cmd/publish_results

# Step 6: Submission report
go run ./cmd/submission_report
```

Output: all files under `artifacts/experiments/` and `artifacts/publication/`.

## 2. Full Pipeline (with On-Chain Regtest, ~5min)

Runs the analytical pipeline plus linked ACS script execution on Bitcoin regtest.

```powershell
# 2a. Create and fund the CALIBER wallet (first time only)
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -regtest -datadir="E:\Bitcoin\data" -conf="E:\Bitcoin\bitcoin.conf" createwallet "CALIBER"
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -regtest -datadir="E:\Bitcoin\data" -conf="E:\Bitcoin\bitcoin.conf" -rpcwallet=CALIBER -generate 101

# 2b. Single linked ACS deploy (paper Table 3)
go run ./scripts/deploy_linked_acs.go -bitcoin-cli "E:\Bitcoin\daemon\bitcoin-cli.exe" -network regtest -wallet CALIBER -fund-sat 3000000 -fee-sat 500000 -try-load-wallet

# 2c. Fee-profile campaign: 5 fees × 3 seeds = 15 runs (paper Table 4)
.\scripts\regtest_fee_profiles.ps1 -BitcoinCli "E:\Bitcoin\daemon\bitcoin-cli.exe" -WalletName CALIBER -FundSat 3000000

# 2d. Variance data: 100 timing runs for plots (config.json: num_runs=100)
uv run scripts/core/orchestrator.py regtest
```

## 3. Full Pipeline (with On-Chain Signet, ~30min)

Requires signet node with funded wallet.

```powershell
# 3a. Create 2 wallets for fund safety (first time only)
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -datadir="E:\Bitcoin\data" -conf="E:\Bitcoin\bitcoin-signet.conf" createwallet "CALIBER1"
& "E:\Bitcoin\daemon\bitcoin-cli.exe" -signet -datadir="E:\Bitcoin\data" -conf="E:\Bitcoin\bitcoin-signet.conf" createwallet "CALIBER2"

# Fund CALIBER1 with ~0.06 BTC and CALIBER2 with remaining ~0.13 BTC
# (send from your existing signet wallet)

# 3b. Single linked ACS deploy (paper Table 3)
go run ./scripts/deploy_linked_acs.go -bitcoin-cli "E:\Bitcoin\daemon\bitcoin-cli.exe" -network signet -wallet CALIBER1 -fund-sat 3000000 -fee-sat 500000 -try-load-wallet -datadir "E:\Bitcoin\data" -conf "E:\Bitcoin\bitcoin-signet.conf" -max-wait-seconds 600

# 3c. Fee-profile: 5 fees × 1 seed = 5 runs (paper Table 4)
.\scripts\signet_fee_profiles.ps1 -BitcoinCli "E:\Bitcoin\daemon\bitcoin-cli.exe" -WalletName CALIBER1 -FundSat 500000

# 3d. Sweep leftover from CALIBER1 → CALIBER2
# (see onchain-signet guide for details)
```

## 4. Visualization

```powershell
# Generate all 20 publication PNGs + 3 interactive HTMLs
uv run scripts/plots/generate_all_plots.py

# Generate for signet output folder instead:
$env:PUBLICATION_SUBDIR = "signet"
uv run scripts/plots/generate_all_plots.py
```

**Output organization:**
```
artifacts/publication/
├── regtest/                # 20 PNGs (or signet/ if PUBLICATION_SUBDIR=signet)
│   ├── paper_evaluation_grid.png
│   ├── plot_01_cdf_box_violin.png
│   ├── ...
│   └── plot_18_radar_comparison.png
└── plotly/                 # 3 interactive HTMLs (network-independent)
    ├── interactive_caliber_width_vs_collateral.html
    ├── interactive_kappa_window_probability.html
    └── interactive_parallel_swaps_cnstar.html
```

Output paths are controlled via `scripts/plots/config.py`. Override with:
```powershell
$env:PUBLICATION_SUBDIR = "signet"    # targets artifacts/publication/signet/
```

## 5. Verification

```powershell
# Check artifact consistency and invariants
go run ./cmd/verify_artifacts

# Expected output: "artifact consistency checks passed"
```

## Expected Results

### Attack Decisions (analytical profile)

| Scheme | Miner accepts | Bob profits | Width (sat) |
|--------|:------------:|:----------:|:----------:|
| Naive CRAB+He | ✓ | ✓ | 2,500,000 |
| Collateral-only \(c'=2c\) | ✓ | ✓ | 2,500,000 |
| CALIBER \(c^*\) | ✗ | ✗ | 0 |

### On-Chain Evidence

| Network | Fee Range (sat) | Runs | Accepted |
|---------|:--------------:|:----:|:--------:|
| Regtest | 250–5000 | 15 | 15/15 |
| Signet  | 250–5000 | 5  | 5/5 |

## File Manifest After Full Pipeline

```
artifacts/
├── experiments/             (9 files)
├── onchain/regtest/fee_profiles/ (≈19 files)
├── onchain/signet/fee_profiles/  (≈9 files)
├── publication/regtest/     (20 PNGs)
├── publication/plotly/      (3 interactive HTMLs)
├── linked_acs_regtest.json
├── linked_acs_signet.json
├── caliber_results.{json,md}
├── submission_report.md
└── tx_size_evidence.{json,md}
```
