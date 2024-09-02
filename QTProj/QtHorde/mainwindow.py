# This Python file uses the following encoding: utf-8
import datetime as dt
import tempfile
import human_readable as hr
from pathlib import Path
import json
import os
import random
import sys
import time
from typing import List, Dict, Optional, Self, Type
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
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
    QLayoutItem,
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
    QSize,
)
from pyqttoast import Toast, ToastPreset, toast_enums
from PySide6.QtGui import QPixmap, QDesktopServices, QFont, QClipboard

from queue import Queue
import logging
import coloredlogs


from model_dialog import ModelPopup
from ui_form import Ui_MainWindow

import keyring
import requests
from util import create_uuid,get_headers,prompt_matrix
from classes import Job,LocalJob,Model, apply_metadata_to_image
ANON_API_KEY = "0000000000"
BASE_URL = "https://aihorde.net/api/v2/"
LOGGER = logging.getLogger("HordeQT")
coloredlogs.install("DEBUG", milliseconds=True)






class ImageWidget(QLabel):
    imageClicked = Signal(QPixmap)

    def __init__(self, lj: LocalJob):
        super().__init__()
        self.lj = lj
        self.original_pixmap = QPixmap(lj.path)
        self.setPixmap(self.original_pixmap)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.setPixmap(scaled_pixmap)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            LOGGER.debug(f"Gallery view item for {self.lj.id} was clicked")
            self.imageClicked.emit(self.original_pixmap)
        super().mouseReleaseEvent(ev)


