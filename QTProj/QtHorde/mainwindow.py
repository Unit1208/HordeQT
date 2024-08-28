# This Python file uses the following encoding: utf-8
import datetime as dt
import uuid
import human_readable as hr
from pathlib import Path
import json
import os
import random
import sys
import time
from typing import List, Dict, Optional, Self
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog,
    QLineEdit,
    QWidget,
    QLayout,
    QSizePolicy,
    QLabel,
    QVBoxLayout,
    QScrollArea,
    QTableWidgetItem,
)
from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    QTimer,
    QStandardPaths,
    QRect,
    Qt,
    QUrl,
    QByteArray,
)
from PySide6.QtGui import QPixmap, QDesktopServices

from queue import Queue


# import cbor2


from ui_form import Ui_MainWindow
from ui_modelinfo import Ui_Dialog

import keyring
import requests

ANON_API_KEY = "0000000000"
BASE_URL = "https://aihorde.net/api/v2/"


def create_uuid():
    return str(uuid.uuid4())


def get_headers(api_key: str):
    return {
        "apikey": api_key,
        "Client-Agent": "HordeQt:0.0.1:Unit1208",
        "accept": "application/json",
        "Content-Type": "application/json",
    }


class ImageWidget(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.original_pixmap = QPixmap(image_path)
        self.setPixmap(self.original_pixmap)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)


class MasonryLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=10):
        super(MasonryLayout, self).__init__(parent)
        self.margin = margin
        self.spacing = spacing
        self.items = []

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def sizeHint(self):
        return self.minimumSize()

    def itemAt(self, index):
        return self.items[index] if 0 <= index < len(self.items) else None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def setGeometry(self, rect):
        super(MasonryLayout, self).setGeometry(rect)
        self.updateGeometry()

    def updateGeometry(self):
        if not self.items:
            return
        width = self.geometry().width()
        self.calculateColumnLayout(width)
        self.arrangeItems()

    def calculateColumnLayout(self, width):
        self.num_columns = max(1, width // (200 + self.spacing))
        self.column_width = (
            width - (self.num_columns - 1) * self.spacing
        ) // self.num_columns
        self.column_heights = [0] * self.num_columns

    def arrangeItems(self):
        x_offsets = [
            i * (self.column_width + self.spacing) for i in range(self.num_columns)
        ]
        for item in self.items:
            widget = item.widget()
            pixmap = widget.pixmap()
            aspect_ratio = (
                pixmap.width() / pixmap.height()
                if pixmap
                else widget.sizeHint().width() / widget.sizeHint().height()
            )
            height = self.column_width / aspect_ratio
            min_col = self.column_heights.index(min(self.column_heights))
            x = x_offsets[min_col]
            y = self.column_heights[min_col]
            widget.setGeometry(QRect(x, y, self.column_width, height))
            self.column_heights[min_col] += height + self.spacing

    def addImage(self, path: os.PathLike):
        image_widget = ImageWidget(path)
        self.addWidget(image_widget)


class Model:
    performance: float
    queued: int
    jobs: int
    eta: float
    type: str
    name: str
    count: int
    details: dict

    def get(self, name, default=None):
        if hasattr(self, name):
            return self["name"]
        elif default != None:
            return default
        raise KeyError(self, name)


class Job:
    def __init__(
        self,
        prompt: str,
        sampler_name: str,
        cfg_scale: float,
        seed: str,
        width: int,
        height: int,
        clip_skip: int,
        steps: int,
        model: str,
        karras: bool = True,
        hires_fix: bool = True,
        allow_nsfw: bool = False,
        horde_job_id: Optional[str] = None,
        wait_time: float = 0,
        queue_position: float = 0,
        done: bool = False,
        faulted: bool = False,
        kudos: float = 0,
    ):
        self.prompt = prompt
        self.sampler_name = sampler_name
        self.cfg_scale = cfg_scale
        self.seed = seed
        self.width = width
        self.height = height
        self.karras = karras
        self.hires_fix = hires_fix
        self.clip_skip = clip_skip
        self.steps = steps
        self.model = model
        self.allow_nsfw = allow_nsfw

        # Status-related attributes
        self.job_id = create_uuid()
        self.horde_job_id = horde_job_id
        self.wait_time = wait_time
        self.queue_position = queue_position
        self.done = done
        self.faulted = faulted
        self.kudos = kudos
        self.creation_time = time.time()
        self.mod_time = time.time()

    def to_json(self) -> Dict:
        return {
            "prompt": self.prompt,
            "params": {
                "sampler_name": self.sampler_name,
                "cfg_scale": self.cfg_scale,
                "seed": str(self.seed),
                "height": self.height,
                "width": self.width,
                "post_processing": [],
                "karras": self.karras,
                "hires_fix": self.hires_fix,
                "clip_skip": self.clip_skip,
                "steps": self.steps,
                "n": 1,
            },
            "nsfw": self.allow_nsfw,
            "trusted_workers": False,
            "slow_workers": True,
            "censor_nsfw": not self.allow_nsfw,
            "models": [self.model],
            "r2": True,
            "shared": False,
            "replacement_filter": True,
        }

    def __str__(self) -> str:
        return json.dumps({"ser": self.serialize(), "tj": self.to_json()})

    @classmethod
    def from_json(cls, data: Dict) -> Self:
        prompt = data.get("prompt")
        params = data.get("params", {})
        return cls(
            prompt=prompt,
            sampler_name=params.get("sampler_name"),
            cfg_scale=params.get("cfg_scale"),
            seed=params.get("seed"),
            width=params.get("width"),
            height=params.get("height"),
            karras=params.get("karras", True),
            hires_fix=params.get("hires_fix", True),
            clip_skip=params.get("clip_skip"),
            steps=params.get("steps"),
            model=data.get("models", ["INVALID_MODEL_NAME_HERE"])[0],
            allow_nsfw=data.get("nsfw", False),
        )

    def serialize(self):
        b = self.to_json()
        b["done"] = self.done
        b["faulted"] = self.faulted
        b["kudos"] = self.kudos
        b["id"] = self.job_id
        b["horde_job_id"] = self.horde_job_id
        b["queue_position"] = self.queue_position
        b["wait_time"] = self.wait_time
        b["mod_time"] = self.mod_time
        b["creation_time"] = self.creation_time
        return b

    @classmethod
    def deserialize(cls, value: Dict) -> Self:
        v = cls.from_json(value)
        v.done = value.get("done", False)
        v.faulted = value.get("faulted", False)
        v.kudos = value.get("kudos", 0)
        v.job_id = value.get("id", create_uuid())
        v.horde_job_id = value.get("horde_job_id")
        v.queue_position = value.get("queue_position", 0)
        v.wait_time = value.get("wait_time", 0)
        v.mod_time = time.time()
        v.creation_time = value.get("creation_time", time.time())
        return v

    def update_status(self, status_data: Dict):
        self.done = status_data.get("done", False)
        self.faulted = status_data.get("faulted", False)
        self.kudos = status_data.get("kudos", 0)
        self.queue_position = status_data.get("queue_position", 0)
        self.wait_time = status_data.get("wait_time", 0)
        self.mod_time = time.time()


class LocalJob:
    id: str
    path: Path
    original: Job
    fileType: str
    downloadURL: str

    def __init__(self, job: Job) -> None:
        self.id = job.job_id
        self.original = job
        self.fileType = "webp"
        self.path = (SAVED_IMAGE_DIR_PATH / self.id).with_suffix(".webp")

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "original": self.original.serialize(),
            "fileType": self.fileType,
            "path": str(self.path),
        }

    @classmethod
    def deserialize(cls, value: dict) -> Self:
        job = value.get("original")
        return cls(Job.deserialize(job))


