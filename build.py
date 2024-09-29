import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List


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
    ui_fns = ["form.ui", "modelinfo.ui", "prompt_item.ui", "prompt_library.ui"]
    ui_files: List[Path] = [
        Path(__file__).parent / "src" / "hordeqt" / "ui" / x for x in ui_fns
    ]
    uic = find_executable("pyside6-uic", prefix)

    for file in ui_files:
        new_py_fpath = (
            Path(__file__).parent
            / "src"
            / "hordeqt"
            / "gen"
            / ("ui_" + file.stem + ".py")
        ).resolve()
        os.makedirs(new_py_fpath.parent, exist_ok=True)
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
        # one will probably work, I guess.
        os.system(
            "sudo apt install git build-essential pkg-config python3-dev python3-venv libgirepository1.0-dev libcairo2-dev gir1.2-gtk-3.0 libcanberra-gtk3-module elfutils flatpak flatpak-builder -y"
        )
        os.system(
            "sudo dnf install git gcc make pkg-config rpm-build python3-devel gobject-introspection-devel cairo-gobject-devel gtk3 libcanberra-gtk3 flatpak flatpak-builder -y"
        )
        os.system(
            "sudo pacman -Syu git base-devel pkgconf python3 gobject-introspection cairo gtk3 libcanberra flatpak flatpak-builder "
        )
        os.system(
            "sudo zypper install git patterns-devel-base-devel_basis pkgconf-pkg-config python3-devel gobject-introspection-devel cairo-devel gtk3 'typelib(Gtk)=3.0' libcanberra-gtk3-module flatpak flatpak-builder "
        )


def main():
    ISDEBUG = False
    curr_dir = Path.cwd()
    curr_platform, is_windows, is_linux, is_macos = detect_platform()

    venv_path = (curr_dir / "venv").resolve()
    gitignore_path = (curr_dir / "src" / "hordeqt" / ".gitignore").resolve()
    gitignore_tmp_path = curr_dir / "src" / "hordeqt" / ".wasgitignore"
    install_sys_reqs()
    if is_windows:
        paths = [
            "C:\\Python312-x64\\python.exe",
            "$env:LOCALAPPDATA\\Local\\Programs\\Python312\\python.exe",
        ]
        py_path = ""
        for p in paths:
            try:
                if os.system(p + " -V") == 0:
                    py_path = p
                    break
            except:
                pass
        if py_path == "":
            print(f"Couldn't find python")
            exit(1)
        subprocess.run([py_path, "-m", "venv", str(venv_path)])
    else:
        subprocess.run(["python", "-m", "venv", str(venv_path)])

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
            "pyside6",
        ]
    )
    print("PRE UIC CONVERSION")

    convert_uic_files(venv_path)
    print("POST UIC CONVERSION")
    formats = ["app"]
    additional_args = []
    briefcase_platform = ""
    if is_linux:
        briefcase_platform = "linux"
        formats = ["flatpak"]
    if is_windows:
        briefcase_platform = "windows"
        additional_args.append("--adhoc-sign")
    if is_macos:
        briefcase_platform = "macOS"
        additional_args.append("--adhoc-sign")

    # This is *really*, *really* dumb, but I don't know how else to fix the issue with briefcase.
    # In short, Briefcase *silently* doesn't copy files that are .gitignore'd, but only on windows.
    # So, the best "fix", apart from just removing gen from the .gitignore, which would just add more data that doesn't need to be included,
    # Is to move .gitignore back and forth. It's not the most elegant, but it technically works.
    if ISDEBUG or is_windows:
        shutil.move(gitignore_path, gitignore_tmp_path)
    briefcase_exec = find_executable("briefcase", venv_path)
    for f in formats:
        subprocess.run(
            [str(new_python), briefcase_exec, "create", briefcase_platform, f]
        )
        convert_uic_files(venv_path)
        subprocess.run(
            [
                str(new_python),
                briefcase_exec,
                "update",
                briefcase_platform,
                f,
                "--no-input",
                "-r",
                "--update-resources",
            ]
        )

    for f in formats:
        subprocess.run(
            [
                str(new_python),
                briefcase_exec,
                "build",
                briefcase_platform,
                f,
                "--no-input",
            ]
        )
        subprocess.run(
            [
                str(new_python),
                briefcase_exec,
                "package",
                briefcase_platform,
                f,
                "--no-input",
                *additional_args,
            ]
        )
    if ISDEBUG or is_windows:
        shutil.move(gitignore_tmp_path, gitignore_path)


if __name__ == "__main__":
    main()
