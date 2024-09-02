import subprocess
import sys
from pathlib import Path
from typing import List


def convert_uic_files(current_dir: Path | None = None):
    current_dir = current_dir or Path(__file__).parent
    ui_fns = ["form.ui", "modelinfo.ui", "prompt_item.ui", "prompt_library.ui"]
    ui_files: List[Path] = [current_dir / Path(x) for x in ui_fns]
    uic = Path(sys.exec_prefix) / "bin" / "pyside6-uic"
    for file in ui_files:
        new_py_fpath = file.with_name("ui_" + file.name).with_suffix(".py").resolve()
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
        f"--linux-icon={iconpath}",
        f"--output-dir={current_dir / 'dist'}",
        str(entry_script),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
