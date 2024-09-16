import datetime as dt
import os
import random
import sys
import time
from typing import Dict, List, Optional, Tuple

import human_readable as hr
import keyring
import requests
from pyqttoast import Toast, ToastPreset, toast_enums
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QTableWidgetItem,
    QVBoxLayout,
)

from hordeqt.classes import Job, LocalJob, Model
from hordeqt.consts import ANON_API_KEY, BASE_URL, LOGGER
from hordeqt.gallery import ImageGalleryWidget, ImagePopup, ImageWidget
from hordeqt.gen.ui_form import Ui_MainWindow
from hordeqt.model_dialog import ModelPopup
from hordeqt.saved_data import SavedData
from hordeqt.threads.download_thread import DownloadThread
from hordeqt.threads.job_manager_thread import JobManagerThread
from hordeqt.threads.load_thread import LoadThread
from hordeqt.threads.save_thread import SaveThread
from hordeqt.util import get_dynamic_constants, prompt_matrix


class HordeQt(QMainWindow):

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
        LOGGER.debug("Setting saved values on UI")
        self.ui.maxJobsSpinBox.setValue(self.savedData.max_jobs)
        self.ui.NSFWCheckBox.setChecked(self.savedData.nsfw_allowed)
        self.ui.shareImagesCheckBox.setChecked(self.savedData.share_images)
        self.ui.saveMetadataCheckBox.setChecked(self.savedData.save_metadata)
        self.ui.tabWidget.setCurrentIndex(self.savedData.current_open_tab)
        self.ui.saveFormatComboBox.setCurrentText(self.savedData.prefered_format)
        self.warned_models = self.savedData.warned_models
        LOGGER.debug("Initializing API thread")
        self.api_thread = JobManagerThread.deserialize(
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
            },
        )
        self.save_thread = SaveThread(self)
        LOGGER.debug("Connecting DL signals")
        self.download_thread.completed.connect(self.on_image_fully_downloaded)
        self.download_thread.use_metadata = self.savedData.save_metadata
        LOGGER.debug("Connecting API signals")
        self.api_thread.job_completed.connect(self.on_job_completed)
        self.api_thread.updated.connect(self.update_inprogess_table)
        self.api_thread.kudos_cost_updated.connect(self.on_kudo_cost_get)
        LOGGER.debug("Connecting Loading signals")
        self.loading_thread.progress.connect(self.update_progress)
        self.loading_thread.model_info.connect(self.construct_model_dict)
        self.loading_thread.user_info.connect(self.update_user_info)
        self.loading_thread.horde_info.connect(self.update_horde_info)
        LOGGER.debug("Connecting UI signals")
        self.ui.GenerateButton.clicked.connect(self.on_generate_click)
        self.ui.modelDetailsButton.clicked.connect(self.on_model_open_click)
        self.ui.saveMetadataCheckBox.checkStateChanged.connect(
            self.update_metadata_save
        )

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
        self.ui.samplerComboBox.currentTextChanged.connect(self.update_kudos_preview)
        self.ui.stepsSpinBox.valueChanged.connect(self.update_kudos_preview)
        self.ui.guidenceDoubleSpinBox.valueChanged.connect(self.update_kudos_preview)
        self.ui.imagesSpinBox.valueChanged.connect(self.update_images_created)
        self.ui.karrasCheckBox.checkStateChanged.connect(self.update_kudos_preview)
        self.ui.highResFixCheckBox.checkStateChanged.connect(self.update_kudos_preview)
        self.ui.progressBar.setValue(0)

        self.preset_being_updated = False
        self.last_job_config: Optional[Dict] = None
        self.job_history: List[Dict] = []
        self.current_kudos_preview_cost = 10.0
        LOGGER.debug("Initializing Masonry/Gallery layout")
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

        LOGGER.debug("Setting up toasts")
        Toast.setAlwaysOnMainScreen(True)
        Toast.setPosition(toast_enums.ToastPosition.TOP_RIGHT)
        Toast.setPositionRelativeToWidget(self)
        LOGGER.debug("Starting threads")
        self.loading_thread.start()
        self.download_thread.start()
        self.api_thread.start()
        self.save_thread.start()

    def closeEvent(self, event):
        LOGGER.debug("Close clicked.")

        self.api_thread.stop()
        self.save_thread.stop()
        LOGGER.debug("Stopping DL thread")
        self.download_thread.stop()
        LOGGER.debug("DL thread stopped")
        LOGGER.debug("Updating saved data")
        self.savedData.update(
            self.api_thread,
            self.ui.NSFWCheckBox.isChecked(),
            self.ui.maxJobsSpinBox.value(),
            self.ui.saveMetadataCheckBox.isChecked(),
            self.download_thread,
            self.save_job_config(),
            self.ui.shareImagesCheckBox.isChecked(),
            self.ui.tabWidget.currentIndex(),
            self.ui.saveFormatComboBox.currentText(),
            self.warned_models,
        )
        LOGGER.debug("Writing saved data")
        self.savedData.write()
        LOGGER.debug("Closing Main window")
        QMainWindow.closeEvent(self, event)

    def update_metadata_save(self):
        self.download_thread.use_metadata = self.ui.saveMetadataCheckBox.isChecked()

    def update_kudos_preview(self):
        jobs = self.create_jobs()
        self.ui.GenerateButton.setText("Generate (Cost: Loading)")
        if jobs is not None:
            # FIXME: for now, this will work. However, if multi-config is added (i.e. request with multiple step counts), this might undershoot or overshoot.
            self.api_thread.request_kudo_cost_update.emit(jobs[0])
            self.api_thread.job_count = len(jobs)

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
        current_model_needs_1024 = self.model_dict[
            self.ui.modelComboBox.currentText()
        ].details.get("baseline", None) in ["stable_diffusion_xl", "stable_cascade"]
        # FIXME: when flux becomes official, make this less hacky.
        if "flux" in self.ui.modelComboBox.currentText().lower():
            current_model_needs_1024 = True
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
                # SQUARE (1:1)
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

    def delete_image(self, lj: LocalJob):
        lj.update_path()
        if not lj.path.exists():
            self.show_warn_toast(
                "Deleting image failed",
                "Image path couldn't be found, can't delete image.",
            )
        self.gallery_container.m_layout.delete_image(lj.id)
        self.gallery_container.m_layout.updateGeometry()
        self.download_thread.delete_image(lj)

    def on_fully_loaded(self):
        LOGGER.info("Fully loaded")
        self.ui.GenerateButton.setEnabled(True)
        self.ui.modelComboBox.setEnabled(True)
        # this doesn't feel right, for some reason.
        self.ui.maxJobsSpinBox.setMaximum(self.ui.maxConcurrencySpinBox.value())
        LOGGER.debug("Loading kudos preview after 300 ms")
        QTimer.singleShot(300, self.update_kudos_preview)
        LOGGER.debug("Hiding progress bar after 500 ms")
        QTimer.singleShot(500, self.ui.progressBar.hide)

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

    def update_horde_info(self, l: Tuple[requests.Response, requests.Response]):
        (r1, r2) = l

        if r1.status_code != 200:
            self.show_error_toast(
                "Horde API Error",
                "The AI Horde API didn't respond correctly, something is likely extremely broken",
            )
            return
        j1 = r1.json()
        if r2.status_code != 200:
            # Subtly different, to make it easier to tell which endpoint is misbehaving.
            self.show_error_toast(
                "Horde API Error",
                "The AI Horde API didn't respond correctly, something is probably extremely broken",
            )
            return
        j2 = r2.json()
        self.horde_info = {"stats": j1, "perf": j2}
        self.ui.lastMinuteImagesLineEdit.setText(str(j1["minute"]["images"]))
        self.ui.lastHourImagesLineEdit.setText(str(j1["hour"]["images"]))
        self.ui.lastDayImagesLineEdit.setText(str(j1["day"]["images"]))
        self.ui.lastMonthImagesLineEdit.setText(str(j1["month"]["images"]))
        self.ui.allTimeImagesLineEdit.setText(str(j1["total"]["images"]))
        self.ui.pastMinuteMPSLineEdit.setText(str(j2["past_minute_megapixelsteps"]))
        self.ui.queuedMPSLineEdit.setText(str(j2["queued_megapixelsteps"]))
        self.ui.queuedRequestsLineEdit.setText(str(j2["queued_requests"]))
        self.ui.workerCountLineEdit.setText(str(j2["worker_count"]))
        self.ui.imageThreadCountLineEdit.setText(str(j2["thread_count"]))

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
        karras = self.ui.karrasCheckBox.isChecked()
        hires_fix = self.ui.highResFixCheckBox.isChecked()
        allow_nsfw = self.ui.NSFWCheckBox.isChecked()
        share_image = self.ui.shareImagesCheckBox.isChecked()
        upscale = self.ui.upscaleComboBox.currentText()
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
                upscale=upscale,
            )
            jobs.append(job)
        LOGGER.info(f"Created {len(jobs)} jobs")
        return jobs

    def construct_model_dict(self, mod):
        self.ui.modelComboBox.clear()

        models: List[Model] = self.get_available_models()
        models.sort(key=lambda k: k.get("count"), reverse=True)
        model_dict: Dict[str, Model] = {}
        for n in models:
            name = n.get("name", "Unknown")
            count = n.get("count", 0)
            self.ui.modelComboBox.addItem(name)
            m = Model()
            m.count = count
            m.eta = n.get("eta", 0)
            m.jobs = n.get("jobs", 0)
            m.name = name
            m.performance = n.get("performance", 0)
            m.queued = n.get("queued", 0)
            m.type = "image"
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

    def get_available_models(self) -> List[Model]:
        # TODO: move to separate thread
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
        self.job_history.append(self.save_job_config())
        jobs = self.create_jobs()
        if jobs is not None:
            for n in range(len(jobs)):
                self.api_thread.add_job(jobs[n])
                LOGGER.debug(f"Added job {jobs[n].job_id}")
            self.show_success_toast(
                "Created!",
                str(len(jobs))
                + (" Job was" if len(jobs) == 1 else " Jobs were")
                + " created and put into queue",
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
        LOGGER.info(f"{title}: {message}")

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
        LOGGER.error(f"{title}: {message}")

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
        LOGGER.warning(f"{title}: {message}")

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
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
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


def main():
    global app, SAVED_DATA_DIR_PATH, SAVED_DATA_PATH, SAVED_IMAGE_DIR_PATH
    # I don't care.
    (app, SAVED_DATA_DIR_PATH, SAVED_DATA_PATH, SAVED_IMAGE_DIR_PATH) = (
        get_dynamic_constants()
    )

    os.makedirs(SAVED_IMAGE_DIR_PATH, exist_ok=True)
    os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)

    widget = HordeQt(app)
    widget.show()
    sys.exit(app.exec())
