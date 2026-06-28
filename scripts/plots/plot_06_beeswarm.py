# /// script
# dependencies = ["pandas", "matplotlib", "seaborn"]
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

wit_dists = data['telemetry']['witnessGenerationDistributions']

rows = []
for d in wit_dists:
    l = d['leaves']
    for v in d['timesMicros']:
        rows.append({"Leaves": f"{l} Leaves", "Time (µs)": v, "Process": "Witness Gen"})

df_wit = pd.DataFrame(rows)
df_wit_sample = df_wit.groupby("Leaves").sample(n=100, random_state=42)

fig, ax = plt.subplots(figsize=(7, 5))
sns.violinplot(data=df_wit, x="Leaves", y="Time (µs)", inner=None, color="#2ca02c", alpha=0.3, ax=ax)
sns.swarmplot(data=df_wit_sample, x="Leaves", y="Time (µs)", color="white", edgecolor="#2ca02c", size=4, linewidth=1, ax=ax)
ax.set_title("6. Beeswarm Plot (Violin Overlay): Witness Generation Time")
ax.grid(True, axis="y")
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "plot_06_beeswarm.png"), dpi=300)
