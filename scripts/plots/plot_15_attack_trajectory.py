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
    "legend.fontsize": 9,
    "grid.alpha": 0.4,
    "grid.linestyle": "--"
})

rounds = np.arange(1, 101)

# Synthetic data mimicking an oscillating attack
honest_rep = 1 - 0.5 * np.exp(-rounds / 20.0)
attack_rep = np.zeros_like(rounds, dtype=float)
val = 0.5
for i, r in enumerate(rounds):
    if r < 40:
        if r % 5 == 0: val -= 0.15 # Slash
        else: val += 0.05          # Slow recovery
    else:
        val -= 0.02 # Permanent isolation
    val = max(0.01, min(1.0, val))
    attack_rep[i] = val

voting_power = np.copy(attack_rep) * 0.1
voting_power[voting_power < 0.02] = 0

accuracy = 1.0 - (voting_power * 1.5)
accuracy = np.clip(accuracy, 0.95, 1.0)
accuracy_naive = 1.0 - (voting_power * 2.5) - 0.02
accuracy_naive = np.clip(accuracy_naive, 0.9, 1.0)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

# Panel 1: Reputation
ax1.plot(rounds, honest_rep, '-', color='#2ca02c', linewidth=2, label='Honest Node')
ax1.plot(rounds, attack_rep, '--', color='#d62728', linewidth=2, label='Attacker (Oscillating)')
ax1.axhline(0.02, color='gray', linestyle='-.', label=r'$R_{min}$ Isolation')
ax1.set_ylabel('Reputation Score $R_t$')
ax1.set_title('(a) Reputation Trajectory under Oscillating Byzantine Attack')
ax1.legend(loc='lower right')
ax1.grid(True)

# Panel 2: Voting Power
ax2.plot(rounds, voting_power, '-', color='#800000', linewidth=2, label='Attacker Voting Weight')
ax2.fill_between(rounds, 0, voting_power, color='#800000', alpha=0.1)
ax2.axhline(0.01, color='purple', linestyle='--', alpha=0.5, label='Isolation Threshold')
ax2.set_ylabel('Voting Weight')
ax2.set_title('(b) Attacker Voting Power Influence')
ax2.legend(loc='upper right')
ax2.grid(True)

# Panel 3: System Accuracy
ax3.plot(rounds, accuracy, 'o-', color='#1f77b4', markersize=3, linewidth=1.5, label='CALIBER (With Penalty)')
ax3.plot(rounds, accuracy_naive, 'x-', color='#d62728', markersize=3, linewidth=1.5, label='Naive (No Penalty)')
ax3.axhline(1.0, color='#2ca02c', linestyle='--', alpha=0.6, label='Perfect Accuracy')
ax3.set_xlabel('Round $t$')
ax3.set_ylabel('System Accuracy')
ax3.set_title('(c) Accuracy Recovery Under Attack')
ax3.legend(loc='lower right')
ax3.grid(True)
ax3.set_ylim(0.9, 1.01)

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "plot_15_attack_trajectory.png"), dpi=300)
plt.close()
