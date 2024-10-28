# HordeQT

**A local frontend to the [AI Horde](https://aihorde.net).**

HordeQT is written in [Python](https://python.org), using the [PySide6](https://pypi.org/project/PySide6/) library for Qt bindings.

> [!WARNING]
> HordeQT is written to be cross-platform, and will work on Linux, Windows, and MacOS. However, due to code signing restrictions, **I can not provide a MacOS build**.

The only requirements to build are: python>=3.10, pip, and venv. `build.py` will install all other dependencies automatically if it can.

> [!IMPORTANT]
> When using the pre-built Windows versions, you may encounter a "unverified publisher" warning. This app is safe, I just don't want to go through the whole process of obtaining a code signing certificate.

## Developing HordeQT

TODO: better documentation

### Initializing environment

```sh
python -m venv venv
source venv/bin/activate # (or .\venv\Scripts\Activate.ps1)
pip install -U briefcase pip setuptools wheel pyside6
python scripts/convert_files.py
briefcase create linux flatpak # `windows app`, `macOS app` for these on other platforms.
briefcase update linux flatpak --no-input -r --update-resources
```

### Running

```sh
source env.sh
python src/hordeqt
```

or

```sh
briefcase dev
```
