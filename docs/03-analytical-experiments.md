# CALIBER — Analytical Experiments

> **Parameter sweeps, payoff decisions, attack timeline, and baseline comparisons.**

This document describes the analytical (non-on-chain) experiments that validate the paper's core incentive claims. All experiments run entirely in Go with no Bitcoin node required.

## 1. Experiment A: Parameter Sweep

**Purpose:** Verify CLBA payoff invariants across a grid of parameter configurations.

**Command:**
```powershell
go run ./cmd/experiment_runner
```

**Grid dimensions** (144 total configurations):

| Parameter | Values |
|-----------|--------|
| \(v_{dep}/v\) | 0.01, 0.025, 0.05, 0.1 |
| \(v_{col}/v_{dep}\) | 0.5, 0.75, 1.0 |
| \(\kappa\) | 3, 5, 7 |
| \(n\) (parallel swaps) | 1, 3, 5, 7 |

**Outputs:**
- `artifacts/experiments/parameter_sweep.csv` — per-configuration width values
- `artifacts/experiments/experiment_summary.json` — full report

**Invariants tested:**
- Baseline width \(W = v + v_{dep} - v_{col} > 0\) for all valid parameters
- Collateral-only width \(W(c')\) independent of \(c'\)
- CALIBER transition at \(c^* = v + v_{dep}\)
- Multi-swap threshold \(c^*_n = v + n \cdot v_{dep}\)

## 2. Experiment B: Collateral-Only Impossibility

**Purpose:** Directly verify that increasing collateral alone cannot close the bribery interval.

**Approach:** Compute payoff boundaries for:
- Baseline: \(c = v\)
- Inflated: \(c' = 2c, 1.25c, 1.5c\)

**Key result:**
```
Baseline:        W = (v + c + v_dep) - (c + v_col) = v + v_dep - v_col
Inflated (c'=2c): W = (v + 2c + v_dep) - (2c + v_col) = v + v_dep - v_col
→ Width invariant under collateral inflation (Theorem 2)
```

## 3. Experiment C: CALIBER Threshold

**Purpose:** Verify threshold behavior around \(c^* = v + v_{dep}\).

**Approach:** Test three collateral values for each configuration:
- \(c^* - \varepsilon\) (1,000 sat below)
- \(c^*\) (exact threshold)
- \(c^* + \varepsilon\) (1,000 sat above)

**Key result at analytical profile (v=2.5M, v_dep=500K, v_col=500K):**

| Collateral | Width (sat) | Attack Feasible |
|------------|:----------:|:---------------:|
| \(c^* - 1,000\) | 1,000 | Yes |
| \(c^*\) | 0 | No |
| \(c^* + 1,000\) | -1,000 | No |

## 4. Experiment D: SDRBA-Style Payoff Decision

**Purpose:** Convert payoff inequalities into explicit accept/reject decisions.

**Command:** (included in `go run ./cmd/experiment_runner`)

**Output:** `artifacts/experiments/attack_decisions.json`

Each decision record contains:
- `scheme` — name of the evaluated scheme
- `offeredBrSat` — bribe value at midpoint of feasible interval
- `bobUbSat` / `minerLbSat` — payoff boundaries
- `widthSat` — feasible bribe interval width
- `minerAccepts` / `bobProfits` — individual rationality checks
- `jointlyProfitable` — true if both benefit
- `decisionRule` — inequality used for boundary computation

**Results at analytical profile:**

| Scheme | Miner-LB | Bob-UB | Width | Jointly |
|--------|---------|-------|:----:|:-------:|
| Naive CRAB+He | 3,000,000 | 5,500,000 | 2,500,000 | ✓ |
| Collateral-only \(c'=2c\) | 5,500,000 | 8,000,000 | 2,500,000 | ✓ |
| CALIBER \(c^* - \varepsilon\) | 2,999,000 | 3,000,000 | 1,000 | ✓ |
| CALIBER \(c^*\) | 3,000,000 | 3,000,000 | 0 | ✗ |
| CALIBER \(c^* + \varepsilon\) | 3,001,000 | 3,000,000 | -1,000 | ✗ |

## 5. Experiment E: Deterministic Attack Timeline

**Purpose:** Replay the CLBA narrative under both baseline and CALIBER defense.

**Command:** (included in `go run ./cmd/experiment_runner`)

**Outputs:**
- `artifacts/experiments/attack_timeline.json` — detailed per-scenario timeline
- `artifacts/experiments/attack_timeline.csv` — summary rows

**Baseline (Naive CRAB+He) replay phases:**

1. **Off-chain:** Bob offers BR to one actively rational miner
2. **Stale state broadcast:** Bob publishes old `tx_commit_A[j_old]`
3. **Censorship:** Miner censors `tx_revoke_ACS` and `tx_dep_A`
4. **Claim:** Bob claims channel value + HTLC value, pays BR

**CALIBER replay phases:**

1. **Off-chain:** Bob searches for BR but interval is empty
2. **Stale state attempt:** Bob must broadcast `dep-B` to claim HTLC value
3. **dep-B trigger:** `pre_b` becomes public; linked ACS spend fires
4. **Terminal state:** Linked output burned; Bob cannot redirect collateral

## 6. Experiment F: Baseline Pipelines

**Purpose:** Compare transaction-level costs across protocol baselines.

**Output:** `artifacts/experiments/baseline_pipelines.json`

Each pipeline records transaction stages, vBytes, and feasibility for:
- **MAD-HTLC standalone** — lock → claim_A (364 vB total)
- **He-HTLC standalone** — dep_A → col_M (358 vB total)
- **CALIBER** — commit_A (linked) → revoke_linked (527 vB total)

## 7. Experiment G: Kappa-Window Diagnostic

**Purpose:** Validate the inherited honest-inclusion probability from He-HTLC.

**Approach:** Monte Carlo simulation across \(\kappa\) window sizes.

| \(\rho_h\) | \(\kappa\) | Analytical | Simulated | Abs Diff |
|:---------:|:--------:|:----------:|:---------:|:--------:|
| 0.30 | 3 | 0.6570 | 0.6568 | 0.03% |
| 0.30 | 5 | 0.8319 | 0.8282 | 0.45% |
| 0.30 | 7 | 0.9176 | 0.9165 | 0.12% |
| 0.50 | 3 | 0.8750 | 0.8749 | 0.01% |
| 0.50 | 5 | 0.9688 | 0.9685 | 0.03% |
| 0.50 | 7 | 0.9922 | 0.9920 | 0.02% |

## 8. Data Flow

```
cmd/experiment_runner/
  ├── internal/attack/payoff.go           → DecisionReport
  ├── internal/experiments/grid.go        → Sweep rows
  ├── internal/experiments/attack_timeline.go → TimelineReport
  └── internal/experiments/baselines.go   → Pipeline baselines
```

## 9. Expected Output Files

| File | Size (approx) | Contents |
|------|:-------------:|----------|
| `experiment_summary.json` | 840 KB | Full report with all sub-results |
| `parameter_sweep.csv` | 25 KB | 144-row parameter grid |
| `attack_decisions.json` | 3 KB | 5 decision rows |
| `attack_timeline.json` | 4 KB | 2 scenarios × 4 events each |
| `parallel_swaps_table.csv` | 100 B | n=1,3,5,7 scaling |
| `baseline_pipelines.json` | 484 KB | All baselines per config |
| `kappa_window_table.csv` | 550 B | 9 simulation rows |
