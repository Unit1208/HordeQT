import copy
import json
import time
from queue import Queue
from typing import Dict, List, Optional

import requests
from PySide6.QtCore import QThread, Signal

from hordeqt.classes import Job, LocalJob
from hordeqt.consts import BASE_URL, LOGGER
from hordeqt.util import SAVED_IMAGE_DIR_PATH, get_headers


class JobManagerThread(QThread):
    job_completed = Signal(LocalJob)  # Signal emitted when a job is completed
    updated = Signal()
    kudos_cost_updated = Signal(type(Optional[float]))
    request_kudo_cost_update=Signal(Job)
    job_count=1
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
        self.request_kudo_cost_update.connect(self.get_kudos_cost)

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

    def log_error(self, job: Job, response: requests.Response):
        valid_error: dict = response.json()
        rc = valid_error.get("rc")
        message = valid_error.get("message")
        errors = ", ".join(valid_error.get("errors", {}).keys())
        LOGGER.error(f'Job {job.job_id} failed validation: "{rc}" {message}. {errors}')

    def get_kudos_cost(self, job: Job):
        LOGGER.info(f"Getting kudos cost for job {str(job)}")
        while (
            not (time.time() - self.generate_rl_reset) > 0
            and self.generate_rl_remaining > 0
        ):
            time.sleep(0.25)
        try:
            c = copy.deepcopy(job)
            c.dry_run = True
            d = json.dumps(c.to_json())
            LOGGER.info(f"Requesting kudos count for {job.job_id}")

            response = requests.post(
                BASE_URL + "generate/async",
                data=d,
                headers=get_headers(self.api_key),
            )
            if response.status_code == 429:
                self.generate_rl_reset = time.time() + 5
                return
            if response.status_code == 400:
                self.log_error(job, response)
                self.kudos_cost_updated.emit(None)

                return
            response.raise_for_status()
            kudos_value: float = float(response.json().get("kudos"))
            LOGGER.info(f"{job.job_id} would cost {kudos_value} Kudos")
            self.kudos_cost_updated.emit(kudos_value)
            self.generate_rl_reset = float(
                response.headers.get("x-ratelimit-reset") or time.time() + 2
            )
            self.generate_rl_remaining = int(
                response.headers.get("x-ratelimit-remaining") or 1
            )
        except requests.RequestException as e:
            LOGGER.error(e)
            # Nested try: except feels like bad practice.
            try:
                self.log_error(job, response)  # type: ignore
            except NameError:
                pass
            except json.JSONDecodeError:
                pass
            self.kudos_cost_updated.emit(None)
        current_time = time.time()
        if current_time - self.generate_rl_reset > 0:
            self.generate_rl_remaining = 2

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
                    if response.status_code == 400:
                        self.log_error(job, response)
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
                    # Nested try: except feels like bad practice.
                    try:
                        self.log_error(job, response)  # type: ignore
                    except NameError:
                        pass
                    except json.JSONDecodeError:
                        pass
                    self.errored_jobs.append(job)
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

                lj = LocalJob(job, SAVED_IMAGE_DIR_PATH)
                try:
                    r = requests.get(BASE_URL + f"generate/status/{job.horde_job_id}")
                    if r.status_code == 429:
                        njobs.append(job)
                        self.status_rl_reset = time.time() + 10
                        continue
                    r.raise_for_status()
                    rj = r.json()
                    if len(rj["generations"])>0:
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
                    else:
                        self.log_error(lj.original,r)
                        #Is this a good idea?
                        # self.job_queue.put(lj.original)
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
