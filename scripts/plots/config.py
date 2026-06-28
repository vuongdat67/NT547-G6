"""Publication output directory configuration.

Override with environment variable PUBLICATION_SUBDIR (default: "regtest").
Example:
    PUBLICATION_SUBDIR=signet uv run scripts/plots/generate_all_plots.py
    PUBLICATION_SUBDIR=signet uv run scripts/plots/plot_00_evaluation_grid.py
"""
import os

OUTPUT_SUBDIR = os.environ.get("PUBLICATION_SUBDIR", "regtest")

# Base directories for figures and interactive plots
FIGURES_DIR = f"artifacts/publication/{OUTPUT_SUBDIR}"
PLOTLY_DIR = "artifacts/publication/plotly"
