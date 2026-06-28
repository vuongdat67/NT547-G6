# CALIBER — Visualization Guide

> **18 publication-quality plots from analytical and on-chain artifacts.**

## 1. Quick Start

```powershell
uv run scripts/plots/generate_all_plots.py
```

**Output:** All PNG files written to `artifacts/publication/`.

**Dependencies:** Automatically managed by `uv` via PEP 723 inline script metadata. Each plot script declares its own dependencies.

## 2. Plot Directory

| # | File | Technique | Data Source | Key Insight |
|:-:|------|-----------|-------------|-------------|
| 01 | `plot_01_cdf_box_violin.png` | CDF + Boxplot + Violin | `regtest_variance.csv` | Latency distribution overview |
| 02 | `plot_02_raincloud.png` | Raincloud (half-violin + jitter + box) | `regtest_variance.csv` | Dense distribution visualization |
| 03 | `plot_03_bootstrap_ci.png` | Bootstrap CI error bars | `experiment_summary.json` | Witness generation overhead vs tree depth |
| 04 | `plot_04_ridgeline.png` | Ridgeline (joyplot) | `kappa_window_sim.json` | Success probability by \(\kappa\) |
| 05 | `plot_05_heatmap.png` | 2D heatmap | `parameter_sweep.csv` | Attack width vs \(v_{dep}, v_{col}\) |
| 06 | `plot_06_beeswarm.png` | Beeswarm + violin overlay | `experiment_summary.json` | Witness generation time distribution |
| 07 | `plot_07_split_violin.png` | Split violin (hue comparison) | `experiment_summary.json` | Witness gen vs script validation |
| 08 | `plot_08_stat_annotation.png` | Boxplot + Mann-Whitney U | `experiment_summary.json` | Statistical significance of differences |
| 09 | `plot_09_gantt_attack.png` | Gantt (broken barh) | Hardcoded CLBA phases | Attack timeline visualization |
| 10 | `plot_10_env_comparison.png` | CDF overlay + split violin | `regtest_variance.csv` | Regtest vs simulated signet latency |
| 11 | `plot_11_joint_marginal.png` | Jointplot with hexbin + KDE | `experiment_summary.json`, `regtest_variance.csv` | Latency vs overhead correlation |
| 12 | `plot_12_cumulative_scatter.png` | Throughput + anomaly scatter | `regtest_variance.csv` | Cumulative processing and anomaly detection |
| 13 | `plot_13_head_to_head_overhead.png` | 3-panel: CDF, box, violin | `experiment_summary.json` | Computational overhead by tree depth |
| 14 | `plot_21_academic_ecg.png` | ECG (latency + size variation) | `repeated_onchain_runs.csv` | Deployment stability and variance |
| 15 | `plot_15_attack_trajectory.png` | Multi-panel time-series | Synthetic (hardcoded) | Reputation, voting power, accuracy under attack |
| 16 | `plot_16_multi_baseline_longitudinal.png` | Multi-baseline line plot | Synthetic (hardcoded) | CALIBER vs 5 baselines over epochs |
| 17 | `plot_17_sankey_fund_flow.png` | Sankey diagram | Hardcoded CALIBER flow | Fund flow and collateral burn mechanism |
| 18 | `plot_18_radar_comparison.png` | Radar/spider chart | Hardcoded | 6-dimensional protocol capability comparison |

## 3. Data Source Details

### From Analytical Pipeline

| Source File | Used By | Key Columns |
|-------------|---------|-------------|
| `experiment_summary.json` | 03, 04, 06, 07, 08, 11, 13 | `telemetry.witnessGenerationDistributions`, `telemetry.scriptValidationDistributions` |
| `kappa_window_sim.json` | 04 | `rows[].simulatedProbMean`, `rows[].kappa` |
| `parameter_sweep.csv` | 05 | `v_dep_sat`, `v_col_sat`, `width_caliber_cstar` |

### From On-Chain Pipeline

| Source File | Used By | Key Columns |
|-------------|---------|-------------|
| `regtest_variance.csv` | 01, 02, 10, 11, 12 | `latency_ms`, `timestamp`, `run_id` |
| `repeated_onchain_runs.csv` | 14 | `duration_ms`, `spend_vbytes`, `run_idx` |

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
```

## 5. Publication Output

Generated files in `artifacts/publication/`:

- **PNG figures:** 18 plots at 300 DPI
- **LaTeX table:** `table_parallel_swaps.tex`
- **SVG figure:** `fig_parallel_swaps_cnstar.svg`
- **Manifest:** `publication_manifest.json`

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