class APIManagerThread(QThread):
    job_completed = Signal(LocalJob)  # Signal emitted when a job is completed
    updated = Signal()

    def __init__(self, api_key: str, max_requests: int, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.max_requests = max_requests
        self.current_requests: Dict[str, Job] = {}
        self.job_queue: Queue[Job] = Queue()
        self.last_status_time = time.time()
        self.last_async_time = time.time()
        self.completed_jobs: List[Job] = []
        self.running = True  # To control the thread's loop
        self.async_requests = 0
        self.async_reset_time = time.time()
        self.status_requests = 0
        self.status_reset_time = time.time()

        self.errored_jobs: List[Job] = []

    def run(self):
        while self.running:
            self.handle_queue()
            self.updated.emit()
            time.sleep(1)  # Sleep for a short time to avoid high CPU usage

    def serialize(self):
        return {
            "current_requests": {
                k: self.current_requests[k].serialize() for k in self.current_requests
            },
            "job_queue": [_.serialize() for _ in list(self.job_queue.queue)],
            "completed_jobs": [_.serialize() for _ in self.completed_jobs],
            "errored_jobs": [_.serialize() for _ in self.errored_jobs],
        }

    @classmethod
    def deserialize(
        cls,
        data: Dict,
        api_key: str,
        max_requests: int,
        parent=None,
    ):
        instance = cls(api_key, max_requests, parent)

        instance.current_requests = {
            k: Job.deserialize(v) for k, v in data.get("current_requests", {}).items()
        }

        instance.job_queue = Queue()
        for item in data.get("job_queue", []):
            instance.job_queue.put(Job.deserialize(item))

        instance.completed_jobs = [
            Job.deserialize(item) for item in data.get("completed_jobs", [])
        ]

        instance.errored_jobs = [
            Job.deserialize(item) for item in data.get("errored_jobs", [])
        ]

        return instance

    def handle_queue(self):
        self._send_new_jobs()
        self._update_current_jobs()
        self._get_download_paths()

    def _send_new_jobs(self):
        while (
            len(self.current_requests) < self.max_requests
            and not self.job_queue.empty()
        ):
            current_time = time.time()
            if current_time - self.last_async_time > 5 and self.async_requests < 10:
                job = self.job_queue.get()
                try:
                    d = json.dumps(job.to_json())
                    response = requests.post(
                        BASE_URL + "generate/async",
                        data=d,
                        headers=get_headers(self.api_key),
                    )
                    response.raise_for_status()
                    horde_job_id = response.json().get("id")
                    job.horde_job_id = horde_job_id
                    self.current_requests[job.job_id] = job
                    print(f"Job {job.job_id} now has horde uuid: " + job.horde_job_id)
                    self.last_async_time = time.time()
                    self.async_requests += 1
                except requests.RequestException as e:
                    print(f"Error sending job: {e}")
                    self.errored_jobs.append(job)
                    # self.job_queue.put(job)
            current_time = time.time()
            if current_time - self.async_reset_time > 60:
                self.async_requests = 0
                self.async_reset_time = current_time

    def _update_current_jobs(self):
        to_remove = []
        for job_id, job in self.current_requests.items():
            if time.time() - job.creation_time > 600:
                job.faulted = True
                to_remove.append(job_id)
                continue

            try:
                # print("checking job "+job_id)

                response = requests.get(BASE_URL + f"generate/check/{job.horde_job_id}")
                response.raise_for_status()
                job.update_status(response.json())
                if job.done:
                    self.completed_jobs.append(job)
                    to_remove.append(job_id)

                    # Emit the signal for the completed job
            except requests.RequestException as e:
                print(f"Error updating job status: {e}")

        for job_id in to_remove:
            del self.current_requests[job_id]

    def _get_download_paths(self):
        njobs = []
        for job in self.completed_jobs:
            if time.time() - self.last_status_time > 5 and self.status_requests < 10:

                lj = LocalJob(job)

                r = requests.get(BASE_URL + f"generate/status/{job.horde_job_id}")
                r.raise_for_status()
                rj = r.json()
                lj.downloadURL = rj["generations"][0]["img"]

                self.job_completed.emit(lj)

                self.last_status_time = time.time()
                if time.time() - self.status_reset_time > 60:
                    self.status_requests = 0
                    self.status_reset_time = time.time()
            else:
                njobs.append(job)
        self.completed_jobs = njobs

    def get_current_jobs(self) -> Dict[str, Job]:
        return self.current_requests

    def get_queued_jobs(self) -> List[Job]:
        return list(self.job_queue.queue)

    def get_completed_jobs(self) -> List[Job]:
        return self.completed_jobs

    def stop(self):
        self.running = False
        self.wait()

    def add_job(self, job: Job):
        self.job_queue.put(job)
        print("added job")


class DownloadThread(QThread):
    completed_downloads: List[LocalJob]
    queued_downloads: List[LocalJob]
    completed = Signal(LocalJob)

    def __init__(
        self, queued_downloads=[], completed_downloads=[], parent=None
    ) -> None:
        super().__init__(parent)
        self.queued_downloads = queued_downloads
        self.completed_downloads = completed_downloads
        self.running = True

    def add_dl(self, local_job: LocalJob):
        self.queued_downloads.append(local_job)

    def run(self):
        while self.running:
            if len(self.queued_downloads) > 0:
                lj = self.queued_downloads.pop()
                print("downloading " + lj.id)
                with open(lj.path, "wb") as f:
                    f.write(requests.get(lj.downloadURL).content)
                self.completed.emit(lj)
                self.completed_downloads.append(lj)
            time.sleep(1)

    def serialize(self):
        return {
            "completed_downloads": [x.serialize() for x in self.completed_downloads],
            "queued_downloads": [x.serialize() for x in self.queued_downloads],
        }

    @classmethod
    def deserialize(cls: Self, value: Dict):
        if (cd := value.get("completed_downloads", None)) is None:
            ncd = []
        else:
            cd: List[dict] = cd
            ncd = [LocalJob.deserialize(x) for x in cd]
        if (qd := value.get("queued_downloads", None)) is None:
            nqd = []
        else:
            qd: List[dict] = qd
            nqd = [LocalJob.deserialize(x) for x in qd]
        return cls(completed_downloads=ncd, queued_downloads=nqd)

    def stop(self):
        self.running = False
        self.wait()


class ModelPopup(QDialog):

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)

        self.ui: Ui_Dialog = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.baselineLineEdit.setText(data.get("baseline"))
        self.ui.nameLineEdit.setText(data.get("name"))
        self.ui.inpaintingCheckBox.setChecked(data.get("inpainting"))
        self.ui.descriptionBox.setText(data.get("description"))
        self.ui.versionLineEdit.setText(data.get("version"))
        self.ui.styleLineEdit.setText(data.get("style"))
        self.ui.nsfwCheckBox.setChecked(data.get("nsfw"))
        self.ui.unsupportedFeaturesLineEdit.setText(
            ", ".join(data.get("features_not_supported", []))
        )
        req: dict = data.get("requirements", {})
        req_str = ", ".join(" = ".join([str(y) for y in x]) for x in list(req.items()))
        self.ui.requirementsLineEdit.setText(req_str)


