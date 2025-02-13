import datetime as dt
import json
import os
import shutil
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import human_readable as hr
import keyring
import requests
from pyqttoast import Toast, ToastPreset, toast_enums
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QSystemTrayIcon,
    QTableWidgetItem,
    QVBoxLayout,
)

from hordeqt.classes.Job import Job
from hordeqt.classes.LocalJob import LocalJob
from hordeqt.classes.Model import Model
from hordeqt.classes.SavedData import SavedData
from hordeqt.classes.Style import Style
from hordeqt.classes.StyleLibrary import StyleLibrary
from hordeqt.components.gallery.image_gallery_widget import ImageGalleryWidget
from hordeqt.components.gallery.image_popup import ImagePopup
from hordeqt.components.gallery.image_widget import ImageWidget
from hordeqt.components.localstats.local_stats import LocalStats
from hordeqt.components.loras.lora_browser import LoraBrowser
from hordeqt.components.loras.lora_item import LoRAItem
from hordeqt.components.loras.selected_loras import SelectedLoRAs
from hordeqt.components.model_dialog import ModelPopup
from hordeqt.components.style_library.selected_styles import SelectedStyles
from hordeqt.components.style_library.style_browser import StyleBrowser
from hordeqt.components.style_library.style_item import StyleItem
from hordeqt.gen.res_resources import qCleanupResources, qInitResources
from hordeqt.gen.ui_form import Ui_MainWindow
from hordeqt.other.consts import (
    ANON_API_KEY,
    APP,
    BASE_URL,
    CACHE_PATH,
    LOGGER,
    SAVED_DATA_DIR_PATH,
    SAVED_IMAGE_DIR_PATH,
)
from hordeqt.other.job_util import get_horde_metadata_pretty
from hordeqt.other.prompt_util import create_jobs
from hordeqt.other.rescan import rescan_jobs
from hordeqt.other.util import get_time_str, size_presets
from hordeqt.threads.connection_thread import (
    CheckConnectionThread,
    OnlineStatus,
    oc_to_description,
)
from hordeqt.threads.etc_download_thread import DownloadThread
from hordeqt.threads.job_download_thread import JobDownloadThread
from hordeqt.threads.job_manager_thread import JobManagerThread
from hordeqt.threads.load_thread import LoadThread
from hordeqt.threads.save_thread import SaveThread


