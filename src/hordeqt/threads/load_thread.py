from hordeqt.consts import BASE_URL,LOGGER
from hordeqt.util import get_headers


import requests
from PySide6.QtCore import QObject, QStandardPaths, QThread, Signal


import json
import os
import time
from pathlib import Path


class LoadThread(QThread):
    progress = Signal(int)
    model_info = Signal(dict)
    user_info = Signal(requests.Response)

    def __init__(self, api_key: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.api_key = api_key

    def reload_user_info(self, api_key):
        self.api_key = api_key
        LOGGER.debug("Reloading user info")
        self.user_info.emit(
            requests.get(BASE_URL + "find_user", headers=get_headers(api_key))
        )
        LOGGER.debug("User info reloaded")

    def run(self):
        LOGGER.debug("Loading user info")
        self.user_info.emit(
            requests.get(BASE_URL + "find_user", headers=get_headers(self.api_key))
        )
        LOGGER.debug("User info loaded")
        self.progress.emit(50)
        p = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.CacheLocation
            )
        )
        model_cache_path = p / "model_ref.json"


        if (
            not model_cache_path.exists()
            or time.time() - model_cache_path.stat().st_mtime > 60 * 60 * 24
        ):
            LOGGER.debug(f"Refreshing model cache at {model_cache_path}")
            os.makedirs(p, exist_ok=True)
            r = requests.get(
                "https://raw.githubusercontent.com/Haidra-Org/AI-Horde-image-model-reference/main/stable_diffusion.json"
            )
            j = r.json()
            with open(model_cache_path, "wt") as f:
                json.dump(j, f)
        else:
            LOGGER.debug(f"Model cache at {model_cache_path} is fresh, not reloading")

            with open(model_cache_path, "rt") as f:
                j = json.load(f)

        self.model_info.emit(j)
        self.progress.emit(100)