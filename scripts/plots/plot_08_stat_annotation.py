# /// script
# dependencies = ["pandas", "matplotlib", "seaborn", "statannotations"]
# ///
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statannotations.Annotator import Annotator

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

rows = []
for d in data['telemetry']['witnessGenerationDistributions']:
    l = d['leaves']
    for v in d['timesMicros']:
        rows.append({"Leaves": f"{l} Leaves", "Time (µs)": v, "Process": "Witness Gen"})
for d in data['telemetry']['scriptValidationDistributions']:
    l = d['leaves']
    for v in d['timesMicros']:
        rows.append({"Leaves": f"{l} Leaves", "Time (µs)": v, "Process": "Script Val"})

df = pd.DataFrame(rows)

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x="Leaves", y="Time (µs)", hue="Process", palette={"Witness Gen": "#d62728", "Script Val": "#2ca02c"}, ax=ax, showfliers=False)

pairs = [
    (("1 Leaves", "Witness Gen"), ("1 Leaves", "Script Val")),
    (("8 Leaves", "Witness Gen"), ("8 Leaves", "Script Val"))
]
annotator = Annotator(ax, pairs, data=df, x="Leaves", y="Time (µs)", hue="Process")
annotator.configure(test="Mann-Whitney", text_format="star", loc="inside")
annotator.apply_and_annotate()

ax.set_title("8. Statistical Significance (Mann-Whitney U Test)")
ax.grid(True, axis="y")
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
fig.tight_layout()
fig.savefig("artifacts/publication/plot_08_stat_annotation.png", dpi=300)
