# /// script
# dependencies = ["numpy", "pandas", "matplotlib", "seaborn"]
# ///
from config import FIGURES_DIR, PLOTLY_DIR

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
})

labels = np.array(['Security', 'Latency', 'Tx Fee', 'Scalability', 'Privacy', 'Complexity'])
num_vars = len(labels)

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

caliber = [0.95, 0.85, 0.75, 0.8, 0.9, 0.7]
crab = [0.6, 0.9, 0.85, 0.7, 0.6, 0.9]
htlc = [0.5, 0.95, 0.95, 0.6, 0.5, 0.95]

caliber += caliber[:1]
crab += crab[:1]
htlc += htlc[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# Draw one axe per variable and add labels
plt.xticks(angles[:-1], labels, color='grey', size=10, fontweight='bold')

# Draw ylabels
ax.set_rlabel_position(30)
plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=7)
plt.ylim(0, 1.1)

# Plot CALIBER
ax.plot(angles, caliber, linewidth=2, linestyle='solid', label='CALIBER (Ours)', color='#2ca02c')
ax.fill(angles, caliber, '#2ca02c', alpha=0.15)

# Plot CRAB
ax.plot(angles, crab, linewidth=2, linestyle='dashed', label='Naive CRAB', color='#d62728')
ax.fill(angles, crab, '#d62728', alpha=0.1)

# Plot Legacy
ax.plot(angles, htlc, linewidth=2, linestyle='dotted', label='Legacy HTLC', color='black')

plt.title('18. Multi-Dimensional Protocol Capabilities', size=12, y=1.1)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "plot_18_radar_comparison.png"), dpi=300)
plt.close()
