import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Self

import requests
from PIL import Image
from PySide6.QtCore import QMutex, QThread, QWaitCondition, Signal

from hordeqt.classes.LocalJob import LocalJob, apply_metadata_to_image
from hordeqt.other.consts import LOGGER
from hordeqt.other.util import SAVED_IMAGE_DIR_PATH


class JobDownloadThread(QThread):
    completed_downloads: List[LocalJob]
    queued_downloads: List[LocalJob]
    queued_deletes: List[LocalJob]
    completed = Signal(LocalJob)
    use_metadata: bool

    def __init__(
        self,
        queued_downloads=[],
        completed_downloads=[],
        queued_deletes=[],
        parent=None,
        use_metadata=True,
    ) -> None:
        super().__init__(parent)
        self.queued_downloads = queued_downloads
        self.completed_downloads = completed_downloads
        self.queued_deletes = queued_deletes
        self.running = True
        self.wait_condition = QWaitCondition()
        self.mutex = QMutex()
        self.image_dir_path = SAVED_IMAGE_DIR_PATH
        self.use_metadata = use_metadata

    def add_dl(self, local_job: LocalJob):
        self.queued_downloads.append(local_job)

    def run(self):
        while self.running:
            self.mutex.lock()
            if not self.running:
                self.mutex.unlock()
                break
            self.pop_downloads()
            self.pop_deletes()
            self.wait_condition.wait(self.mutex, 100)
            self.mutex.unlock()

    def pop_downloads(self):
        if len(self.queued_downloads) > 0:
            lj = self.queued_downloads.pop()
            LOGGER.info(f"Downloading {lj.id}")
            tf = tempfile.NamedTemporaryFile()
            tf.write(requests.get(lj.downloadURL).content)
            if self.use_metadata:
                apply_metadata_to_image(Path(tf.name), lj)
            else:
                im = Image.open(Path(tf.name))
                im.save(lj.path)
            tf.close()
            LOGGER.debug(f"{lj.id} downloaded")
            self.completed.emit(lj)
            self.completed_downloads.append(lj)

    def pop_deletes(self):
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
            ncd = [LocalJob.deserialize(x) for x in cd]
        if (qdl := value.get("queued_downloads", None)) is None:
            nqdl = []
        else:
            nqdl = [LocalJob.deserialize(x) for x in qdl]
        if (qd := value.get("queued_deletes", None)) is None:
            nqd = []
        else:
            nqd = [LocalJob.deserialize(x) for x in qd]
        return cls(
            completed_downloads=ncd,
            queued_downloads=nqdl,
            queued_deletes=nqd,
        )

    def stop(self):
        self.mutex.lock()
        self.running = False
        self.wait_condition.wakeAll()  # Wake the thread immediately to exit
        self.mutex.unlock()
        self.wait()

    def delete_image(self, image: LocalJob):
        self.queued_deletes.append(image)
