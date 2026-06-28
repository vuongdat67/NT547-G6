# /// script
# dependencies = [
#   "numpy",
#   "pandas",
#   "plotly"
# ]
# ///
"""Interactive: Parallel Swaps Collateral Threshold using Plotly."""

from config import FIGURES_DIR, PLOTLY_DIR

import os
import pandas as pd
import plotly.graph_objects as go

os.makedirs(PLOTLY_DIR, exist_ok=True)

df_swaps = pd.read_csv("artifacts/experiments/parallel_swaps_table.csv")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_swaps['n'], y=df_swaps['c_n_star_sat'] / 1e6,
    mode='lines+markers+text',
    text=[f'{v/1e6:.1f}M' for v in df_swaps['c_n_star_sat']],
    textposition='top center',
    name='c_n*',
    line=dict(color='#9467bd', width=3),
    marker=dict(size=10, color='#9467bd', line=dict(color='black', width=1))
))

fig.update_layout(title='Collateral Threshold vs Parallel Swaps',
                  xaxis_title='Number of parallel swaps (n)',
                  yaxis_title='Collateral Threshold c_n* (10⁶ sat)',
                  template='plotly_white',
                  xaxis=dict(tickmode='array', tickvals=list(df_swaps['n'])))

fig.write_html(os.path.join(PLOTLY_DIR, "interactive_parallel_swaps_cnstar.html"))
print("Saved interactive_parallel_swaps_cnstar.html")
