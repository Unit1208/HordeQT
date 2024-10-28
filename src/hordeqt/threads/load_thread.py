import json
import os
import time
from typing import List, Optional, Tuple

import requests
from PySide6.QtCore import QObject, QThread, Signal

from hordeqt.classes.Style import Style
from hordeqt.other.consts import BASE_URL, LOGGER
from hordeqt.other.util import CACHE_PATH, get_headers


class LoadThread(QThread):
    progress = Signal(int)
    model_info = Signal(dict)
    style_info = Signal(list)
    style_preview = Signal()
    user_info = Signal(requests.Response)
    horde_info = Signal(type(Tuple[requests.Response, requests.Response]))

    def __init__(self, api_key: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.api_key = api_key

    def run(self):
        t = [
            self.reload_user_info,
            self.reload_horde_info,
            self.load_model_file,
            self.load_style_file,
            self.load_style_preview,
        ]
        for n in range(len(t)):
            # I don't love this, but it's fine.
            t[n]()
            self.progress.emit((n + 1) * 100 / (len(t)))

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

    # FIXME: The following should absolutely be refactored.
    def load_style_file(self):
        style_cache_path = CACHE_PATH / "style_ref.json"
        if (
            not style_cache_path.exists()
        ) or time.time() - style_cache_path.stat().st_mtime > 60 * 60:
            LOGGER.debug(f"Refreshing style cache at {style_cache_path}")
            os.makedirs(style_cache_path.parent, exist_ok=True)
            r = requests.get(
                "https://raw.githubusercontent.com/Haidra-Org/AI-Horde-Styles/refs/heads/main/styles.json"
            )
            j: dict[str, dict] = r.json()
            with open(style_cache_path, "wt") as f:
                json.dump(j, f)
        else:
            LOGGER.debug(f"Style cache at {style_cache_path} is fresh, not reloading")

            with open(style_cache_path, "rt") as f:
                j: dict[str, dict] = json.load(f)
        styles: List[Style] = []
        for k, v in j.items():
            styles.append(Style.parse_from_json(k, v, True))

        self.style_info.emit(styles)

    def load_style_preview(self):

        self.style_preview_cache_path = CACHE_PATH / "style_preview.json"
        if (
            not self.style_preview_cache_path.exists()
        ) or time.time() - self.style_preview_cache_path.stat().st_mtime > 60 * 60:
            LOGGER.debug(
                f"Refreshing style preview cache at {self.style_preview_cache_path}"
            )
            os.makedirs(self.style_preview_cache_path.parent, exist_ok=True)
            r = requests.get(
                "https://raw.githubusercontent.com/amiantos/AI-Horde-Styles-Previews/refs/heads/main/previews.json"
            )
            j: dict[str, str] = r.json()
            with open(self.style_preview_cache_path, "wt") as f:
                json.dump(j, f)
        else:
            LOGGER.debug(
                f"Style preview cache at {self.style_preview_cache_path} is fresh, not reloading"
            )

            with open(self.style_preview_cache_path, "rt") as f:
                j: dict[str, str] = json.load(f)
        self.style_preview.emit()

    def load_model_file(self):
        model_cache_path = CACHE_PATH / "model_ref.json"

        if (
            not model_cache_path.exists()
        ) or time.time() - model_cache_path.stat().st_mtime > 60 * 60:
            LOGGER.debug(f"Refreshing model cache at {model_cache_path}")
            os.makedirs(model_cache_path.parent, exist_ok=True)
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
