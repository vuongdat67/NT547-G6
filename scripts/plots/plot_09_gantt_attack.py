# /// script
# dependencies = ["matplotlib", "scienceplots"]
# ///
from config import FIGURES_DIR, PLOTLY_DIR

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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

fig, ax = plt.subplots(figsize=(8, 4))
ax.broken_barh([(0, 1), (1.5, 0.5), (2, 2.5)], (15, 8), facecolors=('#1f77b4', '#ff7f0e', '#d62728'), alpha=0.8)
ax.broken_barh([(0, 1), (1.5, 0.5), (2, 0.5), (2.5, 0.5)], (5, 8), facecolors=('#1f77b4', '#ff7f0e', '#9467bd', '#2ca02c'), alpha=0.8)

ax.set_ylim(0, 30)
ax.set_xlim(-0.5, 5.5)
ax.set_xlabel("Time ($t$) in Block Epochs")
ax.set_yticks([9, 19])
ax.set_yticklabels(['CALIBER\n(Defeated)', 'Naive CRAB\n(Vulnerable)'])
ax.grid(True, axis='x')

p1 = mpatches.Patch(color='#1f77b4', label='HTLC Setup')
p2 = mpatches.Patch(color='#ff7f0e', label='Stale State Broadcast')
p3 = mpatches.Patch(color='#d62728', label='Miner Censorship / Bribe')
p4 = mpatches.Patch(color='#9467bd', label='Alice Reveals $pre_b$')
p5 = mpatches.Patch(color='#2ca02c', label='Linked Burn Executed')
ax.legend(handles=[p1, p2, p3, p4, p5], loc='upper right', ncol=2)

ax.set_title("Attack Timeline (Gantt/Broken Barh): CLBA Defeat")
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "plot_09_gantt_attack.png"), dpi=300)
