# /// script
# dependencies = ["matplotlib"]
# ///
import os
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey

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

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[], title="17. Protocol Fund Flow & Collateral Slash Mechanism")

sankey = Sankey(ax=ax, scale=0.01, offset=0.2, head_angle=150, format='%.0f', unit='%')

# Node 1: Initial Deposit
sankey.add(flows=[100, -70, -30],
           labels=['Alice Wallet', 'HTLC Value', 'Collateral'],
           orientations=[0, 0, 1],
           pathlengths=[0.25, 0.25, 0.25],
           facecolor='#1f77b4')

# Node 2: HTLC Resolution
sankey.add(flows=[70, 30, -50, -20, -30],
           labels=['', '', 'Bob Receives', 'Alice Refund', 'Burned Penalty'],
           orientations=[0, -1, 0, 1, -1],
           prior=0,
           connect=(1, 0),
           pathlengths=[0.25, 0.25, 0.25, 0.25, 0.25],
           facecolor='#2ca02c')

diagrams = sankey.finish()
for diagram in diagrams:
    for text in diagram.texts:
        text.set_fontsize(9)
        text.set_fontweight('bold')

plt.tight_layout()
plt.savefig("artifacts/publication/plot_17_sankey_fund_flow.png", dpi=300)
plt.close()
