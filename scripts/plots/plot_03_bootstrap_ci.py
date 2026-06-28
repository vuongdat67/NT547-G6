# /// script
# dependencies = ["numpy", "matplotlib", "scipy", "seaborn"]
# ///
from config import FIGURES_DIR, PLOTLY_DIR

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import bootstrap

os.makedirs("artifacts/publication", exist_ok=True)

try:
    import scienceplots
    plt.style.use(['science', 'ieee', 'no-latex'])
except ImportError:
    plt.style.use('default')

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

with open("artifacts/experiments/experiment_summary.json", "r") as f:
    data = json.load(f)
dists = data['telemetry']['witnessGenerationDistributions']

leaves_list = []
means = []
ci_lows = []
ci_highs = []

for d in dists:
    l = d['leaves']
    vals = np.array(d['timesMicros'])
    mean_val = np.mean(vals)
    res = bootstrap((vals,), np.mean, n_resamples=10000, confidence_level=0.95)
    leaves_list.append(l)
    means.append(mean_val)
    ci_lows.append(mean_val - res.confidence_interval.low)
    ci_highs.append(res.confidence_interval.high - mean_val)

fig, ax = plt.subplots(figsize=(6, 4))
ax.errorbar(leaves_list, means, yerr=[ci_lows, ci_highs], fmt='-o', 
            color="#d62728", capsize=5, capthick=2, linewidth=2, markersize=8)
ax.set_title("3. Bootstrap CI Error Bars: Overhead vs Leaves (95% CI)")
ax.set_xlabel("Number of Leaves")
ax.set_ylabel("Witness Generation Time (µs)")
ax.set_xticks(leaves_list)
ax.grid(True, linestyle="--", alpha=0.5)
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "plot_03_bootstrap_ci.png"), dpi=300)
