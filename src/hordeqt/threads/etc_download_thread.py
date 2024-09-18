import base64
from collections.abc import Callable
import io
import pickle
from typing import Dict, List, Optional, Self, Tuple

import requests
from PySide6.QtCore import QMutex, QThread, QWaitCondition, Signal

from hordeqt.classes.LocalJob import LocalJob
from hordeqt.other.consts import LOGGER
from hordeqt.other.util import SAVED_DATA_DIR_PATH, create_uuid

dl_callback = Callable[[requests.Response], None]
queued_dl = Tuple[str, requests.Request, Optional[dl_callback]]


class DownloadThread(QThread):
    completed_downloads: Dict[str, requests.Response]
    queued_downloads: List[queued_dl]
    completed = Signal(LocalJob)

    def __init__(
        self,
        queued_downloads=[],
        completed_downloads=[],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.queued_downloads = queued_downloads
        self.completed_downloads = completed_downloads
        self.running = True
        self.wait_condition = QWaitCondition()
        self.mutex = QMutex()
        self.save_dir_path = SAVED_DATA_DIR_PATH

    def add_dl(self, request: requests.Request, cb: Optional[dl_callback]) -> str:
        dl_id = create_uuid()
        self.queued_downloads.append((dl_id, request, cb))
        return dl_id

    def prepare_dl(self, url: str, method: str, data: dict, cb: Optional[dl_callback]) -> str:
        req = requests.Request(method, url, data=data)
        dl_id = create_uuid()

        self.queued_downloads.append((dl_id, req, cb))
        return dl_id

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
            self.completed_downloads[dl_id] = response

            LOGGER.info(f"Downloaded {req.url} ({dl_id})")
            if cb is not None:
                cb(response)

    def serialize(self):
        callback_list = {dl_id: cb for dl_id, _, cb in self.queued_downloads}
        pickled_cb_list = pickle.dumps(callback_list)
        cb_str = base64.b64encode(pickled_cb_list).decode("utf-8")
        new_queued_download_list = [(dl_id, req)
                                    for dl_id, req, _ in self.queued_downloads]
        return {
            "callbacks": cb_str,
            "queued_downloads": new_queued_download_list,
            "completed_downloads": self.completed_downloads}

    @classmethod
    def deserialize(cls, data: Dict[str, str | list[requests.Response]]):
        cb_str: str = data.get("callbacks", "")  # type: ignore
        queued_downloads: list[Tuple[str, requests.Request]] = data.get(
            "queued_downloads")  # type: ignore
        completed_downloads: Dict[str, requests.Response] = data.get(
            "completed_downloads")  # type: ignore

        pickled_cb_list = base64.b64decode(cb_str.encode("utf-8"))
        callback_list = pickle.loads(pickled_cb_list)
        s = cls()
        s.queued_downloads = [
            (dl_id, req, callback_list[dl_id])
            for dl_id, req in queued_downloads
        ]

        s.completed_downloads = completed_downloads

    def stop(self):
        self.mutex.lock()
        self.running = False
        self.wait_condition.wakeAll()  # Wake the thread immediately to exit
        self.mutex.unlock()
        self.wait()
