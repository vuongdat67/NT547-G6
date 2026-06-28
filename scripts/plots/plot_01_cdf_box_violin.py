# /// script
# dependencies = ["numpy", "pandas", "matplotlib", "seaborn", "scipy"]
# ///
from config import FIGURES_DIR, PLOTLY_DIR

import os
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

df = pd.read_csv("artifacts/experiments/regtest_variance.csv")

fig, axes = plt.subplots(1, 3, figsize=(12, 4))
sns.ecdfplot(data=df, x='latency_ms', ax=axes[0], color='#2ca02c', linewidth=2)
axes[0].set_title("(a) ECDF (Distribution of Latency)")
axes[0].set_xlabel("E2E Latency (ms)")
axes[0].grid(True, linestyle="--", alpha=0.5)

sns.boxplot(data=df, y='latency_ms', ax=axes[1], color='#2ca02c', width=0.3, showfliers=False)
axes[1].set_title("(b) Boxplot (Quartiles & Medians)")
axes[1].set_ylabel("E2E Latency (ms)")
axes[1].grid(True, axis='y', linestyle="--", alpha=0.5)

sns.violinplot(data=df, y='latency_ms', ax=axes[2], color='#2ca02c', inner="quartile")
axes[2].set_title("(c) Violin Plot (Density Distribution)")
axes[2].set_ylabel("E2E Latency (ms)")
axes[2].grid(True, axis='y', linestyle="--", alpha=0.5)

fig.suptitle("Standard Latency Metrics Overview (CALIBER Regtest)", y=1.05, fontsize=14)
fig.tight_layout()
os.makedirs(FIGURES_DIR, exist_ok=True)
fig.savefig(os.path.join(FIGURES_DIR, "plot_01_cdf_box_violin.png"), dpi=300, bbox_inches='tight')
