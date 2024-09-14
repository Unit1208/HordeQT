import os
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile
from typing import List,Optional
import platform


def find_executable(exe_name: str,prefix:os.PathLike|str=sys.exec_prefix) -> Path:
    # Determine the correct executable name based on the platform
    exec_name = (exe_name + ".exe") if sys.platform == "win32" else exe_name

    # Check common paths where scripts might be located
    possible_paths = [
        Path(prefix) / "bin" / exec_name,
        Path(prefix) / "Scripts" / exec_name,
        Path(prefix) / "lib" / exe_name / exec_name,  # Common on macOS
    ]
    
    for path in possible_paths:
        try:
            print(os.listdir(path.parent))
        except FileExistsError:
            pass
        
        if path.is_file():
            return path

    # If not found, attempt to find in PATH environment variable
    uic_path = shutil.which(exec_name)
    if uic_path:
        return Path(uic_path)

    raise FileNotFoundError(f"{exec_name} not found. Ensure all dependencies are installed.")


def convert_uic_files():
    ui_fns = ["form.ui", "modelinfo.ui", "prompt_item.ui", "prompt_library.ui"]
    ui_files: List[Path] = [
        Path(__file__).parent / "src" / "hordeqt" / x for x in ui_fns
    ]
    uic = find_executable("pyside6-uic")
    for file in ui_files:
        new_py_fpath = (
            Path(__file__).parent
            / "src"
            / "hordeqt"
            / "gen"
            / ("ui_" + file.stem + ".py")
        ).resolve()
        cmd = [str(uic.resolve()), str(file.resolve()), f"-o={str(new_py_fpath)}"]
        subprocess.run(cmd, check=True)
        print(f"Converted {str(file)} to {str(new_py_fpath)}")




def detect_platform():
    curr_platform = platform.system().lower()

    is_windows = curr_platform.startswith("windows")
    is_linux = curr_platform.startswith("linux")
    is_macos = curr_platform.startswith("darwin")
    return curr_platform, is_windows, is_linux, is_macos


def install_sys_reqs():
    curr_platform, is_windows, is_linux, is_macos = detect_platform()
    if is_linux:
        os_rel = platform.freedesktop_os_release()
        match os_rel.get("id"):
            case "debian":
                os.system(
                    "yes | sudo apt install git build-essential pkg-config python3-dev python3-venv libgirepository1.0-dev libcairo2-dev gir1.2-gtk-3.0 libcanberra-gtk3-module elfutils -y"
                )
                pass
            case "fedora":
                os.system(
                    "yes | sudo dnf install git gcc make pkg-config rpm-build python3-devel gobject-introspection-devel cairo-gobject-devel gtk3 libcanberra-gtk3"
                )
            case "arch":
                os.system(
                    "yes | sudo pacman -Syu git base-devel pkgconf python3 gobject-introspection cairo gtk3 libcanberra"
                )
            case "opensuse":
                os.system(
                    "yes | sudo zypper install git patterns-devel-base-devel_basis pkgconf-pkg-config python3-devel gobject-introspection-devel cairo-devel gtk3 'typelib(Gtk)=3.0' libcanberra-gtk3-module"
                )
    # TODO: else:

    pass


def main():
    curr_dir = Path.cwd()

    venv_path = (curr_dir / "venv").resolve()
    install_sys_reqs()
    subprocess.run(["python", "-m", "venv", str(venv_path)])
    print(venv_path)
    print(os.listdir(venv_path))
    curr_platform, is_windows, is_linux, is_macos = detect_platform()

    if is_linux or is_macos:

        new_python = venv_path / "bin" / "python"
    elif is_windows:
        new_python = venv_path / "Scripts" / "python.exe"
    else:
        print(f'Unsupported OS: "{curr_platform}"')
        exit(1)
    subprocess.run(
        [
            str(new_python),
            "-m",
            "pip",
            "install",
            "-U",
            "briefcase",
            "pip",
            "setuptools",
            "wheel",
        ]
    )
    formats = []
    briefcase_platform = ""
    if is_windows:
        briefcase_platform = "windows"
        formats.append("msi")
        formats.append("zip")
    elif is_linux:
        briefcase_platform = "linux"
        formats.append("flatpak")
    elif is_macos:
        briefcase_platform = "macOS"
        formats.append("dmg")
        formats.append("pkg")
    briefcase_exec = find_executable("briefcase",venv_path)
    print(briefcase_exec)
    print(os.listdir(briefcase_exec.parent))
    subprocess.run([briefcase_exec, "dev", "--no-run", "-r"])
    convert_uic_files()
    
    for f in formats:
        subprocess.run([briefcase_exec, "build", briefcase_platform, f, "--no-input"])
    for f in formats:
        subprocess.run([briefcase_exec, "package", briefcase_platform, f, "--no-input"])


if __name__ == "__main__":
    main()
