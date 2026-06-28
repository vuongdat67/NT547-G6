# /// script
# dependencies = [
#   "numpy",
#   "pandas",
#   "plotly"
# ]
# ///
"""Interactive: Kappa Window Probability using Plotly."""

from config import FIGURES_DIR, PLOTLY_DIR

import os
import pandas as pd
import plotly.graph_objects as go

os.makedirs(PLOTLY_DIR, exist_ok=True)

df_kappa = pd.read_csv("artifacts/experiments/kappa_window_table.csv")

fig = go.Figure()

for rho, grp in df_kappa.groupby("rho_h"):
    color = {'0.3': '#2ca02c', '0.4': '#9467bd', '0.5': '#d62728'}.get(str(rho), '#7f7f7f')
    fig.add_trace(go.Scatter(
        x=grp['kappa'], y=grp['simulated_prob_mean'],
        error_y=dict(type='data', array=grp['simulated_prob_std'] * 2, visible=True),
        mode='lines+markers', name=f'ρ_H = {rho:.1f}',
        line=dict(color=color, width=2)
    ))
    fig.add_trace(go.Scatter(
        x=grp['kappa'], y=grp['analytical_prob'],
        mode='lines', line=dict(color=color, width=1, dash='dot'),
        showlegend=False, name=f'ρ_H = {rho:.1f} (analytical)'
    ))

fig.update_layout(title='Linked ACS Confirmation Probability (Mean ± 2σ)',
                  xaxis_title='Security Window κ (blocks)',
                  yaxis_title='Honest Confirmation Probability',
                  template='plotly_white', hovermode='x unified')

fig.write_html(os.path.join(PLOTLY_DIR, "interactive_kappa_window_probability.html"))
print("Saved interactive_kappa_window_probability.html")
