# /// script
# dependencies = [
#   "numpy",
#   "pandas",
#   "plotly"
# ]
# ///
"""Interactive: CLBA Width vs Collateral sweep using Plotly."""

from config import FIGURES_DIR, PLOTLY_DIR

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

os.makedirs(PLOTLY_DIR, exist_ok=True)

df_sweep = pd.read_csv("artifacts/experiments/parameter_sweep.csv")
row = df_sweep.iloc[0]
v_sat = row['v_sat']
v_dep_sat = row['v_dep_sat']
v_col_sat = row['v_col_sat']

multipliers = np.array([1.0, 1.25, 1.5, 2.0])
naive_widths = np.array([
    row['width_crab_sat'], row['width_crab_p125_sat'],
    row['width_crab_p150_sat'], row['width_crab_p200_sat']
]) / 1e6

c_vals = multipliers * v_sat
caliber_widths = ((v_sat + v_dep_sat) - c_vals) / 1e6

fig = go.Figure()
fig.add_trace(go.Scatter(x=multipliers, y=naive_widths, mode='lines+markers',
                          name='Naive CRAB', line=dict(color='#2ca02c', width=3)))
fig.add_trace(go.Scatter(x=multipliers, y=caliber_widths, mode='lines+markers',
                          name='CALIBER', line=dict(color='#9467bd', width=3, dash='dash')))
fig.add_hline(y=0, line=dict(color='black', width=1))
fig.add_vline(x=(v_sat + v_dep_sat) / v_sat, line=dict(color='red', width=2, dash='dot'),
              annotation_text='c*', annotation_position='top left')

fig.update_layout(title='CLBA Width vs Collateral Sweep',
                  xaxis_title='Collateral Multiplier (c\'/v)',
                  yaxis_title='Attack Width (10⁶ sat)',
                  template='plotly_white', hovermode='x unified')

fig.write_html(os.path.join(PLOTLY_DIR, "interactive_caliber_width_vs_collateral.html"))
print("Saved interactive_caliber_width_vs_collateral.html")
