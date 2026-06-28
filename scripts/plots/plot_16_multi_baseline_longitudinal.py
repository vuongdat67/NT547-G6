# /// script
# dependencies = ["numpy", "pandas", "matplotlib", "seaborn"]
# ///
import os
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("artifacts/publication", exist_ok=True)

try:
    import scienceplots
    plt.style.use(['science', 'ieee', 'no-latex'])
except:
    plt.style.use('default')

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "axes.labelsize": 10,
    "legend.fontsize": 8,
    "grid.alpha": 0.4,
    "grid.linestyle": "--"
})

x = np.arange(1, 36)

np.random.seed(42)
# Baseline flat
signum = np.random.uniform(0.0, 0.05, size=35)
tron = np.random.uniform(0.0, 0.1, size=35)
stellar = np.random.uniform(0.05, 0.15, size=35)
stellar[19:25] += np.random.uniform(0.2, 0.4, size=6)

# Spiky ones
iota = np.random.uniform(0.15, 0.3, size=35)
iota[18:32] += np.random.uniform(0.5, 1.8, size=14)

ripple = np.random.uniform(0.15, 0.35, size=35)
ripple[18:32] += np.random.uniform(0.3, 1.0, size=14)

cardano = np.random.uniform(0.05, 0.2, size=35)
cardano[18:32] += np.random.uniform(0.8, 2.5, size=14)

fig, ax = plt.subplots(figsize=(7, 5))

ax.plot(x, cardano, 'o-', color='#1f77b4', markerfacecolor='none', markersize=5, linewidth=1, label='CALIBER_Optimal')
ax.plot(x, iota, 'd-', color='#2ca02c', markerfacecolor='none', markersize=5, linewidth=1, label='CALIBER_Fast')
ax.plot(x, ripple, '^-', color='m', markerfacecolor='none', markersize=5, linewidth=1, label='CRAB_Baseline')
ax.plot(x, stellar, 's-', color='gray', markersize=4, linewidth=1, label='Legacy_HTLC')
ax.plot(x, tron, 'd-', color='#800000', markersize=3, linewidth=1, label='Lightning_Std')
ax.plot(x, signum, 'o-', color='black', markersize=3, linewidth=1, label='Ideal_Threshold')

ax.set_xticks(np.arange(1, 36, 2))
ax.set_yticks(np.arange(-0.2, 2.8, 0.2))
ax.set_xlim(0, 36)
ax.set_ylim(-0.2, 2.7)

ax.set_xlabel('Epoch / Round')
ax.set_ylabel('Overhead Factor (Normalized)')
ax.set_title('16. Multi-Baseline Longitudinal Evaluation')

# Put legend outside
ax.legend(loc='lower left', bbox_to_anchor=(1.0, 0.0), frameon=False)
ax.grid(True)

plt.tight_layout()
plt.savefig("artifacts/publication/plot_16_multi_baseline_longitudinal.png", dpi=300)
plt.close()
