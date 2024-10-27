import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

HORDEQT_BASE = Path(__file__).parent.parent / "src" / "hordeqt"


def find_executable(exe_name: str, prefix: os.PathLike | str = sys.exec_prefix) -> Path:
    # Determine the correct executable name based on the platform
    exec_name = (exe_name + ".exe") if sys.platform == "win32" else exe_name

    # First, try to find in PATH environment variable
    uic_path = shutil.which(exec_name)
    if uic_path:
        return Path(uic_path)

    # Check common paths where scripts might be located, adjusting for platform
    possible_paths = [
        Path(prefix) / "bin" / exec_name,  # Common for Linux/macOS
        Path(prefix) / "Scripts" / exec_name,  # Common for Windows virtualenvs
        Path(prefix)
        / "Library"
        / "bin"
        / exec_name,  # Anaconda and some Windows setups
    ]

    # Look in additional directories like virtualenv and custom prefixes
    if "VIRTUAL_ENV" in os.environ:
        virtualenv_prefix = Path(os.environ["VIRTUAL_ENV"])
        possible_paths.append(virtualenv_prefix / "bin" / exec_name)
        possible_paths.append(virtualenv_prefix / "Scripts" / exec_name)

    # Search in the possible paths
    for path in possible_paths:
        try:
            if path.is_file():
                return path
        except FileNotFoundError:
            pass

    raise FileNotFoundError(
        f"{exec_name} not found. Ensure all dependencies are installed."
    )


def convert_uic_files(prefix: Path):
    ui_fns = ["form.ui", "modelinfo.ui"]
    ui_files: List[Path] = [HORDEQT_BASE / "ui" / x for x in ui_fns]
    uic = find_executable("pyside6-uic", prefix)

    for file in ui_files:
        new_py_fpath = (HORDEQT_BASE / "gen" / ("ui_" + file.stem + ".py")).resolve()
        os.makedirs(new_py_fpath.parent, exist_ok=True)
        cmd = [str(uic.resolve()), str(file.resolve()), f"-o={str(new_py_fpath)}"]
        subprocess.run(cmd, check=True)
        print(f"Converted {str(file)} to {str(new_py_fpath)}")


def convert_qrc_resources(prefix: Path):
    qrc_fns = ["resources.qrc"]
    qrc_files: List[Path] = [HORDEQT_BASE / "resources" / x for x in qrc_fns]
    rcc = find_executable("pyside6-rcc", prefix)

    for file in qrc_files:
        new_py_fpath = (HORDEQT_BASE / "gen" / ("res_" + file.stem + ".py")).resolve()
        os.makedirs(new_py_fpath.parent, exist_ok=True)
        cmd = [str(rcc.resolve()), str(file.resolve()), f"-o={str(new_py_fpath)}"]
        subprocess.run(cmd, check=True)
        print(f"Converted {str(file)} to {str(new_py_fpath)}")


if __name__ == "__main__":
    prefix = Path.cwd() / "venv" / "bin"
    convert_qrc_resources(prefix)
    convert_uic_files(prefix)
