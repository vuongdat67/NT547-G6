"""Batch-update all plot scripts to use config.py-driven output paths.

    Adds  "from config import FIGURES_DIR, PLOTLY_DIR"
    Replaces hardcoded FIGURES_DIR → FIGURES_DIR
    Replaces hardcoded PLOTLY_DIR   → PLOTLY_DIR
    Replaces os.makedirs(...) calls with os.makedirs(FIGURES_DIR/PLOTLY_DIR, exist_ok=True)
"""
import os, re, glob, textwrap

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def sort_key(fname):
    """Extract numeric part for ordering: plot_01_... → 1, plot_14a → 14, plot_xx → 99"""
    base = os.path.basename(fname)
    m = re.search(r'plot_(\d+)([a-z]?)_', base)
    if m:
        num = int(m.group(1))
        return (num, m.group(2))
    # generate_all_plots, config
    return (999, base)

scripts = sorted(
    [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".py") and f not in ("config.py",)],
    key=sort_key
)

IMPORT_LINE = "from config import FIGURES_DIR, PLOTLY_DIR\n"

REPLACEMENTS = [
    # Use raw f-string pattern
    ('FIGURES_DIR', 'FIGURES_DIR'),
    ("FIGURES_DIR", 'FIGURES_DIR'),
    ('PLOTLY_DIR', 'PLOTLY_DIR'),
    ("PLOTLY_DIR", 'PLOTLY_DIR'),
]

for fname in scripts:
    fpath = os.path.join(SCRIPTS_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    old_content = content

    ##############################################
    # (A) Replace os.makedirs calls and output paths
    ##############################################
    for old_pat, new_var in REPLACEMENTS:
        # Replace within f-strings and plain strings
        content = content.replace(old_pat, f"{{{new_var}}}")
        # Also replace outside f-strings (plain concatenation / os.path.join)
        content = content.replace(f'" + {new_var}', f"{{{new_var}}}")

    ##############################################
    # (B) Merge consecutive os.makedirs calls into one
    ##############################################
    # Pattern: FIGURES_DIR followed by PLOTLY_DIR (or vice versa) makedirs
    content = re.sub(
        r'os\.makedirs\(FIGURES_DIR, exist_ok=True\)\s*\n\s*os\.makedirs\(PLOTLY_DIR, exist_ok=True\)',
        'os.makedirs(FIGURES_DIR, exist_ok=True)\nos.makedirs(PLOTLY_DIR, exist_ok=True)',
        content
    )

    ##############################################
    # (C) Add import
    ##############################################
    # Add after the docstring or after the shebang/deps block
    if "from config import" not in content:
        # Try inserting after the PEP 723 block (before imports)
        lines = content.split("\n")
        insert_at = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip PEP 723 dependency block, docstrings, blank lines
            if stripped.startswith("# ///") or stripped.startswith("# //"):
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if stripped == "":
                continue
            if stripped.startswith("import ") or stripped.startswith("from "):
                insert_at = i
                break
            # First line that's not import/docstring/comment/blank
            if stripped.startswith("#") and not stripped.startswith("# ///"):
                continue
            if not stripped.startswith("#"):
                insert_at = i
                break

        if insert_at is not None:
            lines.insert(insert_at, IMPORT_LINE)
            content = "\n".join(lines)
        else:
            # Fallback: append at top after docstring
            content = IMPORT_LINE + content

    ##############################################
    # (D) Special case for generate_all_plots.py
    ##############################################
    if fname == "generate_all_plots.py":
        # It already imports from config for subprocess
        pass

    ##############################################
    # Write if changed
    ##############################################
    if content != old_content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ {fname} — updated")
    else:
        print(f"⏭️  {fname} — no changes")

print("\nDone. All plot scripts updated.")
