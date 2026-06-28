# /// script
# dependencies = ["numpy", "pandas", "matplotlib", "seaborn", "ptitprince"]
# ///
from config import FIGURES_DIR, PLOTLY_DIR

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ptitprince as pt

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

df_e2e = pd.read_csv("artifacts/experiments/regtest_variance.csv")
df_e2e['System'] = "CALIBER (Regtest)"

fig, ax = plt.subplots(figsize=(8, 5))
pt.RainCloud(x="System", y="latency_ms", data=df_e2e, palette=["#2ca02c"],
             bw=.2, width_viol=.6, ax=ax, orient="h", alpha=.65, dodge=True)
ax.set_title("2. Raincloud Plot: E2E Latency Distribution (Half-Violin + Jitter + Box)")
ax.set_xlabel("Latency (ms)")
ax.set_ylabel("")
fig.tight_layout()
os.makedirs(FIGURES_DIR, exist_ok=True)
fig.savefig(os.path.join(FIGURES_DIR, "plot_02_raincloud.png"), dpi=300)
