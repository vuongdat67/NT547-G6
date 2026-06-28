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
val_dists = data['telemetry']['scriptValidationDistributions']

rows = []
for d in wit_dists:
    l = d['leaves']
    for v in d['timesMicros']:
        rows.append({"Leaves": f"{l} Leaves", "Time (µs)": v, "Process": "Witness Gen"})
for d in val_dists:
    l = d['leaves']
    for v in d['timesMicros']:
        rows.append({"Leaves": f"{l} Leaves", "Time (µs)": v, "Process": "Script Val"})

df = pd.DataFrame(rows)

fig, ax = plt.subplots(figsize=(8, 5))
sns.violinplot(data=df, x="Leaves", y="Time (µs)", hue="Process", split=True,
               inner="box", palette={"Witness Gen": "#d62728", "Script Val": "#2ca02c"}, ax=ax, linewidth=1.2)
ax.set_title("7. Split Violin Plot: Witness Gen vs Script Val")
ax.grid(True, axis="y")
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "plot_07_split_violin.png"), dpi=300)
