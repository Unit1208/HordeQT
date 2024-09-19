import json
import time
from pathlib import Path
from typing import Self

from PIL import ExifTags, Image

from hordeqt.classes.Job import Job


class LocalJob:
    id: str
    path: Path
    original: Job
    file_type: str
    downloadURL: str
    completed_at: float
    worker_id: str
    worker_name: str
    base: Path

    def convert_to_metadata(self) -> dict:
        return {
            "Application": "HordeQT",
            "job": self.original.serialize(),
            "id": self.id,
            "worker": f"{self.worker_name} ({self.worker_id})",
        }

    def __init__(self, job: Job, base: Path, file_type: str = "webp") -> None:
        self.id = job.job_id
        self.original = job
        self.file_type = file_type
        self.base = base
        self.update_path()

    def pretty_format(self) -> str:
        _prompt = self.original.prompt
        k = _prompt.split("###")
        prompt = "Error while formatting prompt"
        neg_prompt = "No negative prompt"
        if len(k) == 2:
            prompt = k[0]
            neg_prompt = k[1]
        else:
            prompt = k[0]
            neg_prompt = False
        b = [
            f"Prompt: {prompt}",
            (
                f"Negative Prompt: {neg_prompt}"
                if neg_prompt
                else "" f"Model: {self.original.model}"
            ),
            f"Steps: {self.original.steps}",
            f"Sampler: {self.original.sampler_name}",
            f"Guidence: {self.original.cfg_scale}",
            f"CLIP Skip: {self.original.clip_skip}",
            f"Size: {self.original.width} x {self.original.height} (WxH)",
        ]
        return "\n".join(b)

    def update_path(self):

        self.path = (self.base / self.id).with_suffix("." + self.file_type)

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "original": self.original.serialize(),
            "fileType": self.file_type,
            "path": str(self.path),
            "completed_at": self.completed_at,
            "worker_id": self.worker_id,
            "worker_name": self.worker_name,
        }

    @classmethod
    def deserialize(cls, value: dict, base: Path) -> Self:
        job = value.get("original", {})
        lj = cls(Job.deserialize(job), base)
        lj.completed_at = value.get("completed_at", time.time())
        lj.worker_name = value.get("worker_name", "Unknown")
        lj.worker_id = value.get("worker_id", "00000000-0000-0000-0000-000000000000")
        lj.file_type = value.get("fileType", "webp")
        lj.update_path()
        return lj


def apply_metadata_to_image(path: Path, lj: LocalJob) -> Path:
    im = Image.open(path)

    exif = im.getexif()
    exif[ExifTags.Base.Software] = "HordeQT"
    exif[ExifTags.Base.ImageDescription] = json.dumps(lj.convert_to_metadata())
    exif[ExifTags.Base.UserComment] = lj.pretty_format()
    im.save(lj.path, exif=exif)
    return lj.path