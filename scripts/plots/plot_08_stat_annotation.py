# /// script
# dependencies = ["pandas", "matplotlib", "seaborn", "statannotations"]
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

# Try statannotations, fall back to manual annotation
try:
    from statannotations.Annotator import Annotator
    pairs = [
        (("1 Leaves", "Witness Gen"), ("1 Leaves", "Script Val")),
        (("8 Leaves", "Witness Gen"), ("8 Leaves", "Script Val"))
    ]
    annotator = Annotator(ax, pairs, data=df, x="Leaves", y="Time (µs)", hue="Process")
    annotator.configure(test="Mann-Whitney", text_format="star", loc="inside")
    annotator.apply_and_annotate()
except ImportError:
    # Manual Mann-Whitney annotation as fallback
    from scipy.stats import mannwhitneyu
    for leaves in ["1 Leaves", "8 Leaves"]:
        a = df[(df["Leaves"] == leaves) & (df["Process"] == "Witness Gen")]["Time (µs)"]
        b = df[(df["Leaves"] == leaves) & (df["Process"] == "Script Val")]["Time (µs)"]
        stat, p = mannwhitneyu(a, b, alternative='two-sided')
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
        # Place in top-right of the pair's region
        x_pos = list(range(len(df['Leaves'].unique())))[["1 Leaves", "8 Leaves"].index(leaves)]
        y_max = max(a.max(), b.max())
        ax.annotate(f'M-W {sig}\np={p:.2e}', xy=(x_pos, y_max * 1.05),
                    ha='center', fontsize=8, color='gray')

ax.set_title("Statistical Significance (Mann-Whitney U Test)")
ax.grid(True, axis="y")
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "plot_08_stat_annotation.png"), dpi=300)
