from pathlib import Path

from build import convert_qrc_resources, convert_uic_files

convert_uic_files(Path.cwd() / "venv")
convert_qrc_resources(Path.cwd() / "venv")
