# /// script
# dependencies = [
#   "numpy",
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "scienceplots"
# ]
# ///
from config import FIGURES_DIR, PLOTLY_DIR

"""
CALIBER Protocol — 6-panel evaluation grid (paper figure).
Combines CLBA width, parallel swaps, kappa window, tx sizes, bribery collapse, telemetry.
"""

import os, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

os.makedirs(FIGURES_DIR, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────
df_sweep = pd.read_csv("artifacts/experiments/parameter_sweep.csv")
df_swaps = pd.read_csv("artifacts/experiments/parallel_swaps_table.csv")
df_kappa = pd.read_csv("artifacts/experiments/kappa_window_table.csv")

with open("artifacts/caliber_results.json") as f:
    results_data = json.load(f)

with open("artifacts/experiments/experiment_summary.json") as f:
    exp_summary = json.load(f)

# ── Style ──────────────────────────────────────────────────────────
try:
    import scienceplots
    plt.style.use(["science", "ieee", "no-latex"])
except Exception:
    plt.style.use("default")

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8,
    "figure.titlesize": 14,
    "lines.linewidth": 1.5,
    "lines.markersize": 5,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})

C_NAIVE   = "#2ca02c"     # green — naive CRAB
C_CALIBER = "#9467bd"     # purple — CALIBER (ours)
C_MARKER  = "#d62728"     # red — key markers
C_FILL    = "#e0cff5"     # light purple fill
C_GRAY    = "#7f7f7f"     # gray for secondary

fig, axes = plt.subplots(3, 2, figsize=(7.16, 9.5))

# ── Panel (a): CLBA Width vs Collateral ────────────────────────────
ax = axes[0, 0]
v_sat = 2_000_000
v_dep_sat = 1_000_000
v_col_sat = 500_000
c_range = np.linspace(1.0 * v_sat, 2.5 * v_sat, 200)
naive_width = np.full_like(c_range, (v_sat + v_dep_sat - v_col_sat) / 1e6)
caliber_width = ((v_sat + v_dep_sat) - c_range) / 1e6

ax.plot(c_range / 1e6, naive_width, "-", color=C_NAIVE, linewidth=2, label="Naive CRAB")
ax.plot(c_range / 1e6, caliber_width, "-", color=C_CALIBER, linewidth=2, label="CALIBER")
ax.axhline(0, color=C_GRAY, linewidth=0.8, linestyle="-")
ax.fill_between(c_range / 1e6, caliber_width, 0,
                where=(caliber_width > 0), color=C_FILL, alpha=0.4)
c_star = (v_sat + v_dep_sat) / 1e6
ax.axvline(c_star, color=C_MARKER, linewidth=1.2, linestyle="--")
ax.annotate(r"$c^{\star}$", xy=(c_star, 0), xytext=(c_star + 0.15, 0.8),
            fontsize=10, color=C_MARKER, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=C_MARKER, lw=1.5))
ax.set_xlabel("Collateral $c'$ ($10^6$ sat)")
ax.set_ylabel("Attack Width ($10^6$ sat)")
ax.set_title("(a) CLBA Width vs. Collateral")
ax.legend(loc="upper right", framealpha=0.9)
ax.grid(True)

# ── Panel (b): Parallel Swaps ──────────────────────────────────────
ax = axes[0, 1]
n_vals = df_swaps["n"].values
c_star_vals = df_swaps["c_n_star_sat"].values / 1e6
ax.plot(n_vals, c_star_vals, "o-", color=C_CALIBER, linewidth=2, markersize=7,
        markeredgecolor="black", markeredgewidth=0.8)
for i, row in df_swaps.iterrows():
    ax.annotate(f"{row['c_n_star_sat']/1e6:.1f}M",
                (row["n"], row["c_n_star_sat"]/1e6),
                textcoords="offset points", xytext=(8, -3), fontsize=8, fontweight="bold")
ax.set_xticks(n_vals)
ax.set_xlim(0, 8)
ax.set_ylim(bottom=0)
ax.set_xlabel("Number of parallel swaps ($n$)")
ax.set_ylabel(r"$c_n^{\star}$ ($10^6$ sat)")
ax.set_title("(b) Collateral Threshold vs. Swaps")
ax.grid(True)

# ── Panel (c): Kappa Window ────────────────────────────────────────
ax = axes[1, 0]
markers = ["o", "s", "^"]
for idx, (rho, grp) in enumerate(df_kappa.groupby("rho_h")):
    x = grp["kappa"].values
    y_mean = grp["simulated_prob_mean"].values
    y_std = grp["simulated_prob_std"].values
    y_ana = grp["analytical_prob"].values
    p = ax.errorbar(x, y_mean, yerr=2*y_std, fmt=f"{markers[idx]}-",
                    capsize=4, capthick=1.2, linewidth=1.5,
                    label=rf"$\rho_H = {rho:.1f}$ (sim $\pm 2\sigma$)")
    color = p[0].get_color()
    ax.plot(x, y_ana, "--", color=color, alpha=0.5, linewidth=1)
ax.set_xticks([3, 5, 7])
ax.set_xlabel(r"Security window $\kappa$ (blocks)")
ax.set_ylabel("Honest confirmation probability")
ax.set_title(r"(c) Linked ACS Confirmation ($\bar{x} \pm 2\sigma$)")
ax.legend(loc="lower right", framealpha=0.9, fontsize=7)
ax.grid(True)

