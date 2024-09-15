import json
import os
from typing import Dict, List

from hordeqt.threads.download_thread import DownloadThread
from hordeqt.threads.job_manager_thread import JobManagerThread
from hordeqt.util import SAVED_DATA_DIR_PATH, SAVED_DATA_PATH


class SavedData:
    api_state: Dict
    current_open_tab: int
    current_images: List[Dict]
    finished_jobs: List[Dict]
    job_config: Dict
    max_jobs: int
    nsfw_allowed: bool
    share_images: bool
    prefered_format: str
    warned_models: List[str]

    def __init__(self) -> None:

        os.makedirs(SAVED_DATA_DIR_PATH, exist_ok=True)

    def update(
        self,
        api: JobManagerThread,
        nsfw: bool,
        max_jobs: int,
        save_metadata: bool,
        dlthread: DownloadThread,
        job_config: dict,
        share_images: bool,
        current_open_tab: int,
        prefered_format: str,
        warned_models: list[str],
    ):
        self.api_state = api.serialize()
        self.current_images = (dlv := dlthread.serialize()).get(
            ("completed_downloads"), []
        )
        self.queued_downloads = dlv.get(("queued_downloads"), [])

        self.max_jobs = max_jobs
        self.nsfw_allowed = nsfw
        self.share_images = share_images
        self.save_metadata = save_metadata
        self.job_config = job_config
        self.current_open_tab = current_open_tab
        self.prefered_format = prefered_format
        self.warned_models = warned_models

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
        }
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
        self.save_metadata = j.get("save_metadata", True)
        self.current_images = j.get("current_images", [])
        self.queued_downloads = j.get("queued_downloads", [])
        self.nsfw_allowed = j.get("nsfw_allowed", False)
        self.share_images = j.get("share_images", True)
        self.job_config = j.get("job_config", {})
        self.current_open_tab = j.get("current_open_tab", 0)
        self.prefered_format = j.get("prefered_format", "webp")
        self.warned_models=j.get("warned_models",[])
