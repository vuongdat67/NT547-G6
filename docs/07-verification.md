# CALIBER — Verification and Reproducibility

> **Artifact consistency checks, submission report, and reproducibility checklist.**

## 1. Artifact Verification

The `verify_artifacts` command checks:
1. All required artifact files exist
2. Key invariants hold (analytical and on-chain)

```powershell
go run ./cmd/verify_artifacts
```

**Expected output:**
```
artifact consistency checks passed
```

### Checks Performed

| Check | What It Validates |
|-------|-------------------|
| `parameter_sweep.csv` exists | Experiment A completed |
| `baseline_pipelines.json` exists | Baseline comparisons available |
| `kappa_window_table.csv` exists | Kappa diagnostic complete |
| `parallel_swaps_table.csv` exists | Multi-swap scaling computed |
| `regtest_fee_profiles.ps1` exists | Fee campaign script available |
| `signet_fee_profiles.ps1` exists | Fee campaign script available |
| `linked_acs_regtest.json` exists | Regtest evidence available |
| `linked_acs_signet.json` exists | Signet evidence available |
| `c* = v + v_dep` in `attack_decisions.json` | Threshold invariant |
| Naive CRAB+He jointly profitable | Baseline claim holds |
| CALIBER at c* not jointly profitable | Defense claim holds |
| Baseline timeline width > 0 | Attack exists |
| CALIBER timeline width = 0 | Defense succeeds |
| 15 fee profile runs per network | Campaign completeness |
| All fee profile runs accepted | Campaign success |

## 2. Submission Report

Generates a reviewer-facing Markdown summary of all artifacts.

```powershell
go run ./cmd/submission_report
```

**Output:** `artifacts/submission_report.md`

**Sections:**
1. Attack timeline replay (baseline vs CALIBER)
2. Parallel independent swaps (n=1,3,5,7)
3. Linked ACS evidence (regtest + signet TxIDs, fees, burn)
4. Fee-profile campaign (acceptance rates per network)
5. Explicit non-claims (scope boundaries)

## 3. Reproducibility Checklist

### Prerequisites

- [ ] Go 1.23+
- [ ] Python 3.11+ with `uv`
- [ ] Git clone of repository
- [ ] For on-chain only: Bitcoin Core 27+, regtest/signet node running

### Analytical (No Bitcoin Node)

- [ ] `go test ./...` — all tests pass
- [ ] `go run ./cmd/experiment_runner` — grid, decisions, timeline, kappa
- [ ] `go run ./cmd/experiment_runner_m2` — parameter sensitivity
- [ ] `go run ./cmd/eval_report` — tx table, CLBA summary, coalition diagnostic
- [ ] `go run ./cmd/publish_results` — LaTeX tables, SVG figures
- [ ] `go run ./cmd/submission_report` — reviewer report
- [ ] `go run ./cmd/verify_artifacts` — all checks pass (expected: missing on-chain artifacts reported, analytical checks pass)

### On-Chain Regtest

- [ ] Wallet `CALIBER` created and funded (101 blocks)
- [ ] Single linked ACS deploy succeeds (Table 3)
- [ ] Fee profile campaign: 5 fees × 3 seeds = 15/15 accepted (Table 4)
- [ ] Variance data: 10 runs via orchestrator

### On-Chain Signet

- [ ] Wallet `CALIBER1` (experiment) and `CALIBER2` (vault) created
- [ ] CALIBER1 funded with ≥0.06 BTC
- [ ] Single linked ACS deploy succeeds (Table 3)
- [ ] Fee profile campaign: 5 fees × 1 seed = 5/5 accepted (Table 4)
- [ ] Leftovers swept from CALIBER1 → CALIBER2

### Visualization

- [ ] `uv run scripts/plots/generate_all_plots.py` — all 18 plots generated
- [ ] Plot images readable in `artifacts/publication/`

### Final Verification

- [ ] `go run ./cmd/verify_artifacts` — "artifact consistency checks passed"

## 4. Claim-to-Artifact Mapping

| Paper Claim | Primary Artifact | Invariant Checked |
|-------------|-----------------|-------------------|
| CLBA positive interval exists | `attack_decisions.json`, `attack_timeline.csv` | Width > 0 for baseline |
| Collateral-only fails | `attack_decisions.json`, `parameter_sweep.csv` | Width unchanged at \(c' = 2c\) |
| CALIBER closes interval | `attack_decisions.json` | Width = 0 at \(c^*\) |
| Linked ACS script-feasible | `linked_acs_regtest.json`, `linked_acs_signet.json` | Fund + spend confirmed |
| Fee-profile succeeds | `fee_profile_summary.csv` | 15/15 accepted per network |
| Parallel swaps linear | `parallel_swaps_table.csv` | \(c^*_n = v + n \cdot v_{dep}\) |
| Overhead minimal | `tx_size_evidence.json` | Commit = 281 vB (−2 vs CRAB) |

## 5. File Integrity

After full pipeline execution, the following files MUST exist:

```
artifacts/
├── experiments/
│   ├── attack_decisions.json
│   ├── attack_timeline.csv
│   ├── attack_timeline.json
│   ├── baseline_pipelines.json
│   ├── experiment_summary.json
│   ├── kappa_window_table.csv
│   ├── multi_hop_table.csv
│   ├── parallel_swaps_table.csv
│   ├── parameter_sweep.csv
│   └── regtest_variance.csv
├── onchain/
│   └── regtest/
│       └── fee_profiles/
│           ├── fee_profile_summary.csv
│           ├── fee_profile_summary.json
│           └── fee_*_seed_*.json (15 files)
├── crab_he_results.json
├── crab_he_results.md
├── linked_acs_regtest.json
├── submission_report.md
├── tx_size_evidence.json
├── tx_size_evidence.md
└── publication/
    ├── fig_parallel_swaps_cnstar.svg
    ├── publication_manifest.json
    ├── table_parallel_swaps.tex
    └── plot_*.png (18 files)
```

## 6. Invariant Summary

Key analytical invariants (verified by `verify_artifacts`):

1. **Baseline profitability:** Naive CRAB+He has width > 0 for all valid parameters
2. **Collateral neutrality:** Width unchanged under \(c'\) inflation
3. **CALIBER threshold:** At \(c^* = v + v_{dep}\), width = 0
4. **Single-miner bound:** The CALIBER composed security model is the single-miner bound (Theorem 3), not a coalition-splitting analysis
5. **He-HTLC validity:** All evaluated parameter points satisfy \(\kappa > 2\) and \(v_{col} \in [\lceil v_{dep}/(\kappa-1)\rceil, v_{dep}]\)
