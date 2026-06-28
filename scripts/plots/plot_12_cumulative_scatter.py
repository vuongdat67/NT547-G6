# /// script
# dependencies = ["numpy", "pandas", "matplotlib", "seaborn"]
# ///
from config import FIGURES_DIR, PLOTLY_DIR

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
df_e2e['datetime'] = pd.to_datetime(df_e2e['timestamp'])
df_e2e = df_e2e.sort_values('datetime')
df_e2e['elapsed_sec'] = (df_e2e['datetime'] - df_e2e['datetime'].iloc[0]).dt.total_seconds()
df_e2e['cum_tx'] = np.arange(1, len(df_e2e) + 1)

fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')

# Panel A: Cumulative Throughput
ax1.plot(df_e2e['elapsed_sec'], df_e2e['cum_tx'], color="#2ca02c", linewidth=2, label="CALIBER (Sequential)")
ax1.set_title("(a) Cumulative Throughput Comparison")
ax1.set_xlabel("Elapsed Time (seconds)")
ax1.set_ylabel("Cumulative Transactions Processed")
ax1.grid(True)
ax1.legend(loc="lower right")

# Panel B: Scatter Plot (Anomaly/Variance Detection)
ax2.scatter(df_e2e['run_id'], df_e2e['latency_ms'], color="#1f77b4", s=15, alpha=0.7, label="Honest Deployments")
mean_lat = df_e2e['latency_ms'].mean()
threshold = mean_lat + 2 * df_e2e['latency_ms'].std()
ax2.axhline(threshold, color='red', linestyle='--', label=rf"Anomaly Threshold ($\mu+2\sigma$)")
ax2.set_title("(b) Scatter Plot with Decision Boundary")
ax2.set_xlabel("Experiment Iteration")
ax2.set_ylabel("Latency (ms)")
ax2.grid(True)
ax2.legend(loc="upper right")

fig1.suptitle("12. Cumulative Throughput & Scatter Analysis", fontsize=14, fontweight='bold')
os.makedirs(FIGURES_DIR, exist_ok=True)
out1 = os.path.join(FIGURES_DIR, "plot_12_cumulative_scatter.png")
fig1.savefig(out1, dpi=300, facecolor="white")
plt.close(fig1)
