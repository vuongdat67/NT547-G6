# CALIBER — Visualization Guide

> **20 publication-quality plots + 3 interactive HTMLs from analytical and on-chain artifacts.**

## 1. Quick Start

```powershell
uv run scripts/plots/generate_all_plots.py
```

**Output:** All PNG files written to `artifacts/publication/regtest/`, interactive HTMLs to `artifacts/publication/plotly/`.

**To target a different network folder:**
```powershell
$env:PUBLICATION_SUBDIR = "signet"
uv run scripts/plots/generate_all_plots.py
# → outputs to artifacts/publication/signet/
```

The output directory is controlled by `scripts/plots/config.py`, which reads the `PUBLICATION_SUBDIR` environment variable (default: `regtest`).

**Dependencies:** Automatically managed by `uv` via PEP 723 inline script metadata. Each plot script declares its own dependencies.

## 2. Plot Directory

| # | File | Technique | Data Source | Key Insight |
|:-:|------|-----------|-------------|-------------|
| 00 | `paper_evaluation_grid.png` | 6-panel combined figure | Multiple sources | CLBA width, swaps, kappa, tx sizes, bribery, telemetry |
| 01 | `plot_01_cdf_box_violin.png` | CDF + Boxplot + Violin | `regtest_variance.csv` | Latency distribution overview |
| 02 | `plot_02_raincloud.png` | Raincloud (half-violin + jitter + box) | `regtest_variance.csv` | Dense distribution visualization |
| 03 | `plot_03_bootstrap_ci.png` | Bootstrap CI error bars | `experiment_summary.json` | Witness generation overhead vs tree depth |
| 04 | `plot_04_ridgeline.png` | Ridgeline (joyplot) | `kappa_window_sim.json` | Success probability by \(\kappa\) |
| 05 | `plot_05_heatmap.png` | 2D heatmap | `parameter_sweep.csv` | Attack width vs \(v_{dep}, v_{col}\) |
| 06 | `plot_06_beeswarm.png` | Beeswarm + violin overlay | `experiment_summary.json` | Witness generation time distribution |
| 07 | `plot_07_split_violin.png` | Split violin (hue comparison) | `experiment_summary.json` | Witness gen vs script validation |
| 08 | `plot_08_stat_annotation.png` | Boxplot + Mann-Whitney U | `experiment_summary.json` | Statistical significance of differences |
| 09 | `plot_09_gantt_attack.png` | Gantt (broken barh) | Hardcoded CLBA phases | Attack timeline visualization |
| 10 | `plot_10_env_comparison.png` | CDF overlay + split violin | `regtest_variance.csv` | Regtest vs signet latency comparison |
| 11 | `plot_11_joint_marginal.png` | Jointplot with hexbin + KDE | `experiment_summary.json`, `regtest_variance.csv` | Latency vs overhead correlation |
| 12 | `plot_12_cumulative_scatter.png` | Throughput + anomaly scatter | `regtest_variance.csv` | Cumulative processing and anomaly detection |
| 13 | `plot_13_head_to_head_overhead.png` | 3-panel: CDF, box, violin | `experiment_summary.json` | Computational overhead by tree depth |
| 14a | `plot_14a_ecg_duration.png` | ECG (rolling avg + bands) | `repeated_onchain_runs.csv` | Deployment duration stability (100 runs) |
| 14b | `plot_14b_ecg_latency.png` | ECG (rolling avg + bands) | `regtest_variance.csv` | E2E latency variance with \(\pm 2\sigma\) bands |
| 15 | `plot_15_attack_trajectory.png` | Multi-panel time-series | Synthetic (hardcoded) | Reputation, voting power, accuracy under attack |
| 16 | `plot_16_multi_baseline_longitudinal.png` | Multi-baseline line plot | Synthetic (hardcoded) | CALIBER vs 5 baselines over epochs |
| 17 | `plot_17_sankey_fund_flow.png` | Sankey diagram | Hardcoded CALIBER flow | Fund flow and collateral burn mechanism |
| 18 | `plot_18_radar_comparison.png` | Radar/spider chart | Hardcoded | 6-dimensional protocol capability comparison |

### Interactive HTMLs

| File | Content | Data Source |
|------|---------|-------------|
| `interactive_caliber_width_vs_collateral.html` | CLBA width vs collateral sweep | `parameter_sweep.csv` |
| `interactive_kappa_window_probability.html` | Kappa window confirmation prob | `kappa_window_table.csv` |
| `interactive_parallel_swaps_cnstar.html` | Parallel swaps collateral threshold | `parallel_swaps_table.csv` |

## 3. Data Source Details

### From Analytical Pipeline

| Source File | Used By | Key Columns |
|-------------|---------|-------------|
| `experiment_summary.json` | 03, 04, 06, 07, 08, 11, 13 | `telemetry.witnessGenerationDistributions`, `telemetry.scriptValidationDistributions` |
| `kappa_window_sim.json` | 04 | `rows[].simulatedProbMean`, `rows[].kappa` |
| `parameter_sweep.csv` | 00, 05 | `v_dep_sat`, `v_col_sat`, `width_caliber_cstar` |
| `parallel_swaps_table.csv` | 00 (interactive) | `n`, `c_n_star_sat` |
| `kappa_window_table.csv` | 00 (interactive) | `kappa`, `simulated_prob_mean`, `rho_h` |

### From On-Chain Pipeline

| Source File | Used By | Key Columns |
|-------------|---------|-------------|
| `regtest_variance.csv` | 01, 02, 10, 11, 12, 14b | `latency_ms`, `timestamp`, `run_id` |
| `repeated_onchain_runs.csv` | 14a | `duration_ms`, `spend_vbytes`, `run_idx` |

### Hardcoded (No External Data)

| Plot | Reason |
|------|--------|
| 09 (Gantt) | Attack timeline is protocol-defined, not measured |
| 15 (Attack trajectory) | Synthetic Byzantine behavior model |
| 16 (Multi-baseline) | Comparative longitudinal evaluation |
| 17 (Sankey) | Protocol fund flow diagram |
| 18 (Radar) | Multi-dimensional capability comparison |

## 4. Individual Plot Commands

Run any single plot for faster iteration:

```powershell
uv run scripts/plots/plot_01_cdf_box_violin.py
uv run scripts/plots/plot_06_beeswarm.py
uv run scripts/plots/plot_18_radar_comparison.py

# Target signet output:
$env:PUBLICATION_SUBDIR = "signet"
uv run scripts/plots/plot_00_evaluation_grid.py
```

## 5. Interactive HTML Plots

The 3 interactive Plotly HTMLs support:
- Hover tooltips with exact values
- Zoom/pan for detailed inspection
- Toggle traces on/off
- Export to PNG from the plot toolbar

Open them directly in any modern web browser.

## 6. Styling

All plots use:
- IEEE-compatible styling (via `scienceplots` library when available)
- Serif font (Times New Roman / DejaVu Serif)
- Consistent grid, label sizing, and color palettes
- Colorblind-friendly palette selections

```python
# Academic plot settings
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})
```

## 7. Color Palette

| Role | Hex | Name |
|------|:---:|------|
| Naive CRAB baseline | `#2ca02c` | Green |
| CALIBER (ours) | `#9467bd` | Purple |
| Key markers/critical | `#d62728` | Red |
| Fill/highlight | `#e0cff5` | Light purple |
| Secondary/gray | `#7f7f7f` | Gray |
