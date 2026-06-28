# /// script
# dependencies = ["numpy", "pandas", "matplotlib", "seaborn"]
# ///
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("artifacts/publication", exist_ok=True)

try:
    import scienceplots
    plt.style.use(['science', 'ieee', 'no-latex'])
except ImportError:
    plt.style.use('default')

with open("artifacts/experiments/experiment_summary.json", "r") as f:
    dists = json.load(f)['telemetry']['witnessGenerationDistributions']
overhead = next(d['timesMicros'] for d in dists if d['leaves'] == 1)
latency = pd.read_csv("artifacts/experiments/regtest_variance.csv")['latency_ms'].values

min_len = min(len(overhead), len(latency))
overhead = overhead[:min_len]
latency = latency[:min_len]

df = pd.DataFrame({'Witness Gen Overhead (µs)': overhead, 'E2E Latency (ms)': latency})

# sns.jointplot clears figure, so we set theme before
sns.set_theme(style="white", rc={
    "axes.facecolor": (0, 0, 0, 0),
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

g = sns.jointplot(data=df, x='Witness Gen Overhead (µs)', y='E2E Latency (ms)', kind="hex", color="#2ca02c", height=6)
g.plot_marginals(sns.histplot, kde=True, color="#2ca02c")
g.fig.suptitle("11. Joint Marginal Plot: Latency vs. Overhead", y=1.02, fontsize=14, fontweight='bold')
g.fig.savefig("artifacts/publication/plot_11_joint_marginal.png", dpi=300, bbox_inches='tight')

# Reset to scienceplots just in case for other scripts if run sequentially
try:
    plt.style.use(['science', 'ieee', 'no-latex'])
except:
    pass
