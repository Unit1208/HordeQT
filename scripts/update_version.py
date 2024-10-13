from pathlib import Path

import toml
import typer
from ruamel.yaml import YAML

app = typer.Typer()


def update_hordeqt_version(version: str):
    hordeqt_file = Path("src/hordeqt/__init__.py")
    lines = hordeqt_file.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("APPVERSION"):
            lines[i] = f'APPVERSION = "{version}"'
            break
    hordeqt_file.write_text("\n".join(lines) + "\n")


def update_pyproject_version(version: str):
    pyproject_file = Path("pyproject.toml")
    pyproject_data = toml.load(pyproject_file)
    pyproject_data["tool"]["briefcase"]["version"] = version
    with pyproject_file.open("w") as f:
        toml.dump(pyproject_data, f)


def update_appveyor_version(version: str):
    appveyor_file = Path("appveyor.yml")
    yaml = YAML()
    with appveyor_file.open("r") as f:
        data = yaml.load(f)
    data["version"] = version
    with appveyor_file.open("w") as f:
        yaml.dump(data, f)


@app.command()
def update_version(version: str):
    """Update the version in hordeqt, pyproject.toml, and appveyor.yml."""
    update_hordeqt_version(version)
    update_pyproject_version(version)
    update_appveyor_version(version)
    typer.echo(f"Version updated to {version} in all files.")


if __name__ == "__main__":
    app()
