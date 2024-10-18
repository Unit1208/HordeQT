import os
import sys
from enum import StrEnum, auto
from pathlib import Path

from loguru import logger
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication

ANON_API_KEY = "0000000000"
BASE_URL = "https://aihorde.net/api/v2/"
LOGGER = logger


UPSCALE_MAP = {
    None: None,
    "None": None,
    "RealESRGAN 2x": "RealESRGAN_x2plus",
    "RealESRGAN 4x": "RealESRGAN_x4plus",
    "RealESRGAN 4x Anime": "RealESRGAN_x4plus_anime_6B",
    "NMKD Siax": "NMKD_Siax",
    "Anime 4x": "4x_AnimeSharp",
}


class Samplers(StrEnum):
    k_euler = auto()
    k_euler_a = auto()
    k_lms = auto()
    k_heun = auto()
    k_dpm_2 = auto()
    k_dpm_2_a = auto()
    k_dpm_adaptive = auto()
    k_dpm_fast = auto()
    k_dpmpp_2m = auto()
    k_dpmpp_2s_a = auto()
    k_dpmpp_sde = auto()
    DDIM = auto()
    lcm = auto()
    dpmsolver = auto()


APP = QApplication(sys.argv)
APP.setApplicationDisplayName("Horde QT")
APP.setApplicationName("hordeqt")
APP.setOrganizationName("Unit1208")

SAVED_DATA_DIR_PATH = Path(
    QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
)
SAVED_LOG_PATH = SAVED_DATA_DIR_PATH / "logs"
SAVED_IMAGE_DIR_PATH = SAVED_DATA_DIR_PATH / "images"
SAVED_DATA_PATH = SAVED_DATA_DIR_PATH / "saved_data.json"
CACHE_PATH = Path(
    QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
)
os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)
os.makedirs(SAVED_LOG_PATH, exist_ok=True)
os.makedirs(SAVED_IMAGE_DIR_PATH, exist_ok=True)
os.makedirs(CACHE_PATH, exist_ok=True)

_imported = False
if not _imported:
    LOGGER.remove(0)
    if os.environ.get("HORDEQT_DEBUG"):
        LOGGER.add(sys.stdout, backtrace=True, diagnose=True, level="TRACE")
    else:
        LOGGER.add(sys.stdout, level="WARNING")
    LOGGER.add(
        SAVED_LOG_PATH / "hordeqtlog_{time}.log",
        compression="tar.gz",
        rotation="100 MB",
        enqueue=True,
    )
    LOGGER.add(
        SAVED_LOG_PATH / "hordeqtlog_{time}.jsonl",
        serialize=True,
        rotation="100 MB",
        enqueue=True,
    )

    LOGGER.debug(f"Saved data path: {SAVED_DATA_PATH}")
    LOGGER.debug(f"Saved data dir: {SAVED_DATA_DIR_PATH}")
    LOGGER.debug(f"Saved images dir: {SAVED_IMAGE_DIR_PATH}")
    LOGGER.debug(f"Logs dir: {SAVED_LOG_PATH}")
    LOGGER.debug(f"Cache dir: {CACHE_PATH}")

    _imported = True
