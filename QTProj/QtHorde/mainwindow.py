# This Python file uses the following encoding: utf-8
import enum
import json
import random
import sys
import time
from typing import List, Dict

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog,
    QMessageBox,
    QLineEdit,
)
from queue import Queue


from ui_form import Ui_MainWindow
from ui_modelinfo import Ui_Dialog

import keyring
import requests

ANON_API_KEY = "0000000000"
BASE_URL = "https://aihorde.net/api/v2/"


def get_headers(api_key: str):
    return {
        "apikey": api_key,
        "Client-Agent": "https://github.com/Unit1208/HordeQt:0.0.1:Unit1208",
    }


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
    prompt: str
    sampler_name: str
    cfg_scale: float
    seed: int
    width: int
    height: int
    karras: bool = True
    hires_fix: bool = True
    clip_skip: int
    steps: int
    model: str
    allow_nsfw: bool = False

    def __init__(
        self,
        prompt: str,
        sampler_name: str,
        cfg_scale: float,
        seed: int,
        width: int,
        height: int,
        clip_skip: int,
        steps: int,
        model: str,
        karras: bool = True,
        hires_fix: bool = True,
        allow_nsfw: bool = False,
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

    def to_json(self):
        return {
            "prompt": self.prompt,
            "params": {
                "sampler_name": self.sampler_name,
                "cfg_scale": self.cfg_scale,
                "seed": self.seed,
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

    @classmethod
    def from_json(cls, data: dict):
        prompt = data.get("prompt")
        params = data.get("params", {})
        sampler_name = params.get("sampler_name")
        cfg_scale = params.get("cfg_scale")
        seed = params.get("seed")
        width = params.get("width")
        height = params.get("height")
        karras = params.get("karras", True)
        hires_fix = params.get("hires_fix", True)
        clip_skip = params.get("clip_skip")
        steps = params.get("steps")
        model = data.get("models", ["string"])[0]
        allow_nsfw = data.get("nsfw", False)

        return cls(
            prompt=prompt,
            sampler_name=sampler_name,
            cfg_scale=cfg_scale,
            seed=seed,
            width=width,
            height=height,
            karras=karras,
            hires_fix=hires_fix,
            clip_skip=clip_skip,
            steps=steps,
            model=model,
            allow_nsfw=allow_nsfw,
        )


class JobStatus:
    wait_time: float
    queue_position: float
    done: bool
    faulted: bool
    kudos: float

    mod_time: float

    def __init__(
        self,
        wait_time: float,
        queue_position: float,
        done: bool,
        faulted: bool,
        kudos: float,
    ) -> None:
        self.done = done
        self.faulted = faulted
        self.kudos = kudos
        self.queue_position = queue_position
        self.wait_time = wait_time

        self.mod_time = time.time()

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            done=data.get("done", False),
            faulted=data.get("faulted", False),
            kudos=data.get("kudos", 0),
            queue_position=data.get("queue_position", 0),
            wait_time=data.get("wait_time", 0),
        )


class APIManager:
    max_requests = 10
    current_requests: List[str] = []
    statuses: Dict[str, JobStatus]
    completed_jobs: List[str] = []

    def __init__(self, api_key: str, max_requests: int) -> None:
        self.max_requests = max_requests
        self.api_key = api_key
        self.current_requests = []
        self.job_queue: Queue[Job] = Queue()
        self.last_request = time.time()

    def handle_queue(self):
        if (
            len(self.current_requests) <= self.max_requests
            and time.time() - self.last_request > 2
        ):
            nj = self.job_queue.get()
            res = requests.post(
                BASE_URL + "generate/async",
                json=nj.to_json(),
                headers=get_headers(self.api_key),
            )
            self.last_request = time.time()
            res.raise_for_status()

            rj = res.json()
            self.current_requests.append(rj["id"])

        new_requests = []
        for job in self.current_requests:

            res = requests.get(BASE_URL + "generate/check/" + job)
            res.raise_for_status()

            self.statuses[job] = JobStatus.from_json(res.json())
            if self.statuses[job].done:
                self.completed_jobs.append(job)
            else:
                new_requests.append(job)
        self.current_requests = new_requests

    def done_jobs(self):
        dj = self.completed_jobs.copy()
        self.completed_jobs = []
        return dj


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


class MainWindow(QMainWindow):
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_warn(self, message):
        QMessageBox.warning(self, "Warning", message)

    def show_info(self, message):

        QMessageBox.information(self, "Info", message)

    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        self.clipboard = app.clipboard()
        self.model_dict: Dict[str, Model] = {}
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)
        if (k := keyring.get_password("QTHorde", "QTHordeUser")) != None:
            self.ui.apiKeyEntry.setText(k)

        self.ui.GenerateButton.clicked.connect(self.on_generate_click)
        self.ui.modelDetailsButton.clicked.connect(self.on_model_open_click)

        self.ui.apiKeyEntry.returnPressed.connect(self.save_api_key)
        self.ui.saveAPIkey.clicked.connect(self.save_api_key)
        self.ui.copyAPIkey.clicked.connect(self.copy_api_key)
        self.ui.showAPIKey.clicked.connect(self.toggle_api_key_visibility)
        self.construct_model_dict()

    def toggle_api_key_visibility(self):
        visible = self.ui.apiKeyEntry.echoMode() == QLineEdit.EchoMode.Normal
        if visible:
            self.ui.showAPIKey.setText("Show API Key")
            self.ui.apiKeyEntry.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.ui.showAPIKey.setText("Hide API Key")
            self.ui.apiKeyEntry.setEchoMode(QLineEdit.EchoMode.Normal)

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
        model = self.ui.modelComboBox.currentText()
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

    def construct_model_dict(self):
        self.ui.modelComboBox.clear()
        r = "https://raw.githubusercontent.com/Haidra-Org/AI-Horde-image-model-reference/main/stable_diffusion.json"
        sd_mod_ref = requests.get(r)
        sd_mod_ref.raise_for_status()
        mod = sd_mod_ref.json()
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

    def get_model_details(self, available_models: List[Model] | None):
        if available_models == None:
            available_models = self.get_available_models()

    def on_model_open_click(self):
        curr_model = self.model_dict[self.ui.modelComboBox.currentText()]
        print(json.dumps(curr_model.details))
        ModelPopup(curr_model.details)

    def on_generate_click(self):
        self.show_info("Generate was clicked!")
        print(json.dumps(self.create_job().to_json()))

    def save_api_key(self):
        self.api_key = self.ui.apiKeyEntry.text()
        keyring.set_password("HordeQT", "HordeQTUser", self.api_key)
        self.show_info("API Key saved sucessfully.")

    def copy_api_key(self):
        # Is this confusing to the user? Would they expect the copy to copy what's currently in the api key, or the last saved value?
        self.clipboard.setText(self.api_key)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Horde QT")
    app.setOrganizationName("Unit1208")
    widget = MainWindow(app)
    widget.show()
    sys.exit(app.exec())
