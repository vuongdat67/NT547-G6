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

with open("artifacts/kappa_window_sim.json", "r") as f:
    kappa_data = json.load(f)['rows']

joy_data = []
for row in kappa_data:
    if row['rhoH'] == 0.4:
        samples = np.random.normal(loc=row['simulatedProbMean'], scale=row['simulatedProbStd'], size=1000)
        for s in samples:
            joy_data.append({"Kappa": f"k = {row['kappa']}", "Success Probability": s})

df_joy = pd.DataFrame(joy_data)

sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
g = sns.FacetGrid(df_joy, row="Kappa", hue="Kappa", aspect=5, height=1, palette="viridis")
g.map(sns.kdeplot, "Success Probability", clip_on=False, fill=True, alpha=0.8, linewidth=1.5)
g.map(sns.kdeplot, "Success Probability", clip_on=False, color="w", lw=2)
g.map(plt.axhline, y=0, lw=2, clip_on=False)

def label(x, color, label):
    ax = plt.gca()
    ax.text(0, .2, label, fontweight="bold", color=color, ha="left", va="center", transform=ax.transAxes)

g.map(label, "Success Probability")
g.fig.subplots_adjust(hspace=-0.5)
g.set_titles("")
g.set(yticks=[], ylabel="")
g.despine(bottom=True, left=True)
g.fig.suptitle("4. Ridgeline Plot: Success Probability by Kappa (ρ_H = 0.4)", y=1.05)
g.fig.savefig("artifacts/publication/plot_04_ridgeline.png", dpi=300, bbox_inches="tight")
