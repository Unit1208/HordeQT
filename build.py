import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List


def find_pyside_executable(ex_name: str) -> Path:
    # Determine the correct executable name based on the platform
    exec_name = (ex_name + ".exe") if sys.platform == "win32" else ex_name

    # Check common paths where pyside6-uic might be located
    possible_paths = [
        Path(sys.exec_prefix) / "bin" / exec_name,
        Path(sys.exec_prefix) / "Scripts" / exec_name,  # Common on Windows
        Path(sys.exec_prefix) / "lib" / ex_name / exec_name,  # Common on macOS
    ]

    for path in possible_paths:
        if path.is_file():
            return path

    # If not found, attempt to find in PATH environment variable
    uic_path = shutil.which(exec_name)
    if uic_path:
        return Path(uic_path)

    raise FileNotFoundError(f"{exec_name} not found. Ensure PySide6 is installed.")


def convert_uic_files():
    ui_fns = ["form.ui", "modelinfo.ui", "prompt_item.ui", "prompt_library.ui"]
    ui_files: List[Path] = [
        Path(__file__).parent / "src" / "hordeqt" / x for x in ui_fns
    ]
    uic = find_pyside_executable("pyside6-uic")
    for file in ui_files:
        new_py_fpath = (
            (Path(__file__).parent / "src" / "hordeqt" / "gen" / ("ui_"+file.stem+".py"))
            .resolve()
        )
        cmd = [str(uic.resolve()), str(file.resolve()), f"-o={str(new_py_fpath)}"]
        subprocess.run(cmd, check=True)
        print(f"Converted {str(file)} to {str(new_py_fpath)}")


def main():
    s = os.curdir
    convert_uic_files()
    os.chdir(s)


if __name__ == "__main__":
    main()
