from collections.abc import Callable
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from PySide6.QtCore import QMutex, QThread, QWaitCondition

from hordeqt.other.consts import LOGGER, SAVED_DATA_DIR_PATH
from hordeqt.other.util import get_bucketized_cache_path, get_hash

dl_callback = Callable[[requests.Response], None]
queued_dl = Tuple[str, requests.Request, Optional[dl_callback]]


class DownloadThread(QThread):
    queued_downloads: List[queued_dl]

    def __init__(
        self,
        queued_downloads=[],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.queued_downloads = queued_downloads
        self.running = True
        self.wait_condition = QWaitCondition()
        self.mutex = QMutex()
        self.save_dir_path = SAVED_DATA_DIR_PATH

    def add_dl(self, request: requests.Request, cb: Optional[dl_callback]) -> str:
        dl_id = get_hash(request.url)
        self.queued_downloads.append((dl_id, request, cb))
        return dl_id

    def prepare_dl(
        self,
        url: str,
        method: str = "GET",
        data: dict = {},
        cb: Optional[dl_callback] = None,
    ) -> str:
        req = requests.Request(method, url, data=data)
        dl_id = get_hash(url)

        self.queued_downloads.append((dl_id, req, cb))
        return dl_id

    def download_to_cache(self, url: str, cb: Optional[Callable[[Path], Any]]):
        p = get_bucketized_cache_path(url)

        def _callback(req: requests.Response):
            with open(p, "wb") as f:
                f.write(req.content)
            if cb is not None:
                cb(p)

        if p.exists():
            if cb is not None:
                cb(p)
        else:
            return (self.prepare_dl(url, "GET", cb=_callback), p)

    def run(self):
        while self.running:
            self.mutex.lock()
            if not self.running:
                self.mutex.unlock()
                break
            self.pop_downloads()
            self.wait_condition.wait(self.mutex, 100)
            self.mutex.unlock()

    def pop_downloads(self):
        if len(self.queued_downloads) > 0:
            dl_id, req, cb = self.queued_downloads.pop()
            LOGGER.info(f"Downloading {req.url} ({dl_id})")
            prep_req = req.prepare()
            s = requests.session()
            response = s.send(prep_req)

            LOGGER.info(f"Downloaded {req.url} ({dl_id})")
            if cb is not None:
                cb(response)

    def serialize(self):
        new_queued_download_list = [
            (dl_id, req) for dl_id, req, _ in self.queued_downloads
        ]
        return {
            "queued_downloads": new_queued_download_list,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, dict | list[requests.Response]]):

        queued_downloads: list[Tuple[str, requests.Request]] = data.get(
            "queued_downloads", []
        )  # type: ignore

        s = cls()

        s.queued_downloads = [(dl_id, req, None) for dl_id, req in queued_downloads]

        return s

    def stop(self):
        self.mutex.lock()
        self.running = False
        self.wait_condition.wakeAll()  # Wake the thread immediately to exit
        self.mutex.unlock()
        self.wait()
