# /// script
# dependencies = ["pandas", "matplotlib", "seaborn"]
# ///
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

df_sweep = pd.read_csv("artifacts/experiments/parameter_sweep.csv")
df_sweep['kappa'] = pd.to_numeric(df_sweep['kappa'], errors='coerce')
df_sweep['v_dep_sat'] = pd.to_numeric(df_sweep['v_dep_sat'], errors='coerce')
df_sweep['v_col_sat'] = pd.to_numeric(df_sweep['v_col_sat'], errors='coerce')
df_sweep['width_caliber_cstar'] = pd.to_numeric(df_sweep['width_caliber_cstar'], errors='coerce')

df_slice = df_sweep[df_sweep['kappa'] == 7].copy()
df_slice = df_slice.groupby(['v_dep_sat', 'v_col_sat'])['width_caliber_cstar'].mean().reset_index()

pivot = df_slice.pivot(index='v_dep_sat', columns='v_col_sat', values='width_caliber_cstar')

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='RdYlGn_r', center=0, linewidths=0.5, ax=ax)
ax.set_title("5. Heatmap: Attack Width ($w_c$) given $v_{dep}$ and $v_{col}$ (satoshis)")
ax.set_ylabel("Deposit Value ($v_{dep}$)")
ax.set_xlabel("Collateral Value ($v_{col}$)")
ax.invert_yaxis()
fig.tight_layout()
fig.savefig("artifacts/publication/plot_05_heatmap.png", dpi=300)
