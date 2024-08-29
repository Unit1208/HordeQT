# This Python file uses the following encoding: utf-8
from dataclasses import dataclass
import datetime as dt
import enum
import re
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
    QDialog,
    QLineEdit,
    QWidget,
    QLayout,
    QSizePolicy,
    QLabel,
    QDockWidget,
    QScrollArea,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
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
)
from pyqttoast import Toast, ToastPreset, toast_enums
from PySide6.QtGui import QPixmap, QDesktopServices, QFont, QClipboard

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

def prompt_matrix(prompt: str) -> List[str]:
    # fails with nested brackets, but that shouldn't be an issue?
    # Writing this out, {{1|2}|{3|4}} would evalutate to e.g [1,2,3,4], and I doubt that anyone would the former. If they do, I'll fix it. Maybe.
    # {{1|2|3|4}} should evalutate to [1,2,3,4] as well.
    matched_matrix = re.finditer(r"\{.+?\}", prompt, re.M)

    def generate_prompts(current_prompt: str, matches: List[str]) -> List[str]:
        if not matches:
            return [current_prompt]

        matched = matches[0]
        remaining_matches = matches[1:]

        # Strip brackets and split by '|'
        options = matched[1:-1].split("|")

        # Recursively generate all combinations.
        # If you hit the stack limit, that's on you, it shouldn't happen.
        generated_prompts = []
        for option in options:
            new_prompt = current_prompt.replace(matched, option, 1)
            generated_prompts.extend(generate_prompts(new_prompt, remaining_matches))

        return generated_prompts

    matches = [match.group() for match in matched_matrix]
    result_prompts = generate_prompts(prompt, matches)

    # If no valid combinations were generated, return the original prompt
    return result_prompts if result_prompts else [prompt]

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
        share_image: bool = True,
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
        self.share_image = share_image

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
            "shared": self.share_image,
            # This should never need to be turned off.
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
    completed_at:int

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
            "completed_at":self.completed_at
        }

    @classmethod
    def deserialize(cls, value: dict) -> Self:
        job = value.get("original")
        lj= cls(Job.deserialize(job))
        lj.completed_at=value.get("completed_at",time.time())
        return lj


class ImageWidget(QLabel):
    imageClicked = Signal(QPixmap)

    def __init__(self, lj:LocalJob):
        super().__init__()
        self.lj=lj
        self.original_pixmap = QPixmap(lj.path)
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

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.imageClicked.emit(self.original_pixmap)
        super().mouseReleaseEvent(event)


