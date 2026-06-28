import os
import subprocess
import glob

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root_dir)
    os.makedirs("artifacts/publication", exist_ok=True)
    os.makedirs("artifacts/publication/plotly", exist_ok=True)
    
    plot_scripts = sorted(glob.glob("scripts/plots/plot_*.py"))
    
    for script in plot_scripts:
        print(f"Generating {script}...")
        try:
            subprocess.run(["uv", "run", script], check=True)
            print("  Done.")
        except subprocess.CalledProcessError as e:
            print(f"  Error running {script}: {e}")

if __name__ == "__main__":
    main()