class LoadThread(QThread):
    progress = Signal(int)
    model_info = Signal(dict)
    user_info = Signal(requests.Response)

    def __init__(self, api_key: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.api_key = api_key

    def run(self):
        self.user_info.emit(
            requests.get(BASE_URL + "find_user", headers=get_headers(self.api_key))
        )
        self.progress.emit(50)
        p = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.CacheLocation
            )
        )
        # os.makedirs(p,exist_ok=True)
        model_cache_path = p / "model_ref.json"
        # print(QStandardPaths.locate(QStandardPaths.StandardLocation.CacheLocation,"model_ref.json"))

        if (
            not model_cache_path.exists()
            or time.time() - model_cache_path.stat().st_mtime > 60 * 60 * 24
        ):
            os.makedirs(p, exist_ok=True)
            r = requests.get(
                "https://raw.githubusercontent.com/Haidra-Org/AI-Horde-image-model-reference/main/stable_diffusion.json"
            )
            j = r.json()
            with open(model_cache_path, "wt") as f:
                json.dump(j, f)
        else:

            with open(model_cache_path, "rt") as f:
                j = json.load(f)

        self.model_info.emit(j)
        self.progress.emit(100)


class SavedData:
    api_state: dict
    current_images: List[dict]
    nsfw_allowed: bool
    max_jobs: int
    window_geometry: QByteArray
    window_state: QByteArray
    job_config: dict
    finished_jobs: list[Dict]

    def __init__(self) -> None:

        os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)

    def update(
        self,
        api: APIManagerThread,
        nsfw: bool,
        max_jobs: int,
        dlthread: DownloadThread,
        window: QMainWindow,
        job_config: dict,
    ):
        self.api_state = api.serialize()
        self.current_images = dlthread.serialize()
        self.max_jobs = max_jobs
        self.nsfw_allowed = nsfw
        self.window_geometry = window.saveGeometry()
        self.window_state = window.saveState()
        self.job_config = job_config

    def write(self):
        d = {
            "api_state": self.api_state,
            "max_jobs": self.max_jobs,
            "nsfw_allowed": self.nsfw_allowed,
            "current_images": self.current_images,
            "window_geometry": str(self.window_geometry.toBase64()),
            "window_state": str(self.window_state.toBase64()),
            "job_config": self.job_config,
        }
        # cbor2.dump ?
        jsondata = json.dumps(d)
        with open(SAVED_DATA_PATH, "wt") as f:
            f.write(jsondata)

    def read(self):
        if SAVED_DATA_PATH.exists():
            with open(SAVED_DATA_PATH, "rt") as f:
                j: dict = json.loads(f.read())
        else:
            j = dict()
        self.api_state = j.get("api_state", {})
        self.max_jobs = j.get("max_jobs", 5)
        self.current_images = j.get("current_images", {})
        self.nsfw_allowed = j.get("nsfw_allowed", False)
        self.job_config = j.get("job_config", {})
        wg = j.get("window_geometry", None)
        if wg is not None:
            self.window_geometry = QByteArray.fromBase64(bytes(wg, "utf-8"))
        else:
            self.window_geometry = None
        ws = j.get("window_state", None)
        if ws is not None:
            self.window_state = QByteArray.fromBase64(bytes(ws, "utf-8"))
        else:
            self.window_state = None


