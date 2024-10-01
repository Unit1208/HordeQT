import json
import os
import time
from typing import Optional, Tuple

import requests
from PySide6.QtCore import QObject, QThread, Signal

from hordeqt.other.consts import BASE_URL, LOGGER
from hordeqt.other.util import CACHE_PATH, get_headers


class LoadThread(QThread):
    progress = Signal(int)
    model_info = Signal(dict)
    user_info = Signal(requests.Response)
    horde_info = Signal(type(Tuple[requests.Response, requests.Response]))

    def __init__(self, api_key: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.api_key = api_key

    def reload_user_info(self, api_key: Optional[str] = None):
        if api_key is not None:
            self.api_key = api_key
        LOGGER.debug("loading user info")
        self.user_info.emit(
            requests.get(BASE_URL + "find_user", headers=get_headers(self.api_key))
        )
        LOGGER.debug("User info loaded")

    def reload_horde_info(self):
        LOGGER.debug("Loading horde info")

        self.horde_info.emit(
            (
                requests.get(
                    BASE_URL + "stats/img/totals",
                    headers=get_headers(self.api_key, False),
                ),
                requests.get(
                    BASE_URL + "status/performance",
                    headers=get_headers(self.api_key, False),
                ),
            )
        )
        LOGGER.debug("Horde info loaded")

    def run(self):
        t = [self.reload_user_info, self.reload_horde_info, self.load_model_cache]
        for n in range(len(t)):
            # I don't love this, but it's fine.
            t[n]()
            self.progress.emit((n + 1) * 100 / (len(t)))

    def load_model_cache(self):
        model_cache_path = CACHE_PATH / "model_ref.json"

        if (
            not model_cache_path.exists()
            or time.time() - model_cache_path.stat().st_mtime > 60 * 60
        ):
            LOGGER.debug(f"Refreshing model cache at {model_cache_path}")
            os.makedirs(model_cache_path.parent, exist_ok=True)
            r = requests.get(
                "https://raw.githubusercontent.com/Haidra-Org/AI-Horde-image-model-reference/flux/stable_diffusion.json"
            )
            j = r.json()
            with open(model_cache_path, "wt") as f:
                json.dump(j, f)
        else:
            LOGGER.debug(f"Model cache at {model_cache_path} is fresh, not reloading")

            with open(model_cache_path, "rt") as f:
                j = json.load(f)

        self.model_info.emit(j)
