import copy
import json
import time
from queue import PriorityQueue, Queue
from typing import Dict, List, Optional, Tuple

import requests
from PySide6.QtCore import QMutex, QThread, QWaitCondition, Signal

from hordeqt.classes.Job import Job
from hordeqt.classes.LocalJob import LocalJob
from hordeqt.other.consts import BASE_URL, LOGGER
from hordeqt.other.util import get_headers


class JobManagerThread(QThread):
    job_completed = Signal(LocalJob)  # Signal emitted when a job is completed
    job_errored = Signal(dict)
    job_info = Signal(dict)

    updated = Signal()
    kudos_cost_updated = Signal(type(Optional[float]))
    request_kudo_cost_update = Signal(Job)
    job_count = 1

    def __init__(self, api_key: str, max_requests: int, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.max_requests = max_requests
        self.current_requests: PriorityQueue[Tuple[int, str, Job]] = PriorityQueue(
            max_requests
        )
        self.job_queue: Queue[Job] = Queue()
        self.status_rl_reset = time.time()
        self.generate_rl_reset = time.time()
        self.completed_jobs: List[Job] = []
        self.running = True  # To control the thread's loop
        self.generate_rl_remaining = 1
        self.async_reset_time = time.time()
        self.status_rl_remaining = 1
        self.status_reset_time = time.time()

        self.wait_condition = QWaitCondition()  # Condition variable
        self.mutex = QMutex()  # Mutex for synchronization

        self.errored_jobs: List[Job] = []
        self.request_kudo_cost_update.connect(self.get_kudos_cost)

    def run(self):
        LOGGER.debug("API thread started")
        while self.running:
            # Acquire the mutex to check for stop conditions
            self.mutex.lock()
            if not self.running:
                self.mutex.unlock()
                break

            self.handle_queue()
            self.updated.emit()

            self.wait_condition.wait(self.mutex, 1000)
            self.mutex.unlock()

    def serialize(self):
        return {
            "current_requests": [
                (k[0], k[1], k[2].serialize()) for k in self.current_requests.queue
            ],
            "job_queue": [_.serialize() for _ in list(self.job_queue.queue)],
            "completed_jobs": [_.serialize() for _ in self.completed_jobs],
            "errored_jobs": [_.serialize() for _ in self.errored_jobs],
        }

    def log_error(self, job: Job, response: requests.Response):
        valid_error: dict = response.json()
        rc = valid_error.get("rc")
        message = valid_error.get("message")
        errors = ", ".join(valid_error.get("errors", {}).items())
        LOGGER.error(f'Job {job.job_id} failed validation: "{rc}" {message}. {errors}')

    def get_kudos_cost(self, job: Job):
        while (
            not (time.time() - self.generate_rl_reset) > 0
            and self.generate_rl_remaining > 0
        ):
            time.sleep(0.25)
        try:
            c = copy.deepcopy(job)
            c.dry_run = True
            c.prompt = "KUDOS!"  # Prevent empty prompt from interfering
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

        instance.current_requests = PriorityQueue(max_requests)
        for item in data.get("current_requests", []):
            instance.current_requests.put((item[0], item[1], Job.deserialize(item[2])))

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
        if (not self.current_requests.full()) and not self.job_queue.empty():
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
                    response_json = response.json()
                    horde_job_id = response_json.get("id")
                    job.horde_job_id = horde_job_id
                    self.current_requests.put((0, job.horde_job_id, job))
                    LOGGER.info(
                        f"Job {job.job_id} now has horde uuid: " + job.horde_job_id
                    )
                    self.generate_rl_reset = float(
                        response.headers.get("x-ratelimit-reset") or time.time() + 2
                    )
                    self.generate_rl_remaining = int(
                        response.headers.get("x-ratelimit-remaining") or 1
                    )
                    self.updated.emit()

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
        if not self.current_requests.empty():
            _, job_id, job = self.current_requests.get()

            if time.time() - job.creation_time > 600:
                LOGGER.warning(
                    f'Job "{job_id}" was created more than 10 minutes ago, likely errored'
                )
            try:
                LOGGER.debug(f"Checking job {job_id} - ({job.horde_job_id})")
                response = requests.get(BASE_URL + f"generate/check/{job.horde_job_id}")
                response.raise_for_status()
                job.update_status(response.json())
                if job.done:
                    LOGGER.info(f"Job {job_id} done")
                    self.completed_jobs.append(job)
                elif job.faulted:
                    LOGGER.error(f"Job {job_id} Errored")
                    self.errored_jobs.append(job)
                else:
                    self.current_requests.put((round(job.wait_time or 0), job_id, job))
                    self.updated.emit()

            except requests.RequestException as e:
                LOGGER.error(e)

    def _get_download_paths(self):
        njobs = []
        for job in self.completed_jobs:
            if (
                time.time() - self.status_rl_reset
            ) > 0 and self.status_rl_remaining > 0:
                lj = LocalJob(job)
                try:
                    r = requests.get(BASE_URL + f"generate/status/{job.horde_job_id}")
                    if r.status_code == 429:
                        njobs.append(job)
                        self.status_rl_reset = time.time() + 10
                        continue
                    r.raise_for_status()
                    rj = r.json()
                    if len(rj["generations"]) > 0:
                        self.status_reset_time = float(
                            r.headers.get("x-ratelimit-reset") or time.time() + 60
                        )
                        self.status_rl_remaining = int(
                            r.headers.get("x-ratelimit-remaining") or 1
                        )
                        rj["job_id"] = job.job_id
                        rj["prompt"] = job.prompt
                        gen = rj["generations"][0]
                        if gen["censored"] or rj["faulted"]:
                            self.job_errored.emit(rj)
                        else:
                            if len("gen_metadata") > 0:
                                self.job_info.emit(rj)
                            lj.downloadURL = gen["img"]
                            lj.worker_id = gen["worker_id"]
                            lj.worker_name = gen["worker_name"]
                            lj.completed_at = time.time()
                            self.job_completed.emit(lj)
                        self.updated.emit()

                    else:
                        self.log_error(lj.original, r)

                except requests.RequestException as e:
                    LOGGER.error(e)
                self.status_rl_reset = time.time()
                if time.time() - self.status_reset_time > 0:
                    self.status_rl_remaining = 1
                    self.status_reset_time = time.time()
            else:
                njobs.append(job)
        self.completed_jobs = njobs

    def get_queued_jobs(self) -> List[Job]:
        return list(self.job_queue.queue)

    def get_completed_jobs(self) -> List[Job]:
        return self.completed_jobs

    def stop(self):
        LOGGER.debug("Stopping API thread")
        self.mutex.lock()
        self.running = False
        self.wait_condition.wakeAll()  # Wake the thread immediately to exit
        self.mutex.unlock()
        LOGGER.debug("API thread stopped.")

    def add_job(self, job: Job):
        self.job_queue.put(job)