# ── Panel (d): Transaction Sizes ───────────────────────────────────
ax = axes[1, 1]
tx_data = []
for tx in results_data["txTable"]:
    name = tx["name"].replace("tx_", "")
    size = tx["vbytes"]
    phase = "HTLC"
    if "commit" in name or "fund" in name:
        phase = "Setup"
    elif "revoke" in name:
        phase = "Punishment"
    tx_data.append({"name": name, "size": size, "phase": phase})
df_tx = pd.DataFrame(tx_data).sort_values(["phase", "size"], ascending=[True, True])
phase_map = {"Setup": C_CALIBER, "Punishment": C_MARKER, "HTLC": C_GRAY}
y_pos = np.arange(len(df_tx))
bars = ax.barh(y_pos, df_tx["size"],
               color=[phase_map[p] for p in df_tx["phase"]],
               edgecolor="black", linewidth=0.5, height=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(df_tx["name"], fontsize=7)
ax.bar_label(bars, fmt="%d vB", padding=4, fontsize=7)
legend_h = [Patch(facecolor=c, edgecolor="black", label=p) for p, c in phase_map.items()]
ax.legend(handles=legend_h, loc="lower right", fontsize=7, title="Phase", title_fontsize=8)
ax.set_xlabel("Transaction size (vbytes)")
ax.set_title("(d) CALIBER Transaction Sizes")
ax.grid(True, axis="x")

# ── Panel (e): Bribery Interval Collapse ───────────────────────────
ax = axes[2, 0]
naive_lb = v_col_sat / 1e6
naive_ub = (v_sat + v_dep_sat) / 1e6
cal_point = c_star
ax.plot([naive_lb, naive_ub], [1, 1], color=C_NAIVE, linewidth=6,
        solid_capstyle="round", label="Naive CRAB interval")
ax.plot(cal_point, 0, "o", color=C_CALIBER, markersize=12,
        markeredgecolor="black", markeredgewidth=1.2, label="CALIBER (width = 0)")
ax.annotate(f"LB = {naive_lb}M", xy=(naive_lb, 1),
            xytext=(naive_lb - 0.1, 1.35), ha="center", fontsize=8,
            arrowprops=dict(arrowstyle="-|>", color="black", lw=1))
ax.annotate(f"UB = {naive_ub}M", xy=(naive_ub, 1),
            xytext=(naive_ub + 0.1, 1.35), ha="center", fontsize=8,
            arrowprops=dict(arrowstyle="-|>", color="black", lw=1))
ax.annotate("", xy=(cal_point, 0.15), xytext=(naive_ub, 0.85),
            arrowprops=dict(arrowstyle="->", color=C_CALIBER, lw=2, linestyle="--"))
ax.annotate(f"Interval collapses\n$c^{{\\star}} = {cal_point}$M",
            xy=(cal_point, 0), xytext=(cal_point - 0.8, -0.45),
            ha="center", fontsize=8, color=C_CALIBER, fontweight="bold")
ax.set_yticks([0, 1])
ax.set_yticklabels(["CALIBER", "Naive CRAB"])
ax.set_ylim(-0.8, 1.8)
ax.set_xlim(-0.2, 4.0)
ax.set_xlabel("Bribe value ($10^6$ sat)")
ax.set_title("(e) Bribery Interval Collapse")
ax.grid(True, axis="x")
ax.legend(loc="upper right", fontsize=7)

# ── Panel (f): Crypto Telemetry ────────────────────────────────────
ax = axes[2, 1]
tel = exp_summary["telemetry"]
leaves_list, w_means, w_stds, s_means, s_stds = [], [], [], [], []
for dist in tel["witnessGenerationDistributions"]:
    leaves_list.append(dist["leaves"])
    t = np.array(dist["timesMicros"])
    w_means.append(np.mean(t))
    w_stds.append(np.std(t))
for dist in tel["scriptValidationDistributions"]:
    t = np.array(dist["timesMicros"])
    s_means.append(np.mean(t))
    s_stds.append(np.std(t))
x = np.arange(len(leaves_list))
w = 0.35
bars_w = ax.bar(x - w/2, w_means, w, yerr=w_stds, capsize=4,
                color=C_CALIBER, edgecolor="black", linewidth=0.5, label="Witness Gen")
bars_s = ax.bar(x + w/2, s_means, w, yerr=s_stds, capsize=4,
                color=C_GRAY, edgecolor="black", linewidth=0.5, label="Script Val")
ax.set_xticks(x)
ax.set_xticklabels([str(l) for l in leaves_list])
ax.set_xlabel("Taproot leaves ($O(\\log N)$ depth)")
ax.set_ylabel("Execution time (µs)")
ax.set_title(r"(f) Crypto Telemetry ($\bar{x} \pm \sigma$, N=1000)")
ax.legend(loc="upper left", fontsize=7)
ax.grid(True, axis="y")

# ── Save ───────────────────────────────────────────────────────────
fig.suptitle("CALIBER: Evaluation Grid", fontweight="bold", y=1.01)
plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "paper_evaluation_grid.png"), dpi=300,
            bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved: {FIGURES_DIR}/paper_evaluation_grid.png")
