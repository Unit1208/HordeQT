import gzip
import os
from typing import Dict, List

import jsonpickle

from hordeqt.classes.Style import Style
from hordeqt.other.consts import ISDEBUG, SAVED_DATA_DIR_PATH, SAVED_DATA_PATH
from hordeqt.threads.etc_download_thread import DownloadThread
from hordeqt.threads.job_download_thread import JobDownloadThread
from hordeqt.threads.job_manager_thread import JobManagerThread


class SavedData:
    api_state: Dict
    download_state: Dict
    current_open_tab: int
    current_images: List[Dict]
    finished_jobs: List[Dict]
    job_config: Dict
    max_jobs: int
    nsfw_allowed: bool
    share_images: bool
    prefered_format: str
    warned_models: List[str]
    show_done_images: bool
    notify_after_n: int
    user_saved_styles: List[Dict]

    def __init__(self) -> None:
        os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)

    def update(
        self,
        api: JobManagerThread,
        nsfw: bool,
        max_jobs: int,
        save_metadata: bool,
        dlthread: JobDownloadThread,
        downloads: DownloadThread,
        job_config: dict,
        share_images: bool,
        current_open_tab: int,
        prefered_format: str,
        warned_models: List[str],
        show_done_images: bool,
        notify_after_n: int,
        user_saved_styles: List[Style],
    ):
        self.api_state = api.serialize()
        self.current_images = (dlv := dlthread.serialize()).get(
            ("completed_downloads"), []
        )
        self.queued_downloads = dlv.get(("queued_downloads"), [])
        self.download_state = downloads.serialize()
        self.max_jobs = max_jobs
        self.nsfw_allowed = nsfw
        self.share_images = share_images
        self.save_metadata = save_metadata
        self.job_config = job_config
        self.current_open_tab = current_open_tab
        self.prefered_format = prefered_format
        self.warned_models = warned_models
        self.show_done_images = show_done_images
        self.notify_after_n = notify_after_n
        self.user_saved_styles = [uss.serialize() for uss in user_saved_styles]

    def write(self):
        d = {
            "api_state": self.api_state,
            "max_jobs": self.max_jobs,
            "nsfw_allowed": self.nsfw_allowed,
            "save_metadata": self.save_metadata,
            "current_images": self.current_images,
            "queued_downloads": self.queued_downloads,
            "job_config": self.job_config,
            "share_images": self.share_images,
            "current_open_tab": self.current_open_tab,
            "prefered_format": self.prefered_format,
            "warned_models": self.warned_models,
            "download_state": self.download_state,
            "show_done_images": self.show_done_images,
            "notify_after_n": self.notify_after_n,
            "user_saved_styles": self.user_saved_styles,
        }
        jsondata: str = jsonpickle.encode(d)  # type: ignore
        with gzip.open(SAVED_DATA_PATH.with_suffix(".json.gz"), "wt") as f:
            f.write(jsondata)
        if ISDEBUG:
            with open(SAVED_DATA_PATH.with_suffix(".readable.json"), "wt") as f:
                f.write(jsonpickle.encode(d, indent=4) or "")

    def read(self):
        if SAVED_DATA_PATH.with_suffix(".json.gz").exists():
            with gzip.open(SAVED_DATA_PATH.with_suffix(".json.gz"), "rt") as f:
                j: dict = jsonpickle.decode(f.read())  # type: ignore
        elif SAVED_DATA_PATH.exists():
            with open(SAVED_DATA_PATH, "rt") as f:
                j: dict = jsonpickle.decode(f.read())  # type: ignore
            SAVED_DATA_PATH.rename(
                SAVED_DATA_PATH.with_name("old_" + SAVED_DATA_PATH.name)
            )
        else:
            j = dict()
        self.api_state = j.get("api_state", {})
        self.max_jobs = j.get("max_jobs", 5)
        self.save_metadata = j.get("save_metadata", True)
        self.current_images = j.get("current_images", [])
        self.queued_downloads = j.get("queued_downloads", [])
        self.nsfw_allowed = j.get("nsfw_allowed", False)
        self.share_images = j.get("share_images", True)
        self.job_config = j.get("job_config", {})
        self.current_open_tab = j.get("current_open_tab", 0)
        self.prefered_format = j.get("prefered_format", "webp")
        self.warned_models = j.get("warned_models", [])
        self.download_state = j.get("download_state", {})
        self.show_done_images = j.get("show_done_images", True)
        self.notify_after_n = j.get("notify_after_n", 10)
        self.user_saved_styles = j.get("user_saved_styles", [])