class MainWindow(QMainWindow):

    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        self.savedData = SavedData()
        self.savedData.read()

        self.clipboard = app.clipboard()
        self.model_dict: Dict[str, Model] = {}
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)
        if self.savedData.window_state is not None:
            self.restoreGeometry(self.savedData.window_state)
        if self.savedData.window_geometry is not None:
            self.restoreGeometry(self.savedData.window_geometry)
        self.restore_job_config(self.savedData.job_config)
        if (k := keyring.get_password("HordeQT", "HordeQTUser")) is not None:
            self.ui.apiKeyEntry.setText(k)
            self.api_key = k
        else:
            self.api_key = None
        self.loading_thread = LoadThread(self.api_key)
        self.show()
        self.ui.maxJobsSpinBox.setValue(self.savedData.max_jobs)
        self.ui.NSFWCheckBox.setChecked(self.savedData.nsfw_allowed)
        self.ui.GenerateButton.setEnabled(False)
        self.ui.modelComboBox.setEnabled(False)
        self.api_thread = APIManagerThread.deserialize(
            self.savedData.api_state,
            api_key=self.api_key,
            max_requests=self.savedData.max_jobs,
        )
        self.download_thread: DownloadThread = DownloadThread.deserialize(
            self.savedData.current_images
        )
        self.api_thread.job_completed.connect(self.on_job_completed)
        self.api_thread.updated.connect(self.update_inprogess_table)
        # Connect signals
        self.loading_thread.progress.connect(self.update_progress)
        self.loading_thread.model_info.connect(self.construct_model_dict)
        self.loading_thread.user_info.connect(self.update_user_info)

        self.ui.GenerateButton.clicked.connect(self.on_generate_click)
        self.ui.modelDetailsButton.clicked.connect(self.on_model_open_click)

        self.ui.apiKeyEntry.returnPressed.connect(self.save_api_key)
        self.ui.saveAPIkey.clicked.connect(self.save_api_key)
        self.ui.copyAPIkey.clicked.connect(self.copy_api_key)
        self.ui.showAPIKey.clicked.connect(self.toggle_api_key_visibility)
        self.ui.openSavedData.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(SAVED_DATA_DIR_PATH))
        )
        self.ui.openSavedImages.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(SAVED_IMAGE_DIR_PATH))
        )
        self.ui.progressBar.setValue(0)
        self.gallery_layout = MasonryLayout()
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_widget.setLayout(self.gallery_layout)

        scroll_area.setWidget(content_widget)

        self.ui.galleryView.addWidget(scroll_area)

        for lj in self.download_thread.completed_downloads:
            print(lj.path)
            self.gallery_layout.addImage(lj.path)
        # =MasonryGallery()
        QTimer.singleShot(0, self.loading_thread.start)
        QTimer.singleShot(0, self.download_thread.start)
        QTimer.singleShot(0, self.api_thread.start)

    def show_error(self, message):

        QMessageBox.critical(self, "Error", message)

    def show_warn(self, message):

        QMessageBox.warning(self, "Warning", message)

    def show_info(self, message):

        QMessageBox.information(self, "Info", message)

    def on_fully_loaded(self):
        self.ui.GenerateButton.setEnabled(True)
        self.ui.modelComboBox.setEnabled(True)
        # this doesn't feel right, for some reason.
        self.ui.maxJobsSpinBox.setMaximum(self.ui.maxConcurrencySpinBox.value())
        QTimer.singleShot(150, lambda: self.ui.progressBar.hide())

    def closeEvent(self, event):

        self.api_thread.stop()
        self.download_thread.stop()
        job_config = {
            "prompt": self.ui.PromptBox.toPlainText(),
            "negative_prompt": self.ui.NegativePromptBox.toPlainText(),
            "sampler_name": self.ui.samplerComboBox.currentText(),
            "cfg_scale": self.ui.guidenceDoubleSpinBox.value(),
            "seed": self.ui.seedSpinBox.value(),
            "width": self.ui.widthSpinBox.value(),
            "height": self.ui.heightSpinBox.value(),
            "clip_skip": self.ui.clipSkipSpinBox.value(),
            "steps": self.ui.stepsSpinBox.value(),
            "model": self.ui.modelComboBox.currentText(),
        }
        self.savedData.update(
            self.api_thread,
            self.ui.NSFWCheckBox.isChecked(),
            self.ui.maxJobsSpinBox.value(),
            self.download_thread,
            self,
            job_config,
        )
        self.savedData.write()
        QMainWindow.closeEvent(self, event)

    def restore_job_config(self, job_config: dict):

        # Restore job configuration

        self.ui.PromptBox.setPlainText(job_config.get("prompt", ""))
        self.ui.NegativePromptBox.setPlainText(job_config.get("negative_prompt", ""))
        self.ui.samplerComboBox.setCurrentText(
            job_config.get("sampler_name", "k_euler")
        )
        self.ui.guidenceDoubleSpinBox.setValue(job_config.get("cfg_scale", 5.0))
        self.ui.seedSpinBox.setValue(job_config.get("seed", 0))
        self.ui.widthSpinBox.setValue(job_config.get("width", 512))
        self.ui.heightSpinBox.setValue(job_config.get("height", 512))
        self.ui.clipSkipSpinBox.setValue(job_config.get("clip_skip", 1))
        self.ui.stepsSpinBox.setValue(job_config.get("steps", 20))
        self.ui.modelComboBox.setCurrentText(job_config.get("model", "default"))
        self.ui.NSFWCheckBox.setChecked(job_config.get("allow_nsfw", False))

    def on_job_completed(self, job: LocalJob):
        print(f"Job {job.id} completed.")
        self.download_thread.add_dl(job)

    def update_progress(self, value):
        self.ui.progressBar.setValue(value)
        if value == 100:
            self.loading_thread.quit()
            self.on_fully_loaded()

    def update_user_info(self, r: requests.Response):
        if r.status_code == 404:
            self.show_error("Invalid API key; User could not be found.")
            return
        j = r.json()
        self.user_info = j
        self.ui.usernameLineEdit.setText(j["username"])
        self.ui.idLineEdit.setText(str(j["id"]))
        self.ui.kudosSpinBox.setValue(j["kudos"])
        self.ui.maxConcurrencySpinBox.setValue(j["concurrency"])
        self.ui.moderatorCheckBox.setChecked(j["moderator"])
        self.ui.numberOfWorkersSpinBox.setValue(j["worker_count"])
        self.ui.trustedCheckBox.setChecked(j["trusted"])
        self.ui.serviceCheckBox.setChecked(j["service"])
        self.ui.educationCheckBox.setChecked(j["education"])
        self.ui.customizerCheckBox.setChecked(j["customizer"])
        self.ui.specialCheckBox.setChecked(j["special"])
        self.ui.pseudonymousCheckBox.setChecked(j["pseudonymous"])
        self.ui.accountAgeLineEdit.setText(str(j["account_age"]) + " seconds")
        self.ui.accountCreatedLineEdit.setText(
            (
                dt.datetime.fromtimestamp(time.time())
                - dt.timedelta(seconds=j["account_age"])
            ).isoformat()
        )
        records = j["records"]
        usage = records["usage"]
        contrib = records["contribution"]

        fulfill = records["fulfillment"]
        self.ui.textGeneratedSpinBox.setValue(fulfill["text"])
        self.ui.imageGeneratedSpinBox.setValue(fulfill["image"])
        self.ui.interrogationGeneratedSpinBox.setValue(fulfill["interrogation"])

        request = records["request"]

        self.ui.textRequestedSpinBox.setValue(request["text"])
        self.ui.imagesRequestedSpinBox.setValue(request["image"])
        self.ui.interrogationRequestedSpinBox.setValue(request["interrogation"])

        usage = records["usage"]
        self.ui.tokensRequestedSpinBox.setValue(usage["tokens"])
        self.ui.megapixelstepsRequestedDoubleSpinBox.setValue(usage["megapixelsteps"])

        contrib = records["contribution"]

        self.ui.tokensGeneratedSpinBox.setValue(contrib["tokens"])
        self.ui.megapixelstepsGeneratedDoubleSpinBox.setValue(contrib["megapixelsteps"])

    def toggle_api_key_visibility(self):
        visible = self.ui.apiKeyEntry.echoMode() == QLineEdit.EchoMode.Normal
        if visible:
            self.hide_api_key()
        else:
            self.show_api_key()

    def show_api_key(self):
        self.ui.showAPIKey.setText("Hide API Key")
        self.ui.apiKeyEntry.setEchoMode(QLineEdit.EchoMode.Normal)

    def hide_api_key(self):
        self.ui.showAPIKey.setText("Show API Key")
        self.ui.apiKeyEntry.setEchoMode(QLineEdit.EchoMode.Password)

    def create_job(self):
        prompt = self.ui.PromptBox.toPlainText()
        if prompt.strip() == "":
            self.show_error("Prompt can not be empty")
            return None
        np = self.ui.NegativePromptBox.toPlainText()
        if np.strip() != "":
            prompt = prompt + " ### " + np

        sampler_name = self.ui.samplerComboBox.currentText()
        cfg_scale = self.ui.guidenceDoubleSpinBox.value()
        seed = self.ui.seedSpinBox.value()
        if seed == 0:
            seed = random.randint(0, 2**31 - 1)
        width = self.ui.widthSpinBox.value()
        height = self.ui.heightSpinBox.value()
        clip_skip = self.ui.clipSkipSpinBox.value()
        steps = self.ui.stepsSpinBox.value()
        model = self.model_dict[self.ui.modelComboBox.currentText()].name
        karras = True
        hires_fix = True
        allow_nsfw = True
        job = Job(
            prompt,
            sampler_name,
            cfg_scale,
            seed,
            width,
            height,
            clip_skip,
            steps,
            model,
            karras,
            hires_fix,
            allow_nsfw,
        )
        return job

    def construct_model_dict(self, mod):
        self.ui.modelComboBox.clear()

        # mod = sd_mod_ref
        models: List[Model] = self.get_available_models()
        models.sort(key=lambda k: k["count"], reverse=True)
        model_dict: Dict[str, Model] = {}
        for n in models:
            name = n.get("name", "Unknown")
            count = n.get("count", 0)
            self.ui.modelComboBox.addItem(k := f"{name} ({count})")
            m = Model()
            m.count = count
            m.eta = n.get("eta", 0)
            m.jobs = n.get("jobs", 0)
            m.name = name
            m.performance = n.get("performance", 0)
            m.queued = n.get("queued", 0)
            m.type = "image"
            m.details = mod[m.name]
            model_dict[k] = m
        self.ui.modelComboBox.setCurrentIndex(0)
        self.model_dict = model_dict

    def get_available_models(self) -> List[Model]:
        r = requests.get(
            BASE_URL + "status/models",
            params={"type": "image", "min_count": 1, "model_state": "all"},
        )
        r.raise_for_status()
        return r.json()

    def get_model_details(self, available_models: Optional[List[Model]]):
        if available_models == None:
            available_models = self.get_available_models()

    def on_model_open_click(self):
        curr_model = self.model_dict[self.ui.modelComboBox.currentText()]
        print(json.dumps(curr_model.details))
        ModelPopup(curr_model.details)

    def on_generate_click(self):
        # self.show_info("Generate was clicked!")
        job = self.create_job()
        if job is not None:
            print(json.dumps(self.create_job().to_json()))
            self.api_thread.add_job(job)

    def save_api_key(self):
        self.hide_api_key()
        self.api_key = self.ui.apiKeyEntry.text()
        keyring.set_password("HordeQT", "HordeQTUser", self.api_key)
        self.show_info("API Key saved sucessfully.")
        self.update_user_info()

    def copy_api_key(self):
        # Is this confusing to the user? Would they expect the copy to copy what's currently in the api key, or the last saved value?
        self.clipboard.setText(self.api_key)

    def update_row(self, row, id: str, status: str, prompt: str, model: str, eta: int):
        # ID, STATUS, PROMPT, MODEL, ETA
        table = self.ui.inProgressItemsTable
        table.setSortingEnabled(False)

        for col, value in enumerate(
            [
                id,
                status,
                prompt,
                model,
                (
                    "Done"
                    if eta == -1
                    else hr.time_delta(dt.datetime.now() + dt.timedelta(seconds=eta))
                ),
            ]
        ):
            item = table.item(row, col)
            if item is None:
                item = QTableWidgetItem()
                table.setItem(row, col, item)
            item.setText(value)

        table.setSortingEnabled(True)

    def update_inprogess_table(self):
        table = self.ui.inProgressItemsTable
        table.setUpdatesEnabled(True)
        current_jobs = self.api_thread.current_requests
        for job_id in current_jobs.keys():
            job = current_jobs[job_id]
            r = table.findItems(job_id, Qt.MatchFlag.MatchFixedString)
            if len(r) == 0:
                if table.columnCount() == 0:
                    table.setColumnCount(5)  # Set the number of columns
                row = table.rowCount()
                table.insertRow(row)
            else:
                row = r[0].row()

            self.update_row(
                row,
                job_id,
                "In Progress",
                job.prompt[: min(len(job.prompt), 50)],
                job.model,
                job.wait_time,
            )
        for lj in self.download_thread.completed_downloads:
            r = table.findItems(lj.id, Qt.MatchFlag.MatchFixedString)
            if len(r) == 0:
                if table.columnCount() == 0:
                    table.setColumnCount(5)  # Set the number of columns
                row = table.rowCount()
                table.insertRow(row)
            else:
                row = r[0].row()

            self.update_row(
                row,
                lj.id,
                "Done",
                lj.original.prompt[: min(len(lj.original.prompt), 50)],
                lj.original.model,
                -1,
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Horde QT")
    app.setOrganizationName("Unit1208")
    SAVED_DATA_DIR_PATH = Path(
        QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    )
    SAVED_IMAGE_DIR_PATH = SAVED_DATA_DIR_PATH / "images"

    SAVED_DATA_PATH = SAVED_DATA_DIR_PATH / "saved_data.json"
    print(SAVED_DATA_PATH, SAVED_IMAGE_DIR_PATH)
    os.makedirs(SAVED_IMAGE_DIR_PATH, exist_ok=True)
    os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)

    widget = MainWindow(app)
    widget.show()
    sys.exit(app.exec())
