import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

def find_uic_executable() -> Path:
    # Determine the correct executable name based on the platform
    exec_name = "pyside6-uic.exe" if sys.platform == "win32" else "pyside6-uic"
    
    # Check common paths where pyside6-uic might be located
    possible_paths = [
        Path(sys.exec_prefix) / "bin" / exec_name,
        Path(sys.exec_prefix) / "Scripts" / exec_name,  # Common on Windows
        Path(sys.exec_prefix) / "lib" / "pyside6-uic" / exec_name  # Common on macOS
    ]
    
    for path in possible_paths:
        if path.is_file():
            return path
    
    # If not found, attempt to find in PATH environment variable
    uic_path = shutil.which(exec_name)
    if uic_path:
        return Path(uic_path)
    
    raise FileNotFoundError(f"{exec_name} not found. Ensure PySide6 is installed.")

def convert_uic_files(current_dir: Path | None = None):
    current_dir = current_dir or Path(__file__).parent
    ui_fns = ["form.ui", "modelinfo.ui", "prompt_item.ui", "prompt_library.ui"]
    ui_files: List[Path] = [current_dir / Path(x) for x in ui_fns]
    uic = find_uic_executable()
    for file in ui_files:
        new_py_fpath = file.with_name("ui_" + file.stem).with_suffix(".py").resolve()
        cmd = [str(uic.resolve()), str(file.resolve()), f"-o={str(new_py_fpath)}"]
        subprocess.run(cmd, check=True)
        print(f"Converted {str(file)} to {str(new_py_fpath)}")

def main():
    current_dir = Path(__file__).parent
    convert_uic_files(current_dir)

    entry_script = current_dir / "mainwindow.py"
    iconpath = current_dir / "QTHordeAssets" / "IconSmall.png"
    command = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--onefile",
        "--noinclude-qt-translations",
        "--remove-output",
        "--enable-plugin=pyside6",
        "--include-qt-plugins=accessiblebridge,platforminputcontexts,platforms/darwin",
        f"--linux-icon={iconpath}",
        "--macos-create-app-bundle",
        f"--macos-app-icon={iconpath}",
        f"--windows-icon-from-ico={iconpath}",
        f"--output-dir={current_dir / 'dist'}",
        "--assume-yes-for-downloads",
        str(entry_script),
    ]
    subprocess.run(command, check=True)

if __name__ == "__main__":
    main()
