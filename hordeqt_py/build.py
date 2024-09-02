import subprocess
import sys
from pathlib import Path

def main():
    current_dir = Path(__file__).parent
    
    entry_script = current_dir / "mainwindow.py"
    
    command = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--remove-output",
        f"--output-dir={current_dir / 'dist'}",
        str(entry_script)
    ]
    
    subprocess.run(command, check=True)
    
if __name__ == "__main__":
    main()
