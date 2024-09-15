import logging
from hordeqt.classes import LocalJob, apply_metadata_to_image
from hordeqt.util import SAVED_IMAGE_DIR_PATH

import requests
from PySide6.QtCore import QThread, Signal


import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Self
from hordeqt.consts import LOGGER


class DownloadThread(QThread):
    completed_downloads: List[LocalJob]
    queued_downloads: List[LocalJob]
    queued_deletes: List[LocalJob]
    completed = Signal(LocalJob)

    def __init__(
        self,
        queued_downloads=[],
        completed_downloads=[],
        queued_deletes=[],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.queued_downloads = queued_downloads
        self.completed_downloads = completed_downloads
        self.queued_deletes = queued_deletes
        self.running = True
        self.image_dir_path = SAVED_IMAGE_DIR_PATH

    def add_dl(self, local_job: LocalJob):
        self.queued_downloads.append(local_job)

    def run(self):
        while self.running:
            if len(self.queued_downloads) > 0:
                lj = self.queued_downloads.pop()
                LOGGER.info(f"Downloading {lj.id}")
                tf = tempfile.NamedTemporaryFile()
                tf.write(requests.get(lj.downloadURL).content)
                apply_metadata_to_image(Path(tf.name), lj)
                tf.close()
                LOGGER.debug(f"{lj.id} downloaded")
                self.completed.emit(lj)
                self.completed_downloads.append(lj)
            if len(self.queued_deletes) > 0:
                lj = self.queued_deletes.pop()
                LOGGER.info(f"Deleting {lj.id}")
                try:
                    self.completed_downloads.remove(lj)
                except ValueError as e:
                    LOGGER.warning(f"Failed to delete {lj.id}")
                if os.path.exists(lj.path):
                    if lj.path.is_file():
                        lj.path.unlink()
                    else:
                        LOGGER.warning(
                            f'Path referred to by {lj.id} ("{lj.path}") is a directory'
                        )
            time.sleep(0.1)

    def serialize(self):
        return {
            "completed_downloads": [x.serialize() for x in self.completed_downloads],
            "queued_downloads": [x.serialize() for x in self.queued_downloads],
            "queued_deletes": [x.serialize() for x in self.queued_deletes],
        }

    @classmethod
    def deserialize(
        cls: type[Self],
        value: Dict,
    ):
        if (cd := value.get("completed_downloads", None)) is None:
            ncd = []
        else:
            cd: List[dict] = cd
            ncd = [LocalJob.deserialize(x, SAVED_IMAGE_DIR_PATH) for x in cd]
        if (qdl := value.get("queued_downloads", None)) is None:
            nqdl = []
        else:
            qdl: List[dict] = qdl
            nqdl = [LocalJob.deserialize(x, SAVED_IMAGE_DIR_PATH) for x in qdl]
        if (qd := value.get("queued_deletes", None)) is None:
            nqd = []
        else:
            qd: List[dict] = qd
            nqd = [LocalJob.deserialize(x, SAVED_IMAGE_DIR_PATH) for x in qd]
        return cls(
            
            completed_downloads=ncd,
            queued_downloads=nqdl,
            queued_deletes=nqd,
        )

    def stop(self):
        self.running = False
        self.wait()

    def delete_image(self, image: LocalJob):
        self.queued_deletes.append(image)
