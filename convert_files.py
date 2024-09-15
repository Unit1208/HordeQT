from pathlib import Path
from build import convert_uic_files

convert_uic_files(Path.cwd() / "venv")