class ImagePopup(QDockWidget):
    def copy_prompt(self):
        LOGGER.debug(f"Copying prompt for {self.lj.id}")
        self._parent.clipboard.setText(self.lj.original.prompt)

    def copy_all(self):
        pass

    # TODO: Implement buttons - Signal for each.
    def __init__(self, pixmap: QPixmap, lj: LocalJob, parent: "MainWindow"):
        super().__init__("Image Viewer", parent)
        self._parent = parent
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.lj = lj
        # Create a label to display the image
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

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
        self.m_spacing = spacing
        self.items: List[QLayoutItem] = []
        self.column_heights = []

    def addItem(self, arg__1):
        self.items.append(arg__1)

    def count(self):
        return len(self.items)

    def sizeHint(self):
        if not self.column_heights:
            self.updateGeometry()
        total_height = max(self.column_heights, default=0) + self.m_spacing
        return QSize(self.geometry().width(), total_height)

    def itemAt(self, index) -> QLayoutItem:
        try:
            return self.items[index]
        except IndexError:
            return None  # type: ignore

    def takeAt(self, index):
        return self.items.pop(index)

    def setGeometry(self, rect):  # type: ignore
        super(MasonryLayout, self).setGeometry(rect)
        self.updateGeometry()

    def updateGeometry(self):
        if not self.items:
            return
        width = self.geometry().width()
        self.calculateColumnLayout(width)
        self.arrangeItems()

    def calculateColumnLayout(self, width):
        self.num_columns = max(1, width // (200 + self.m_spacing))
        self.column_width = (
            width - (self.num_columns - 1) * self.m_spacing
        ) // self.num_columns
        self.column_heights = [0] * self.num_columns

    def arrangeItems(self):
        x_offsets = [
            i * (self.column_width + self.m_spacing) for i in range(self.num_columns)
        ]
        for item in self.items:
            widget: ImageWidget = item.widget()  # type: ignore
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
            self.column_heights[min_col] += height + self.m_spacing

        # Ensure the container widget height is adjusted based on the tallest column
        self.parentWidget().setMinimumHeight(max(self.column_heights) + self.m_spacing)


class ImageGalleryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.m_layout = MasonryLayout(self)
        self.setLayout(self.m_layout)


class APIManagerThread(QThread):
    job_completed = Signal(LocalJob)  # Signal emitted when a job is completed
    updated = Signal()

    def __init__(self, api_key: str, max_requests: int, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.max_requests = max_requests
        self.current_requests: Dict[str, Job] = {}
        self.job_queue: Queue[Job] = Queue()
        self.status_rl_reset = time.time()
        self.generate_rl_reset = time.time()
        self.completed_jobs: List[Job] = []
        self.running = True  # To control the thread's loop
        self.generate_rl_remaining = 1
        self.async_reset_time = time.time()
        self.status_rl_remaining = 1
        self.status_reset_time = time.time()

        self.errored_jobs: List[Job] = []

    def run(self):
        LOGGER.debug("API thread started")
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
            if (
                time.time() - self.generate_rl_reset
            ) > 0 and self.generate_rl_remaining > 0:
                job = self.job_queue.get()
                try:
                    d = json.dumps(job.to_json())
                    response = requests.post(
                        BASE_URL + "generate/async",
                        data=d,
                        headers=get_headers(self.api_key),
                    )
                    if response.status_code == 429:
                        self.job_queue.put(job)
                        self.generate_rl_reset = time.time() + 5
                        return
                    response.raise_for_status()
                    horde_job_id = response.json().get("id")
                    job.horde_job_id = horde_job_id
                    self.current_requests[job.job_id] = job
                    LOGGER.info(
                        f"Job {job.job_id} now has horde uuid: " + job.horde_job_id
                    )
                    self.generate_rl_reset = float(
                        response.headers.get("x-ratelimit-reset") or time.time() + 2
                    )
                    self.generate_rl_remaining = int(
                        response.headers.get("x-ratelimit-remaining") or 1
                    )
                except requests.RequestException as e:
                    LOGGER.error(e)
                    self.errored_jobs.append(job)
                    # self.job_queue.put(job)
            else:
                LOGGER.debug(
                    "Too many requests would be made, skipping a possible new job"
                )
            current_time = time.time()
            if current_time - self.generate_rl_reset > 0:
                self.generate_rl_remaining = 2

    def _update_current_jobs(self):
        to_remove = []
        for job_id, job in self.current_requests.items():
            if time.time() - job.creation_time > 600:
                LOGGER.info(
                    f'Job "{job_id}" was created more than 10 minutes ago, likely errored'
                )
                job.faulted = True
                to_remove.append(job_id)
                continue

            try:
                LOGGER.debug(f"Checking job {job_id} - ({job.horde_job_id})")
                response = requests.get(BASE_URL + f"generate/check/{job.horde_job_id}")
                response.raise_for_status()
                job.update_status(response.json())
                if job.done:
                    LOGGER.info(f"Job {job_id} done")
                    self.completed_jobs.append(job)
                    to_remove.append(job_id)

                    # Emit the signal for the completed job
            except requests.RequestException as e:
                LOGGER.error(e)

        for job_id in to_remove:
            del self.current_requests[job_id]

    def _get_download_paths(self):
        njobs = []
        for job in self.completed_jobs:
            if (
                time.time() - self.status_rl_reset
            ) > 0 and self.status_rl_remaining > 0:

                lj = LocalJob(job,SAVED_IMAGE_DIR_PATH)
                try:
                    r = requests.get(BASE_URL + f"generate/status/{job.horde_job_id}")
                    if r.status_code == 429:
                        njobs.append(job)
                        self.status_rl_reset = time.time() + 10
                        continue
                    r.raise_for_status()
                    rj = r.json()
                    gen = rj["generations"][0]
                    lj.downloadURL = gen["img"]
                    lj.worker_id = gen["worker_id"]
                    lj.worker_name = gen["worker_name"]
                    lj.completed_at = time.time()
                    self.status_reset_time = float(
                        r.headers.get("x-ratelimit-reset") or time.time() + 60
                    )
                    self.status_rl_remaining = int(
                        r.headers.get("x-ratelimit-remaining") or 1
                    )
                    self.job_completed.emit(lj)
                except requests.RequestException as e:
                    LOGGER.error(e)
                self.status_rl_reset = time.time()
                if time.time() - self.status_reset_time > 0:
                    self.status_rl_remaining = 1
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
        LOGGER.debug("Stopping API thread")
        self.running = False
        self.wait()
        LOGGER.debug("API thread stopped.")

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
                LOGGER.info(f"Downloading {lj.id}")
                tf = tempfile.NamedTemporaryFile()
                tf.write(requests.get(lj.downloadURL).content)
                apply_metadata_to_image(Path(tf.name), lj)
                tf.close()
                LOGGER.debug(f"{lj.id} downloaded")
                self.completed.emit(lj)
                self.completed_downloads.append(lj)
            time.sleep(1)

    def serialize(self):
        return {
            "completed_downloads": [x.serialize() for x in self.completed_downloads],
            "queued_downloads": [x.serialize() for x in self.queued_downloads],
        }

    @classmethod
    def deserialize(cls: type[Self], value: Dict):
        if (cd := value.get("completed_downloads", None)) is None:
            ncd = []
        else:
            cd: List[dict] = cd
            ncd = [LocalJob.deserialize(x,SAVED_IMAGE_DIR_PATH) for x in cd]
        if (qd := value.get("queued_downloads", None)) is None:
            nqd = []
        else:
            qd: List[dict] = qd
            nqd = [LocalJob.deserialize(x,SAVED_IMAGE_DIR_PATH) for x in qd]
        return cls(completed_downloads=ncd, queued_downloads=nqd)

    def stop(self):
        self.running = False
        self.wait()




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
        # os.makedirs(p,exist_ok=True)
        model_cache_path = p / "model_ref.json"

        # print(QStandardPaths.locate(QStandardPaths.StandardLocation.CacheLocation,"model_ref.json"))

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


class SavedData:
    api_state: dict
    current_open_tab: int
    current_images: List[dict]
    finished_jobs: list[Dict]
    job_config: dict
    max_jobs: int
    nsfw_allowed: bool
    share_images: bool
    prefered_format: str

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
        prefered_format: str,
    ):
        self.api_state = api.serialize()
        self.current_images = (dlv := dlthread.serialize()).get(
            ("completed_downloads"), []
        )
        self.queued_downloads = dlv.get(("queued_downloads"), [])

        self.max_jobs = max_jobs
        self.nsfw_allowed = nsfw
        self.share_images = share_images
        self.job_config = job_config
        self.current_open_tab = current_open_tab
        self.prefered_format = prefered_format

    def write(self):
        d = {
            "api_state": self.api_state,
            "max_jobs": self.max_jobs,
            "nsfw_allowed": self.nsfw_allowed,
            "current_images": self.current_images,
            "queued_downloads": self.queued_downloads,
            "job_config": self.job_config,
            "share_images": self.share_images,
            "current_open_tab": self.current_open_tab,
            "prefered_format": self.prefered_format,
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
        self.current_images = j.get("current_images", [])
        self.queued_downloads = j.get("queued_downloads", [])
        self.nsfw_allowed = j.get("nsfw_allowed", False)
        self.share_images = j.get("share_images", True)
        self.job_config = j.get("job_config", {})
        self.current_open_tab = j.get("current_open_tab", 0)
        self.prefered_format = j.get("prefered_format", "webp")


class MainWindow(QMainWindow):

    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        LOGGER.debug("Main Window init start")
        self.savedData = SavedData()
        self.savedData.read()
        LOGGER.debug("Saved data loaded")
        self.clipboard = app.clipboard()
        self.model_dict: Dict[str, Model] = {}
        self.setGeometry(100, 100, 1200, 1200)
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)
        LOGGER.debug("UI setup")
        self.restore_job_config(self.savedData.job_config)
        if (k := keyring.get_password("HordeQT", "HordeQTUser")) is not None:
            self.ui.apiKeyEntry.setText(k)
            self.api_key = k
            LOGGER.debug("API key loaded from keyring")
        else:
            self.api_key = ANON_API_KEY
            self.show_warn_toast(
                "Anonymous API key",
                "Warning: No API key set. Large generations may fail, and images will take a long time to generate",
            )
            LOGGER.debug("API key not loaded, using anon key")
        self.loading_thread = LoadThread(self.api_key)
        self.hide_api_key()
        LOGGER.debug("Showing main window")
        self.show()
        LOGGER.debug("Setting saved values on UI")
        self.ui.maxJobsSpinBox.setValue(self.savedData.max_jobs)
        self.ui.NSFWCheckBox.setChecked(self.savedData.nsfw_allowed)
        self.ui.shareImagesCheckBox.setChecked(self.savedData.share_images)
        self.ui.tabWidget.setCurrentIndex(self.savedData.current_open_tab)
        self.ui.saveFormatComboBox.setCurrentText(self.savedData.prefered_format)
        LOGGER.debug("Initializing API thread")
        self.api_thread = APIManagerThread.deserialize(
            self.savedData.api_state,
            api_key=self.api_key,
            max_requests=self.savedData.max_jobs,
        )
        LOGGER.debug("Disabling Generate button until models are loaded")
        self.ui.GenerateButton.setEnabled(False)
        self.ui.modelComboBox.setEnabled(False)

        self.download_thread: DownloadThread = DownloadThread.deserialize(
            {
                "completed_downloads": self.savedData.current_images,
                "queued_downloads": self.savedData.queued_downloads,
            }
        )
        LOGGER.debug("Connecting DL signals")
        self.download_thread.completed.connect(self.on_image_fully_downloaded)
        LOGGER.debug("Connecting API signals")
        self.api_thread.job_completed.connect(self.on_job_completed)
        self.api_thread.updated.connect(self.update_inprogess_table)
        LOGGER.debug("Connecting Loading signals")
        self.loading_thread.progress.connect(self.update_progress)
        self.loading_thread.model_info.connect(self.construct_model_dict)
        self.loading_thread.user_info.connect(self.update_user_info)
        LOGGER.debug("Connecting UI signals")
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
        self.ui.presetComboBox.currentTextChanged.connect(self.on_preset_change)
        self.ui.widthSpinBox.valueChanged.connect(self.on_width_change)
        self.ui.heightSpinBox.valueChanged.connect(self.on_height_change)
        self.ui.resetSettingsButton.clicked.connect(self.reset_job_config)
        self.ui.undoResetButton.clicked.connect(self.undo_reset_job_config)
        self.ui.undoResetButton.setEnabled(False)
        self.ui.progressBar.setValue(0)

        self.preset_being_updated = False
        self.last_job_config: Optional[Dict] = None
        self.job_history:List[Dict]=[]
        LOGGER.debug("Initializing Masonry/Gallery layout")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.ui.galleryViewFrame.setSizePolicy(sizePolicy)
        container_layout = QVBoxLayout(self.ui.galleryViewFrame)
        scroll_area = QScrollArea()

        scroll_area.setSizePolicy(sizePolicy)
        scroll_area.setWidgetResizable(True)
        self.gallery_container = ImageGalleryWidget()
        for lj in self.download_thread.completed_downloads:
            lj.update_path()
            LOGGER.info(f"Image found, adding to gallery: {lj.id}")
            self.add_image_to_gallery(lj)
            # May need to update scroll_area when jobs are added?
        scroll_area.setWidget(self.gallery_container)
        container_layout.addWidget(scroll_area)
        self.ui.galleryViewFrame.setLayout(container_layout)
        #

        LOGGER.debug("Setting up toasts")
        Toast.setAlwaysOnMainScreen(True)
        Toast.setPosition(toast_enums.ToastPosition.TOP_RIGHT)
        Toast.setPositionRelativeToWidget(self)
        LOGGER.debug("Starting threads")
        QTimer.singleShot(0, self.loading_thread.start)
        QTimer.singleShot(0, self.download_thread.start)
        QTimer.singleShot(0, self.api_thread.start)

    def closeEvent(self, event):
        LOGGER.debug("Close clicked.")

        self.api_thread.stop()

        LOGGER.debug("Stopping DL thread")
        self.download_thread.stop()
        LOGGER.debug("DL thread stopped")
        LOGGER.debug("Updating saved data")
        self.savedData.update(
            self.api_thread,
            self.ui.NSFWCheckBox.isChecked(),
            self.ui.maxJobsSpinBox.value(),
            self.download_thread,
            self.get_job_config(),
            self.ui.shareImagesCheckBox.isChecked(),
            self.ui.tabWidget.currentIndex(),
            self.ui.saveFormatComboBox.currentText(),
        )
        LOGGER.debug("Writing saved data")
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
            "images": self.ui.imagesSpinBox.value(),
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

    def add_image_to_gallery(self, lj: LocalJob):
        image_widget = ImageWidget(lj)
        image_widget.imageClicked.connect(lambda v: self.show_image_popup(v, lj))
        self.gallery_container.m_layout.addWidget(image_widget)

    def show_image_popup(self, pixmap, lj):
        popup = ImagePopup(pixmap, lj, self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, popup)
        popup.show()

    def on_fully_loaded(self):
        LOGGER.info("Fully loaded")
        self.ui.GenerateButton.setEnabled(True)
        self.ui.modelComboBox.setEnabled(True)
        # this doesn't feel right, for some reason.
        self.ui.maxJobsSpinBox.setMaximum(self.ui.maxConcurrencySpinBox.value())
        LOGGER.debug("Hiding progress bar after 250 ms")
        QTimer.singleShot(250, lambda: self.ui.progressBar.hide())

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
        self.ui.imagesSpinBox.setValue(job_config.get("images", 1))

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
        LOGGER.info(f"Job {job.id} completed.")
        job.file_type = self.ui.saveFormatComboBox.currentText()
        job.update_path()
        self.download_thread.add_dl(job)

    def update_progress(self, value):
        self.ui.progressBar.setValue(value)
        if value == 100:
            self.loading_thread.quit()
            self.on_fully_loaded()

    def update_user_info(self, r: requests.Response):
        if r.status_code == 404:
            self.show_error_toast("Invalid API key", "User could not be found.")
            LOGGER.warn("User not found, API key is invalid.")
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
            LOGGER.error("Empty prompt")
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
            *To be fair*, you'd either be an idiot or know exactly what you're doing to encounter this. :shrug:
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
            LOGGER.warn(
                "Model has requirements. This is a WIP feature, and may have issues."
            )
            # Pony is the largest family of models to have this issue, but dreamshaperXL also has a specific configuration.
            if reqs.get("clip_skip", None) == 2:
                if clip_skip == 1:
                    self.show_warn_toast(
                        "CLIP Skip Requirement", "This model requires CLIP Skip = 2"
                    )
                    self.ui.clipSkipSpinBox.setValue(2)
                    return None
            if (mins := reqs.get("min_steps", 0)) != 0:
                if steps < int(mins):
                    self.show_warn_toast(
                        "Min Steps",
                        f"This model requires at least {mins} steps, currently {steps}",
                    )
                    self.ui.stepsSpinBox.setValue(int(mins))
                    return None

            if (maxs := reqs.get("max_steps", 150)) != 150:
                if steps > int(maxs):
                    self.show_warn_toast(
                        "Max Steps",
                        f"This model requires at most {maxs} steps, currently {steps}",
                    )
                    self.ui.stepsSpinBox.setValue(int(maxs))
                    return None
            if (cfgreq := reqs.get("cfg_scale", None)) is not None:
                if cfg_scale != cfgreq:
                    self.show_warn_toast(
                        "Min Steps",
                        f"This model requires a CFG value of {cfgreq}, currently {cfg_scale}",
                    )
                    self.ui.guidenceDoubleSpinBox.setValue(float(cfgreq))
                    return None

            if (rsamplers := reqs.get("samplers", [])) != []:  # type: ignore
                if type(rsamplers) == type(str):
                    rsamplers = [rsamplers]
                if type(rsamplers) != type(int):
                    rsamplers: list[str] = rsamplers
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
                        self.ui.samplerComboBox.setCurrentText(rsamplers[0])
                        return None
        karras = True
        hires_fix = True
        allow_nsfw = self.ui.NSFWCheckBox.isChecked()
        share_image = self.ui.shareImagesCheckBox.isChecked()
        prompts = prompt_matrix(prompt)
        prompts *= self.ui.imagesSpinBox.value()
        jobs = []
        for nprompt in prompts:
            # if the user hasn't provided a seed, pick one. It must be under 2**31 so that we can display it on a spinbox eventually.
            # something something C++.
            if seed == 0:
                sj_seed = random.randint(0, 2**31 - 1)
            else:
                sj_seed = seed
            job = Job(
                prompt=nprompt,
                sampler_name=sampler_name,
                cfg_scale=cfg_scale,
                seed=str(sj_seed),
                width=width,
                height=height,
                clip_skip=clip_skip,
                steps=steps,
                model=model,
                karras=karras,
                hires_fix=hires_fix,
                allow_nsfw=allow_nsfw,
                share_image=share_image,
            )
            jobs.append(job)
        LOGGER.info(f"Created {len(jobs)} jobs")
        return jobs

    def construct_model_dict(self, mod):
        self.ui.modelComboBox.clear()

        # mod = sd_mod_ref
        models: List[Model] = self.get_available_models()
        models.sort(key=lambda k: k.get("count"), reverse=True)
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
        # print(json.dumps(curr_model.details))
        self.show_warn_toast(
            "Model info not yet implemented", "Model details is curently not working"
        )
        ModelPopup(curr_model.details)

    def on_generate_click(self):
        self.job_history.append(self.get_job_config())
        jobs = self.create_jobs()
        if jobs is not None:
            for n in range(len(jobs)):
                self.api_thread.add_job(jobs[n])
                LOGGER.debug(f"Added job {jobs[n].job_id}")
            self.show_success_toast("Created!", "Jobs were created and put into queue")

    def save_api_key(self):
        self.hide_api_key()
        self.api_key = self.ui.apiKeyEntry.text()
        keyring.set_password("HordeQT", "HordeQTUser", self.api_key)
        self.show_success_toast("Saved", "API Key saved sucessfully.")
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

    def update_row(
        self, row, id: str, status: str, prompt: str, model: str, eta: float
    ):
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
                    else (
                        "Unknown"
                        if eta == -2
                        else hr.time_delta(
                            dt.datetime.now() + dt.timedelta(seconds=eta)
                        )
                        + (" ago" if eta < 0 else "")
                    )
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

        def find_or_insert_row(job_id):
            r = table.findItems(job_id, Qt.MatchFlag.MatchFixedString)
            if not r:
                if table.columnCount() == 0:
                    table.setColumnCount(5)
                row = table.rowCount()
                table.insertRow(row)
            else:
                row = r[0].row()
            return row

        def update_table_with_jobs(jobs, status):
            for job_id, job in jobs.items():
                row = find_or_insert_row(job_id)
                self.update_row(
                    row,
                    job_id,
                    status,
                    job.prompt,
                    job.model,
                    float(job.wait_time) if status == "In Progress" else -2,
                )

        update_table_with_jobs(
            {job.job_id: job for job in self.api_thread.job_queue.queue}, "Queued"
        )
        update_table_with_jobs(self.api_thread.current_requests, "In Progress")

        for lj in self.download_thread.completed_downloads:
            row = find_or_insert_row(lj.id)
            self.update_row(
                row,
                lj.id,
                "Done",
                lj.original.prompt,
                lj.original.model,
                lj.completed_at - time.time(),
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
    LOGGER.debug(f"Saved data path: {SAVED_DATA_PATH}")
    LOGGER.debug(f"Saved data dir: {SAVED_DATA_DIR_PATH}")
    LOGGER.debug(f"Saved images dir: {SAVED_IMAGE_DIR_PATH}")

    os.makedirs(SAVED_IMAGE_DIR_PATH, exist_ok=True)
    os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)

    widget = MainWindow(app)
    widget.show()
    sys.exit(app.exec())