class ImagePopup(QDockWidget):
    def copy_prompt(self):
        print("Copying")
        self._parent.clipboard.setText(self.lj.original.prompt)
        
    
    def copy_all(self):
        pass
    # TODO: Implement buttons - Signal for each.
    def __init__(self, pixmap:QPixmap, lj:LocalJob, parent=None):
        super().__init__("Image Viewer", parent)
        self._parent=parent
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.lj=lj
        # Create a label to display the image
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create buttons
        use_prompt = QPushButton("Use Prompt")
        use_all = QPushButton("Use All")
        copy_prompt = QPushButton("Copy Prompt")
        copy_prompt.clicked.connect(self.copy_prompt)
        copy_all = QPushButton("Copy All")
        show_details = QPushButton("Show Details")

        # Create horizontal layouts for button pairs
        copy_layout = QHBoxLayout()
        copy_layout.addWidget(copy_prompt)
        copy_layout.addWidget(copy_all)

        use_layout = QHBoxLayout()
        use_layout.addWidget(use_prompt)
        use_layout.addWidget(use_all)

        # Create a main vertical layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(copy_layout)
        layout.addLayout(use_layout)
        layout.addWidget(show_details)

        # Create a central widget to set the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the widget for the QDockWidget
        self.setWidget(widget)

        self.setFloating(True)
        self.resize(400, 400)  # Adjust the size of the popup window


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

    def addImage(self, path: os.PathLike,lj:LocalJob):
        image_widget = ImageWidget(path,lj)
        self.addWidget(image_widget)

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
        if (
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
                lj.completed_at=time.time()
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
    def reload_user_info(self,api_key):
        self.api_key=api_key
        self.user_info.emit(
            requests.get(BASE_URL + "find_user", headers=get_headers(api_key))
        )
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
    current_open_tab: int
    current_images: List[dict]
    finished_jobs: list[Dict]
    job_config: dict
    max_jobs: int
    nsfw_allowed: bool
    share_images: bool

    def __init__(self) -> None:

        os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)

    def update(
        self,
        api: APIManagerThread,
        nsfw: bool,
        max_jobs: int,
        dlthread: DownloadThread,
        job_config: dict,
        share_images: bool,
        current_open_tab: int,
    ):
        self.api_state = api.serialize()
        self.current_images = dlthread.serialize()
        self.max_jobs = max_jobs
        self.nsfw_allowed = nsfw
        self.share_images = share_images
        self.job_config = job_config
        self.current_open_tab = current_open_tab

    def write(self):
        d = {
            "api_state": self.api_state,
            "max_jobs": self.max_jobs,
            "nsfw_allowed": self.nsfw_allowed,
            "current_images": self.current_images,
            "job_config": self.job_config,
            "share_images": self.share_images,
            "current_open_tab": self.current_open_tab,
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
        self.share_images = j.get("share_images", True)
        self.job_config = j.get("job_config", {})
        self.current_open_tab = j.get("current_open_tab", 0)


class MainWindow(QMainWindow):

    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        self.savedData = SavedData()
        self.savedData.read()

        self.clipboard = app.clipboard()
        self.model_dict: Dict[str, Model] = {}
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)

        self.restore_job_config(self.savedData.job_config)
        if (k := keyring.get_password("HordeQT", "HordeQTUser")) is not None:
            self.ui.apiKeyEntry.setText(k)
            self.api_key = k
        else:
            self.api_key = None
        
        self.loading_thread = LoadThread(self.api_key)
        self.hide_api_key()
        self.show()
        self.ui.maxJobsSpinBox.setValue(self.savedData.max_jobs)
        self.ui.NSFWCheckBox.setChecked(self.savedData.nsfw_allowed)
        self.ui.shareImagesCheckBox.setChecked(self.savedData.share_images)
        self.ui.tabWidget.setCurrentIndex(self.savedData.current_open_tab)
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
        self.download_thread.completed.connect(self.on_image_fully_downloaded)
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
        self.ui.presetComboBox.currentTextChanged.connect(self.on_preset_change)
        self.ui.widthSpinBox.valueChanged.connect(self.on_width_change)
        self.ui.heightSpinBox.valueChanged.connect(self.on_height_change)
        self.ui.resetSettingsButton.clicked.connect(self.reset_job_config)
        self.ui.undoResetButton.clicked.connect(self.undo_reset_job_config)
        self.ui.undoResetButton.setEnabled(False)
        self.preset_being_updated = False
        self.last_job_config: Optional[Dict] = None
        self.gallery_layout = MasonryLayout()
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_widget.setLayout(self.gallery_layout)

        scroll_area.setWidget(content_widget)

        self.ui.galleryView.addWidget(scroll_area)

        for lj in self.download_thread.completed_downloads:
            print(lj.path)
            self.add_image_to_gallery(lj)
        Toast.setAlwaysOnMainScreen(True)
        Toast.setPosition(toast_enums.ToastPosition.TOP_RIGHT)
        Toast.setPositionRelativeToWidget(self)
        # =MasonryGallery()
        QTimer.singleShot(0, self.loading_thread.start)
        QTimer.singleShot(0, self.download_thread.start)
        QTimer.singleShot(0, self.api_thread.start)

    def closeEvent(self, event):

        self.api_thread.stop()
        self.download_thread.stop()
        self.savedData.update(
            self.api_thread,
            self.ui.NSFWCheckBox.isChecked(),
            self.ui.maxJobsSpinBox.value(),
            self.download_thread,
            self.get_job_config(),
            self.ui.shareImagesCheckBox.isChecked(),
            self.ui.tabWidget.currentIndex(),
        )
        self.savedData.write()
        QMainWindow.closeEvent(self, event)

    def get_job_config(self):
        return {
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

    def on_width_change(self):
        if not self.preset_being_updated:
            self.ui.presetComboBox.setCurrentIndex(0)

    def on_height_change(self):
        if not self.preset_being_updated:
            self.ui.presetComboBox.setCurrentIndex(0)

    def on_preset_change(self):
        current_model_needs_1024 = self.model_dict[
            self.ui.modelComboBox.currentText()
        ].details.get("baseline", None) in ["stable_diffusion_xl", "stable_cascade"]
        self.preset_being_updated = True
        match self.ui.presetComboBox.currentIndex():
            case 0:
                pass
            case 1:
                # LANDSCAPE (16:9)
                self.ui.widthSpinBox.setValue(1024)
                self.ui.heightSpinBox.setValue(576)
            case 2:
                # LANDSCAPE (3:2)
                if current_model_needs_1024:
                    self.ui.widthSpinBox.setValue(1024)
                    self.ui.heightSpinBox.setValue(704)
                else:
                    self.ui.widthSpinBox.setValue(768)
                    self.ui.heightSpinBox.setValue(512)
            case 3:
                # PORTRAIT (2:3)
                if current_model_needs_1024:
                    self.ui.widthSpinBox.setValue(704)
                    self.ui.heightSpinBox.setValue(1024)
                else:
                    self.ui.widthSpinBox.setValue(512)
                    self.ui.heightSpinBox.setValue(768)
            case 4:
                # PHONE BACKGROUND (9:21)
                self.ui.widthSpinBox.setValue(448)
                self.ui.heightSpinBox.setValue(1024)
            case 5:
                # ULTRAWIDE (21:9)
                self.ui.widthSpinBox.setValue(1024)
                self.ui.heightSpinBox.setValue(448)
            case 6:
                if current_model_needs_1024:
                    self.ui.widthSpinBox.setValue(1024)
                    self.ui.heightSpinBox.setValue(1024)
                else:
                    self.ui.widthSpinBox.setValue(512)
                    self.ui.heightSpinBox.setValue(512)
        self.preset_being_updated = False

    def on_image_fully_downloaded(self, lj: LocalJob):
        self.add_image_to_gallery(lj)

    def add_image_to_gallery(self, lj:LocalJob):
        image_widget = ImageWidget(lj)
        image_widget.imageClicked.connect(lambda v:self.show_image_popup(v,lj))
        self.gallery_layout.addWidget(image_widget)

    def show_image_popup(self, pixmap, lj):
        popup = ImagePopup(pixmap, lj,self)
        self.addDockWidget(Qt.RightDockWidgetArea, popup)
        popup.show()

    def on_fully_loaded(self):
        self.ui.GenerateButton.setEnabled(True)
        self.ui.modelComboBox.setEnabled(True)
        # this doesn't feel right, for some reason.
        self.ui.maxJobsSpinBox.setMaximum(self.ui.maxConcurrencySpinBox.value())
        QTimer.singleShot(150, lambda: self.ui.progressBar.hide())

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

    def undo_reset_job_config(self):
        if self.last_job_config is not None:
            self.restore_job_config(self.last_job_config)

    def reset_job_config(self):
        self.last_job_config = self.get_job_config()
        self.ui.undoResetButton.setEnabled(True)
        # Restore the job config, using the defaults for everything. Model needs to be set after, as the default is "default"
        self.restore_job_config({})
        self.ui.modelComboBox.setCurrentIndex(0)

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
            self.show_error_toast("Invalid API key; User could not be found.")
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

    def create_jobs(self) -> Optional[List[Job]]:
        prompt = self.ui.PromptBox.toPlainText()
        if prompt.strip() == "":
            self.show_error_toast("Prompt error", "Prompt cannot be empty")
            return None
        np = self.ui.NegativePromptBox.toPlainText()
        if np.strip() != "":
            """
            NOTE: the subsequent call to prompt matrix could do some *really* dumb stuff with this current implementation.
            Along the lines of:

            Prompt: This is a {test|
            Negative Prompt: negative test}
            new prompt: This is a {test| ### negative test}

            prompt matrix: [This is a test, this is a  ### negative test]
            "###" delineates prompt from negative prompt in the horde. i.e prompt ### negative prompt
            *To be fair*, you'd either be an idiot or know exactly what you're doing to encounter this. -\_o_/-
            """
            prompt = prompt + " ### " + np
        sampler_name = self.ui.samplerComboBox.currentText()
        cfg_scale = self.ui.guidenceDoubleSpinBox.value()

        seed = self.ui.seedSpinBox.value()

        width = self.ui.widthSpinBox.value()
        height = self.ui.heightSpinBox.value()
        clip_skip = self.ui.clipSkipSpinBox.value()
        steps = self.ui.stepsSpinBox.value()
        model_details = self.model_dict[self.ui.modelComboBox.currentText()]
        model = model_details.name
        reqs: Optional[Dict[str, int | str]] = model_details.details.get(
            "requirements", None
        )
        if reqs is not None:
            # Pony is the largest family of models to have this issue, but dreamshaperXL also has a specific configuration.
            if reqs.get("clip_skip", None) == 2:
                if clip_skip == 1:
                    self.show_warn_toast(
                        "CLIP Skip Requirement", "This model requires CLIP Skip = 2"
                    )
                    self.ui.clipSkipSpinBox.setValue(2)
                    return
            if (mins := reqs.get("min_steps", None)) is not None:
                if steps < mins:
                    self.show_warn_toast(
                        "Min Steps",
                        f"This model requires at least {mins} steps, currently {steps}",
                    )
                    self.ui.stepsSpinBox.setValue(mins)
                    return

            if (maxs := reqs.get("max_steps", None)) is not None:
                if steps > maxs:
                    self.show_warn_toast(
                        "Max Steps",
                        f"This model requires at most {maxs} steps, currently {steps}",
                    )
                    self.ui.stepsSpinBox.setValue(maxs)
                    return
            if (cfgreq := reqs.get("cfg_scale", None)) is not None:
                if cfg_scale != cfgreq:
                    self.show_warn_toast(
                        "Min Steps",
                        f"This model requires a CFG value of {cfgreq}, currently {cfg_scale}",
                    )
                    self.ui.guidenceDoubleSpinBox.setValue(float(cfgreq))
                    return
            if (rsamplers := reqs.get("samplers", None)) is not None:
                if sampler_name not in rsamplers:
                    samplertext = ""
                    for n in rsamplers:
                        samplertext += '"' + n + '",'
                    samplertext = samplertext[:-1]
                    self.show_warn_toast(
                        "Wrong Sampler",
                        "This mode requires the use of one of "
                        + samplertext
                        + " samplers",
                    )
                    self.ui.samplerComboBox = rsamplers[0]
                    return
        karras = True
        hires_fix = True
        allow_nsfw = self.ui.NSFWCheckBox.isChecked()
        share_image = self.ui.shareImagesCheckBox.isChecked()
        prompts = prompt_matrix(prompt)
        prompts *= self.ui.imagesSpinBox.value()
        jobs = []
        for nprompt in prompts:
            #if the user hasn't provided a seed, pick one. It must be under 2**31 so that we can display it on a spinbox eventually.
            #something something C++.
            if seed == 0:
                sj_seed = random.randint(0, 2**31 - 1)
            else:
                sj_seed=seed
            job = Job(
                nprompt,
                sampler_name,
                cfg_scale,
                sj_seed,
                width,
                height,
                clip_skip,
                steps,
                model,
                karras,
                hires_fix,
                allow_nsfw,
                share_image,
            )
            jobs.append(job)
        return jobs

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
        jobs = self.create_jobs()
        if jobs is not None:
            for n in range(len(jobs)):
                self.api_thread.add_job(jobs[n])
                # print(jobs[n])
            self.show_success_toast("Created!", "Jobs were created and put into queue")

    def save_api_key(self):
        self.hide_api_key()
        self.api_key = self.ui.apiKeyEntry.text()
        keyring.set_password("HordeQT", "HordeQTUser", self.api_key)
        self.show_success_toast("Saved","API Key saved sucessfully.")
        self.loading_thread.reload_user_info(self.api_key)

    def copy_api_key(self):
        # Is this confusing to the user? Would they expect the copy to copy what's currently in the api key, or the last saved value?
        self.clipboard.setText(self.api_key)

    def show_success_toast(self, title, message, duration=5000):
        success_toast = Toast(self)
        success_toast.setDuration(duration)
        success_toast.setTitle(title)
        success_toast.setText(message)
        success_toast.applyPreset(
            ToastPreset.SUCCESS
            if app.styleHints() == Qt.ColorScheme.Light
            else ToastPreset.SUCCESS_DARK
        )
        success_toast.show()

    def show_info_toast(self, title, message, duration=5000):
        info_toast = Toast(self)
        info_toast.setDuration(duration)
        info_toast.setTitle(title)
        info_toast.setText(message)
        info_toast.applyPreset(
            ToastPreset.INFORMATION
            if app.styleHints() == Qt.ColorScheme.Light
            else ToastPreset.INFORMATION_DARK
        )
        info_toast.show()

    def show_error_toast(self, title, message, duration=5000):
        error_toast = Toast(self)
        error_toast.setDuration(duration)
        error_toast.setTitle(title)
        error_toast.setText(message)
        error_toast.applyPreset(
            ToastPreset.ERROR
            if app.styleHints() == Qt.ColorScheme.Light
            else ToastPreset.ERROR_DARK
        )
        error_toast.show()

    def show_warn_toast(self, title, message, duration=5000):
        warn_toast = Toast(self)
        warn_toast.setDuration(duration)
        warn_toast.setTitle(title)
        warn_toast.setText(message)
        warn_toast.applyPreset(
            ToastPreset.WARNING
            if app.styleHints() == Qt.ColorScheme.Light
            else ToastPreset.WARNING_DARK
        )
        warn_toast.show()

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
                    # FIXME: This is hacky, I don't like it.
                    "Done"
                    if eta == -1
                    else ("Unknown" if eta==-2 else hr.time_delta(dt.datetime.now() + dt.timedelta(seconds=eta))+ " ago" if eta<0 else "")
                ),
            ]
        ):
            item = table.item(row, col)

            if item is None:
                item = QTableWidgetItem()
                table.setItem(row, col, item)
            font = QFont()
            font.setStyleHint(
                QFont.StyleHint.Monospace
            )  # Set the style hint to Monospace
            font.setFamily(
                "Monospace"
            )  # This ensures a fallback to a common monospace font
            item.setFont(font)
            item.setText(value)
        table.resizeColumnsToContents()
        # self.ui.groupBox_2.resize()
        table.setSortingEnabled(True)

    def update_inprogess_table(self):
        table = self.ui.inProgressItemsTable
        table.setUpdatesEnabled(True)
        for job in self.api_thread.job_queue.queue:
            r = table.findItems(job.id, Qt.MatchFlag.MatchFixedString)
            if len(r) == 0:
                if table.columnCount() == 0:
                    table.setColumnCount(5)  # Set the number of columns
                row = table.rowCount()
                table.insertRow(row)
            else:
                row = r[0].row()

            self.update_row(
                row,
                job.id,
                "Queued",
                job.original.prompt[: min(len(lj.original.prompt), 50)],
                job.original.model,
                -2,
            )
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
                lj.completed_at-time.time(),
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