class HordeQt(QMainWindow):
    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        LOGGER.debug("Main Window init start")
        self.fullyloaded = False
        self.savedData = SavedData()
        self.savedData.read()
        LOGGER.debug("Saved data loaded")
        self.clipboard = app.clipboard()
        self.model_dict: Dict[str, Model] = {}
        self.user_styles: List[Style] = [
            Style.deserialize(s) for s in self.savedData.user_saved_styles
        ]
        self.setGeometry(100, 100, 1200, 1200)
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)
        LOGGER.debug("UI setup")
        self.selectedLoRAs = SelectedLoRAs(self)
        self.ui.LoraVBox.addWidget(self.selectedLoRAs)
        self.selectedStyles = SelectedStyles(self)
        self.ui.StyleVBox.addWidget(self.selectedStyles)
        self.restore_job_config(self.savedData.job_config)
        if (
            k := keyring.get_password("HordeQT", "HordeQTUser")
        ) is not None and k.strip() != "":
            self.ui.apiKeyEntry.setText(k.strip())
            self.api_key = k.strip()
            LOGGER.debug("API key loaded from keyring")
        else:
            self.api_key = ANON_API_KEY
            LOGGER.debug("API key not loaded, using anon key")
        if self.api_key == ANON_API_KEY:
            self.show_warn_toast(
                "Anonymous API key",
                "Warning: No API key set. Large generations may fail, and images will take a long time to generate",
            )

        self.loading_thread = LoadThread(self.api_key)
        self.hide_api_key()
        LOGGER.debug("Updating generate frame")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.ui.frame.setSizePolicy(sizePolicy)
        self.ui.scrollArea.setSizePolicy(sizePolicy)
        self.ui.scrollArea.setWidgetResizable(True)
        LOGGER.debug("Showing main window")
        self.show()
        LOGGER.debug("Loading resources")
        qInitResources()
        LOGGER.debug("Updating resources")
        self.ui.tabWidget.setTabIcon(6, QIcon(":/icons/IconSmall.png"))  # "About" Tab
        LOGGER.debug("Opening system tray for notifications")
        self.systemTray = QSystemTrayIcon(QIcon(":/icons/IconSmaller.png"))
        self.systemTray.show()
        LOGGER.debug("Setting saved values on UI")

        if (
            not self.systemTray.isSystemTrayAvailable()
            or not self.systemTray.supportsMessages()
        ):

            self.ui.notifyAfterNFinishedSpinBox.setEnabled(False)

        else:
            self.ui.notifyAfterNFinishedSpinBox.setValue(self.savedData.notify_after_n)

        self.ui.maxJobsSpinBox.setValue(self.savedData.max_jobs)
        self.ui.NSFWCheckBox.setChecked(self.savedData.nsfw_allowed)
        self.ui.shareImagesCheckBox.setChecked(self.savedData.share_images)
        self.ui.saveMetadataCheckBox.setChecked(self.savedData.save_metadata)
        self.ui.tabWidget.setCurrentIndex(self.savedData.current_open_tab)
        self.ui.saveFormatComboBox.setCurrentText(self.savedData.prefered_format)
        self.ui.showDoneImagesCheckbox.setChecked(self.savedData.show_done_images)
        self.warned_models = self.savedData.warned_models
        LOGGER.debug("Initializing API thread")
        self.api_thread = JobManagerThread.deserialize(
            self.savedData.api_state,
            api_key=self.api_key,
            max_requests=self.savedData.max_jobs,
        )
        LOGGER.debug("Disabling buttons until fully loaded")
        self.ui.GenerateButton.setEnabled(False)
        self.ui.modelComboBox.setEnabled(False)
        self.ui.StyleSelector.setEnabled(False)

        self.job_download_thread: JobDownloadThread = JobDownloadThread.deserialize(
            {
                "completed_downloads": self.savedData.current_images,
                "queued_downloads": self.savedData.queued_downloads,
            },
        )
        self.job_download_thread.completed_downloads = rescan_jobs(
            self.job_download_thread.completed_downloads
        )
        self.save_thread = SaveThread(self)
        self.download_thread: DownloadThread = DownloadThread.deserialize(
            self.savedData.download_state
        )
        self.connection_thread = CheckConnectionThread()
        self.last_online_status: Optional[OnlineStatus] = None
        self.online = False
        LOGGER.debug("Connecting online status signal")
        self.connection_thread.onlineUpdate.connect(self.on_connection_status_update)

        LOGGER.debug("Connecting DL signals")
        self.job_download_thread.completed.connect(self.on_image_fully_downloaded)
        self.job_download_thread.use_metadata = self.savedData.save_metadata
        LOGGER.debug("Connecting API signals")
        self.api_thread.job_completed.connect(self.on_job_completed)
        self.api_thread.job_errored.connect(self.on_job_errored)
        self.api_thread.job_info.connect(self.on_job_info)
        self.api_thread.updated.connect(self.update_inprogess_table)
        self.api_thread.kudos_cost_updated.connect(self.on_kudo_cost_get)
        LOGGER.debug("Connecting Loading signals")
        self.loading_thread.progress.connect(self.update_progress)
        self.loading_thread.model_info.connect(self.construct_model_dict)
        self.loading_thread.style_info.connect(self.construct_style_info)
        self.loading_thread.style_preview.connect(self.construct_style_preview)
        self.loading_thread.user_info.connect(self.update_user_info)
        self.loading_thread.horde_info.connect(self.update_horde_info)
        LOGGER.debug("Connecting UI signals")
        self.ui.GenerateButton.clicked.connect(self.on_generate_click)
        self.ui.modelDetailsButton.clicked.connect(self.on_model_open_click)
        self.ui.saveMetadataCheckBox.checkStateChanged.connect(
            self.update_metadata_save
        )
        self.ui.LoRASelector.clicked.connect(lambda: LoraBrowser(self))

        self.ui.apiKeyEntry.editingFinished.connect(self.save_api_key)
        self.ui.saveAPIkey.clicked.connect(self.save_api_key)
        self.ui.copyAPIkey.clicked.connect(self.copy_api_key)
        self.ui.showAPIKey.clicked.connect(self.toggle_api_key_visibility)

        self.ui.openSavedData.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(SAVED_DATA_DIR_PATH))
        )
        self.ui.openSavedImages.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(SAVED_IMAGE_DIR_PATH))
        )
        self.ui.clearCacheButton.clicked.connect(self.clear_cache)
        self.ui.presetComboBox.currentTextChanged.connect(self.on_preset_change)
        self.ui.widthSpinBox.valueChanged.connect(self.on_width_change)
        self.ui.heightSpinBox.valueChanged.connect(self.on_height_change)
        self.ui.resetSettingsButton.clicked.connect(self.reset_job_config)
        self.ui.undoResetButton.clicked.connect(self.undo_reset_job_config)
        self.ui.undoResetButton.setEnabled(False)
        self.ui.samplerComboBox.currentTextChanged.connect(self.update_kudos_preview)
        self.ui.stepsSpinBox.valueChanged.connect(self.update_kudos_preview)
        self.ui.guidenceDoubleSpinBox.valueChanged.connect(self.update_kudos_preview)
        self.ui.imagesSpinBox.valueChanged.connect(self.update_images_created)
        self.ui.karrasCheckBox.checkStateChanged.connect(self.update_kudos_preview)
        self.ui.highResFixCheckBox.checkStateChanged.connect(self.update_kudos_preview)

        localStatsLayout = QVBoxLayout()
        localStatsLayout.addWidget(LocalStats(self))
        self.ui.LocalStats_tab.setLayout(localStatsLayout)
        self.ui.progressBar.setValue(0)
        self.preset_being_updated = False
        self.last_job_config: Optional[Dict] = None
        self.job_history: List[Dict] = []
        self.current_kudos_preview_cost = 10.0
        self.jobs_in_progress = 0
        LOGGER.debug("Initializing Masonry/Gallery layout")
        self.ui.galleryViewFrame.setSizePolicy(sizePolicy)
        container_layout = QVBoxLayout(self.ui.galleryViewFrame)
        scroll_area = QScrollArea()

        scroll_area.setSizePolicy(sizePolicy)
        scroll_area.setWidgetResizable(True)
        self.gallery_container = ImageGalleryWidget()
        existing_ids: List[str] = []
        filtered_jobs: List[LocalJob] = []
        for lj in self.job_download_thread.completed_downloads:
            if lj.id in existing_ids:
                LOGGER.debug(f"Found duplicate for {lj.id}")
            else:
                lj.update_path()
                v = self.add_image_to_gallery(lj)
                if not v:
                    LOGGER.warning(f"Image {lj.path} is invalid, not adding to gallery")
                else:
                    LOGGER.trace(f"Image found, added to gallery: {lj.id}")
                    filtered_jobs.append(lj)
                    existing_ids.append(lj.id)
        self.job_download_thread.completed_downloads = filtered_jobs
        # May need to update scroll_area when jobs are added?
        scroll_area.setWidget(self.gallery_container)
        container_layout.addWidget(scroll_area)
        self.ui.galleryViewFrame.setLayout(container_layout)

        LOGGER.debug("Setting up toasts")
        Toast.setAlwaysOnMainScreen(True)
        Toast.setPosition(toast_enums.ToastPosition.TOP_RIGHT)
        Toast.setPositionRelativeToWidget(self)
        LOGGER.debug("Starting threads")
        self.loading_thread.start()
        self.job_download_thread.start()
        self.download_thread.start()
        self.api_thread.start()
        self.connection_thread.start()

    def closeEvent(self, event):
        LOGGER.debug("Close clicked.")

        LOGGER.debug("Stopping threads")
        self.save_thread.stop()
        self.api_thread.stop()
        self.job_download_thread.stop()
        self.download_thread.stop()
        self.connection_thread.stop()
        LOGGER.debug("Threads stopped")
        if not self.fullyloaded:
            qCleanupResources()
            QMainWindow.closeEvent(self, event)
            return
        LOGGER.debug("Updating saved data")
        self.savedData.update(
            self.api_thread,
            self.ui.NSFWCheckBox.isChecked(),
            self.ui.maxJobsSpinBox.value(),
            self.ui.saveMetadataCheckBox.isChecked(),
            self.job_download_thread,
            self.download_thread,
            self.save_job_config(),
            self.ui.shareImagesCheckBox.isChecked(),
            self.ui.tabWidget.currentIndex(),
            self.ui.saveFormatComboBox.currentText(),
            self.warned_models,
            self.ui.showDoneImagesCheckbox.isChecked(),
            self.ui.notifyAfterNFinishedSpinBox.value(),
            self.styleLibrary.get_user_styles(),
        )
        LOGGER.debug("Writing saved data")
        self.savedData.write()
        LOGGER.debug("Unloading resources")
        qCleanupResources()
        LOGGER.debug("Closing Main window")
        QMainWindow.closeEvent(self, event)

    def on_connection_status_update(self, value: OnlineStatus):
        self.online = value.online
        if self.last_online_status is None:
            self.last_online_status = value
        else:
            LOGGER.debug(
                "Horde is "
                + ("online" if value.online else "offline")
                + " @ "
                + get_time_str()
            )
            if self.last_online_status.online == value.online:
                pass
            else:
                if value.online:
                    self.show_info_toast(
                        "Reconnected",
                        f'HordeQT has reconnected to AI Horde servers after reason: "{oc_to_description(self.last_online_status.offline_comp)}"',
                    )

                else:
                    self.show_error_toast(
                        "Disconnected",
                        f'HordeQT has disconnected from AI Horde servers. Reason: "{oc_to_description(value.offline_comp)}"',
                    )
                self.set_paused_requests(not self.online)
        self.last_online_status = value

    def set_paused_requests(self, value: bool):
        self.api_thread.pause_requests = value
        self.job_download_thread.pause_downloads = value
        self.download_thread.pause_downloads = value

    def update_metadata_save(self):
        self.job_download_thread.use_metadata = self.ui.saveMetadataCheckBox.isChecked()

    def update_kudos_preview(self):
        self.ui.GenerateButton.setText("Generate (Cost: Loading)")
        jobs = self.get_job_data(True)
        if jobs is not None:
            # FIXME: for now, this will work. However, if multi-config is added (i.e. request with multiple step counts), this might undershoot or overshoot.
            self.api_thread.job_count = len(jobs)
            self.api_thread.kudos_cost_queue.put(jobs[0])

    def on_kudo_cost_get(self, value: float):
        LOGGER.debug(
            f"Got signal that kudos cost would be {value}. Multiplying by {self.api_thread.job_count} for total kudos cost of {value*self.api_thread.job_count}"
        )

        self.ui.GenerateButton.setText(
            f := f"Generate (Cost: {round(value)*self.api_thread.job_count} Kudos)"
        )

        LOGGER.debug(f"Tried to update generate button text to {f}")

        self.current_kudos_preview_cost = value

    def update_images_created(self, value: int):
        self.api_thread.job_count = value
        self.on_kudo_cost_get(self.current_kudos_preview_cost)

    def on_width_change(self):
        if not self.preset_being_updated:
            self.ui.presetComboBox.setCurrentIndex(0)
        self.update_kudos_preview()

    def on_height_change(self):
        if not self.preset_being_updated:
            self.ui.presetComboBox.setCurrentIndex(0)
        self.update_kudos_preview()

    def on_preset_change(self):
        current_model = self.ui.modelComboBox.currentText()
        current_model_needs_1024 = self.model_dict[current_model].details.get(
            "baseline", None
        ) in [
            "stable_diffusion_xl",
            "stable_cascade",
            "flux_1",
        ]
        self.preset_being_updated = True
        new_width, new_height = size_presets(
            self.ui.presetComboBox.currentIndex(), current_model_needs_1024
        )
        self.ui.widthSpinBox.setValue(new_width)
        self.ui.heightSpinBox.setValue(new_height)
        self.preset_being_updated = False

    def on_image_fully_downloaded(self, lj: LocalJob):
        self.add_image_to_gallery(lj)
        QTimer.singleShot(1000, self.check_for_notifications)

    def check_for_notifications(self):
        # this seems like it could be an oppurtuniy for a race condition, but it's probably not a huge deal.
        # Also, this construction is... not the cleanest or clearest, but it's also probably fine.
        conditions = [
            len(self.job_download_thread.queued_downloads),
            self.api_thread.job_queue.qsize(),
            self.api_thread.current_requests.qsize(),
        ]
        preconditions_satisfied = all([condition == 0 for condition in conditions])
        if preconditions_satisfied:
            if self.jobs_in_progress > 0:
                self.systemTray.showMessage(
                    "Images done",
                    f"All {self.jobs_in_progress} finished processing",
                    msecs=5000,
                )
            self.show_success_toast("Images done", "All images finished processing")
            self.jobs_in_progress = 0
        else:
            LOGGER.debug(
                f"{len(self.job_download_thread.queued_downloads)=} {self.api_thread.job_queue.qsize()=} {self.api_thread.current_requests.qsize()=}"
            )

    def add_image_to_gallery(self, lj: LocalJob):
        image_widget = ImageWidget(lj)
        if image_widget.valid:
            image_widget.imageClicked.connect(lambda v: self.show_image_popup(v, lj))
            self.gallery_container.m_layout.addWidget(image_widget)
        return image_widget.valid

    def show_image_popup(self, pixmap, lj):
        popup = ImagePopup(pixmap, lj, self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, popup)
        popup.show()

    def delete_image(self, lj: LocalJob):
        lj.update_path()
        if not lj.path.exists():
            self.show_warn_toast(
                "Deleting image failed",
                "Image path couldn't be found, can't delete image.",
            )
        self.gallery_container.m_layout.delete_image(lj.id)
        self.gallery_container.m_layout.updateGeometry()
        self.job_download_thread.delete_image(lj)

    def on_fully_loaded(self):
        LOGGER.info("Fully loaded")
        self.ui.GenerateButton.setEnabled(True)
        self.ui.modelComboBox.setEnabled(True)
        # this doesn't feel right, for some reason.
        self.ui.maxJobsSpinBox.setMaximum(self.ui.maxConcurrencySpinBox.value())
        LOGGER.debug("Loading kudos preview after 200 ms")
        QTimer.singleShot(200, self.update_kudos_preview)
        LOGGER.debug("Hiding progress bar after 500 ms")
        QTimer.singleShot(500, self.ui.progressBar.hide)
        LOGGER.debug("Starting save thread after 750 ms")
        QTimer.singleShot(750, self.save_thread.start)
        self.fullyloaded = True

    def save_job_config(self):
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
            "hires_fix": self.ui.highResFixCheckBox.isChecked(),
            "karras": self.ui.karrasCheckBox.isChecked(),
            "upscale": self.ui.upscaleComboBox.currentText(),
            "loras": [lora.serialize() for lora in self.selectedLoRAs.loras],
            "styles": [
                style.style_data.serialize() for style in self.selectedStyles.styles
            ],
        }

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
        self.ui.imagesSpinBox.setValue(job_config.get("images", 1))
        self.ui.highResFixCheckBox.setChecked(job_config.get("hires_fix", True))
        self.ui.karrasCheckBox.setChecked(job_config.get("karras", True))
        self.ui.upscaleComboBox.setCurrentText(job_config.get("upscale", "None"))
        ser_loras = job_config.get("loras", [])
        loras = [LoRAItem.deserialize(lora, self.selectedLoRAs) for lora in ser_loras]
        for lora in self.selectedLoRAs.loras:
            lora.remove_lora()
        for lora in loras:
            self.selectedLoRAs.add_lora_widget(lora.loraModel, lora.loraVersion)
        ser_styles = job_config.get("styles", [])
        styles = [
            StyleItem.deserialize(style, self.selectedStyles) for style in ser_styles
        ]
        for style in self.selectedStyles.styles:
            style.remove_style()
        for style in styles:
            self.selectedStyles.add_style_widget(style.style_data)

    def undo_reset_job_config(self):
        if self.last_job_config is not None:
            self.restore_job_config(self.last_job_config)

    def reset_job_config(self):
        self.last_job_config = self.save_job_config()
        self.ui.undoResetButton.setEnabled(True)
        # Restore the job config, using the defaults for everything. Model needs to be set after, as the default is "default"
        self.restore_job_config({})
        self.ui.modelComboBox.setCurrentIndex(0)
        self.update_kudos_preview()

    def on_job_errored(self, val: Dict[str, Any]):
        self.show_error_toast("Job Errored", get_horde_metadata_pretty(val))

    def on_job_info(self, val: Dict[str, Any]):
        self.show_warn_toast("Job Warning", get_horde_metadata_pretty(val))

    def on_job_completed(self, job: LocalJob):
        LOGGER.info(f"Job {job.id} completed.")
        job.file_type = self.ui.saveFormatComboBox.currentText()
        job.update_path()
        self.job_download_thread.add_dl(job)

    def update_progress(self, value):
        self.ui.progressBar.setValue(value)
        if value == 100:
            self.loading_thread.quit()
            self.on_fully_loaded()

    def update_user_info(self, r: requests.Response):
        if r.status_code == 404:
            self.show_error_toast("Invalid API key", "User could not be found.")
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
        self.ui.accountAgeLineEdit.setText(str(j["account_age"]))
        self.ui.accountCreatedLineEdit.setText(
            hr.date_time(
                (
                    dt.datetime.fromtimestamp(time.time())
                    - dt.timedelta(seconds=j["account_age"])
                )
            )
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

    def update_horde_info(
        self, horde_info_tuple: Tuple[requests.Response, requests.Response]
    ):
        (image_totals_response, performance_response) = horde_info_tuple

        if image_totals_response.status_code != 200:
            self.show_error_toast(
                "Horde API Error",
                "The AI Horde API didn't respond correctly, something is likely extremely broken",
            )
            return
        image_totals_dict = image_totals_response.json()
        if performance_response.status_code != 200:
            # Subtly different, to make it easier to tell which endpoint is misbehaving.
            self.show_error_toast(
                "Horde API Error",
                "The AI Horde API didn't respond correctly, something is probably extremely broken",
            )
            return
        performance_dict = performance_response.json()
        self.horde_info = {"stats": image_totals_dict, "perf": performance_dict}
        self.ui.lastMinuteImagesLineEdit.setText(
            str(image_totals_dict["minute"]["images"])
        )
        self.ui.lastHourImagesLineEdit.setText(str(image_totals_dict["hour"]["images"]))
        self.ui.lastDayImagesLineEdit.setText(str(image_totals_dict["day"]["images"]))
        self.ui.lastMonthImagesLineEdit.setText(
            str(image_totals_dict["month"]["images"])
        )
        self.ui.allTimeImagesLineEdit.setText(str(image_totals_dict["total"]["images"]))
        self.ui.pastMinuteMPSLineEdit.setText(
            str(performance_dict["past_minute_megapixelsteps"])
        )
        self.ui.queuedMPSLineEdit.setText(
            str(performance_dict["queued_megapixelsteps"])
        )
        self.ui.queuedRequestsLineEdit.setText(str(performance_dict["queued_requests"]))
        self.ui.workerCountLineEdit.setText(str(performance_dict["worker_count"]))
        self.ui.imageThreadCountLineEdit.setText(str(performance_dict["thread_count"]))

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

    def get_job_data(self, checking_cost=False) -> Optional[List[Job]]:
        p = self.ui.PromptBox.toPlainText()
        if p.strip() == "" and not checking_cost:
            self.show_error_toast("Prompt error", "Prompt cannot be empty")
            return None
        np = self.ui.NegativePromptBox.toPlainText()

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
        karras = self.ui.karrasCheckBox.isChecked()
        hires_fix = self.ui.highResFixCheckBox.isChecked()
        allow_nsfw = self.ui.NSFWCheckBox.isChecked()
        share_image = self.ui.shareImagesCheckBox.isChecked()
        upscale = self.ui.upscaleComboBox.currentText()
        loras = self.selectedLoRAs.to_LoRA_list()
        styles = self.selectedStyles.to_style_list()
        images = self.ui.imagesSpinBox.value()
        if reqs is not None:
            LOGGER.warning(
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
            # TODO: make sure this works for flux!
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
                        f"This model requires a CFG (Guidence) value of {cfgreq}, currently {cfg_scale}",
                    )
                    self.ui.guidenceDoubleSpinBox.setValue(float(cfgreq))
                    return None
            if (rsamplers := reqs.get("samplers", [])) != []:  # type: ignore
                if isinstance(rsamplers, str):
                    rsamplers = [rsamplers]
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

        return create_jobs(
            p,
            np,
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
            share_image,
            upscale,
            loras,
            styles,
            images,
        )

    def construct_style_info(self, styles: List[Style]):
        self.styleLibrary = StyleLibrary(styles=styles, parent=self)
        self.styleLibrary.add_styles(self.user_styles)
        self.ui.StyleSelector.clicked.connect(lambda: StyleBrowser(self))
        self.ui.StyleSelector.setEnabled(True)

    def construct_style_preview(self):
        with open(self.loading_thread.style_preview_cache_path, "rt") as f:
            self.styleLibrary.previews = json.load(f)

    def construct_model_dict(self, mod):
        self.ui.modelComboBox.clear()

        models: List[dict] = self.get_available_models()
        models.sort(key=lambda k: k.get("count", 0), reverse=True)
        model_dict: Dict[str, Model] = {}
        for n in models:
            name = n.get("name") or "Unknown"
            self.ui.modelComboBox.addItem(name)
            m = Model(
                n.get("performance", 0),
                n.get("queued", 0),
                n.get("jobs", 0),
                n.get("eta", 0),
                "image",
                name,
                n.get("count", 1),
                n.get("details", {}),
            )
            try:
                m.details = mod[m.name]
            except KeyError:
                if m.name not in self.warned_models:
                    self.show_warn_toast(
                        "Unknown Model",
                        f"{m.name} is not on the official model list. This may be a custom model, or may be an extremely new model.",
                    )
                    m.details = {}
                    self.warned_models.append(m.name)
                else:
                    LOGGER.warning(
                        f"Unknown model {m.name} is already known, not warning user."
                    )
            model_dict[name] = m
        self.ui.modelComboBox.setCurrentIndex(0)
        self.model_dict = model_dict

    def get_available_models(self) -> List[dict]:
        # TODO: move to separate thread
        r = requests.get(
            BASE_URL + "status/models",
            params={"type": "image", "min_count": 1, "model_state": "all"},
        )
        r.raise_for_status()
        return r.json()

    def on_model_open_click(self):
        curr_model = self.model_dict[self.ui.modelComboBox.currentText()]
        # print(json.dumps(curr_model.details))
        self.show_warn_toast(
            "Model info not yet implemented", "Model details is curently not working"
        )
        ModelPopup(curr_model.details)

    def on_generate_click(self):
        self.job_history.append(self.save_job_config())
        jobs = self.get_job_data()
        if jobs is not None:
            pre_queue_size = self.api_thread.job_queue.qsize()
            for n in range(len(jobs)):
                self.api_thread.add_job(jobs[n])
                LOGGER.debug(f"Added job {jobs[n].job_id}")
            self.show_success_toast(
                "Created!",
                str(len(jobs))
                + (" Job was" if len(jobs) == 1 else " Jobs were")
                + " created and put into queue",
            )
            if (
                (pre_queue_size + len(jobs))
                >= self.ui.notifyAfterNFinishedSpinBox.value()
                and self.ui.notifyAfterNFinishedSpinBox.isEnabled()
                and self.ui.notifyAfterNFinishedSpinBox.value() > 0
            ):

                self.jobs_in_progress += len(jobs)
            if not self.online:
                self.show_warn_toast(
                    "Jobs were created offline",
                    f"HordeQT is not online. {len(jobs)} were queued.",
                )

    def save_api_key(self):
        self.hide_api_key()
        self.api_key = self.ui.apiKeyEntry.text()
        keyring.set_password("HordeQT", "HordeQTUser", self.api_key)
        self.show_success_toast("Saved", "API Key saved sucessfully.")
        self.loading_thread.reload_user_info(self.api_key)

    def copy_api_key(self):
        # Is this confusing to the user? Would they expect the copy to copy what's currently in the api key, or the last saved value?
        self.clipboard.setText(self.api_key)

    def show_toast(
        self, title: str, message: str, preset_type: str, log_level=None, duration=5000
    ):
        toast = Toast(self)
        toast.setDuration(duration)
        toast.setTitle(title)
        toast.setText(message)

        # Determine the correct preset based on style hints and toast type
        preset_map = {
            "success": (ToastPreset.SUCCESS, ToastPreset.SUCCESS_DARK),
            "info": (ToastPreset.INFORMATION, ToastPreset.INFORMATION_DARK),
            "error": (ToastPreset.ERROR, ToastPreset.ERROR_DARK),
            "warning": (ToastPreset.WARNING, ToastPreset.WARNING_DARK),
        }
        light_preset, dark_preset = preset_map.get(preset_type.lower(), (None, None))
        if light_preset is None or dark_preset is None:
            LOGGER.debug("Invalid preset id.")
        else:
            toast.applyPreset(
                light_preset
                if APP.styleHints() == Qt.ColorScheme.Light
                else dark_preset
            )

            toast.show()

        # Log message if log level is specified
        if log_level:
            log_func = getattr(LOGGER, log_level)
            log_func(f"{title}: {message}")

    def show_success_toast(self, title: str, message: str, duration=5000):
        self.show_toast(
            title, message, "success", log_level="success", duration=duration
        )

    def show_info_toast(self, title: str, message: str, duration=5000):
        self.show_toast(title, message, "info", log_level="info", duration=duration)

    def show_error_toast(self, title: str, message: str, duration=5000):
        self.show_toast(title, message, "error", log_level="error", duration=duration)

    def show_warn_toast(self, title: str, message: str, duration=5000):
        self.show_toast(
            title, message, "warning", log_level="warning", duration=duration
        )

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
                prompt,
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
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        table.resizeColumnsToContents()
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

        def update_table_with_jobs(jobs: Dict[str, Job], status: str):
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
        update_table_with_jobs(
            {job.job_id: job for job in self.api_thread.errored_jobs}, "Errored"
        )
        update_table_with_jobs(
            {job_id: job for _, job_id, job in self.api_thread.current_requests.queue},
            "In Progress",
        )

        show_done_images = self.ui.showDoneImagesCheckbox.isChecked()

        # Clear the table if necessary
        if not show_done_images:
            # Optionally remove all "Done" rows if we don't want to show them
            for row in range(table.rowCount() - 1, -1, -1):  # Traverse in reverse
                status_item = table.item(row, 1)
                if status_item and status_item.text() == "Done":
                    table.removeRow(row)

        for lj in self.job_download_thread.completed_downloads:
            if show_done_images:
                row = find_or_insert_row(lj.id)
                self.update_row(
                    row,
                    lj.id,
                    "Done",
                    lj.original.prompt,
                    lj.original.model,
                    lj.completed_at - time.time(),
                )

    def clear_cache(self):
        if CACHE_PATH.exists():
            try:
                pre_size = shutil.disk_usage(CACHE_PATH.parent)
                shutil.rmtree(CACHE_PATH)
                post_size = shutil.disk_usage(CACHE_PATH.parent)
                diff = post_size.free - pre_size.free

                self.show_success_toast(
                    "Cache cleared",
                    f"Cache was cleared successfully. {hr.file_size(diff)} Freed",
                )
            except Exception as e:
                self.show_error_toast(
                    "Cache not cleared",
                    f'While clearing cache, HordeQT ran into an issue: "{e}"',
                )

        else:
            self.show_info_toast(
                "Cache not cleared",
                "Cache directory does not exist (i.e. no cache to clear)",
            )


def main():
    LOGGER.debug(f"Running on {threading.current_thread().native_id}")
    os.makedirs(SAVED_IMAGE_DIR_PATH, exist_ok=True)
    os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)

    widget = HordeQt(APP)
    widget.show()
    sys.exit(APP.exec())
