# /// script
# dependencies = ["numpy", "pandas", "matplotlib", "seaborn"]
# ///
from config import FIGURES_DIR, PLOTLY_DIR

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
rows = []
for d in dists:
    leaves = d['leaves']
    vals = d['timesMicros']
    for v in vals:
        rows.append({"Leaves": f"{leaves} Leaves", "Overhead": v})

df_comp = pd.DataFrame(rows)

fig2, (ax3, ax4, ax5) = plt.subplots(1, 3, figsize=(12, 4), layout='constrained')
colors = {"1 Leaves": "#2ca02c", "2 Leaves": "#ff7f0e", "4 Leaves": "#1f77b4", "8 Leaves": "#d62728"}

# Panel A: Comparative CDF
sns.ecdfplot(data=df_comp, x='Overhead', hue='Leaves', ax=ax3, palette=colors, linewidth=2)
ax3.set_title("(a) CDF of Witness Generation Time")
ax3.set_xlabel("Time (µs)")
ax3.set_ylabel("CDF")
ax3.grid(True)

# Panel B: Comparative Boxplot
sns.boxplot(data=df_comp, x='Leaves', y='Overhead', hue='Leaves', palette=colors, ax=ax4, width=0.4, showfliers=True, legend=False)
ax4.set_title("(b) Dispersion (Boxplot)")
ax4.set_ylabel("Time (µs)")
ax4.grid(True, axis='y')

# Panel C: Comparative Violin Plot
sns.violinplot(data=df_comp, x='Leaves', y='Overhead', hue='Leaves', palette=colors, ax=ax5, inner="box", linewidth=1.2, legend=False)
ax5.set_title("(c) Distribution (Violin)")
ax5.set_ylabel("Time (µs)")
ax5.grid(True, axis='y')

fig2.suptitle("Head-to-Head Comparison: Computational Overhead by Tree Depth", fontsize=14, fontweight='bold')
out2 = os.path.join(FIGURES_DIR, "plot_13_head_to_head_overhead.png")
fig2.savefig(out2, dpi=300, facecolor="white")
plt.close(fig2)
