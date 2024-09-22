import json
import time
from typing import Dict, Optional, Self

from hordeqt.other.consts import UPSCALE_MAP
from hordeqt.other.util import create_uuid


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
        upscale: Optional[str] = None,
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
        self.dry_run = False
        self.upscale = upscale
        self.job_id = create_uuid()
        self.horde_job_id = horde_job_id
        self.wait_time = wait_time
        self.queue_position = queue_position
        self.done = done
        self.faulted = faulted
        self.kudos = kudos
        self.creation_time = time.time()
        self.mod_time = time.time()

    def to_job_config(self):
        pandnp = self.prompt.split("###")
        if len(pandnp) == 1:
            prompt = pandnp[0]
            neg_prompt = ""
        else:
            prompt = pandnp[0]
            neg_prompt = pandnp[1]
        return {
            "prompt": prompt,
            "negative_prompt": neg_prompt,
            "sampler_name": self.sampler_name,
            "cfg_scale": self.cfg_scale,
            "seed": int(self.seed),
            "width": self.width,
            "height": self.height,
            "clip_skip": self.clip_skip,
            "steps": self.steps,
            "model": self.model,
            "images": 1,
            "hires_fix": self.hires_fix,
            "karras": self.karras,
            "upscale": self.upscale or "None",
        }

    def to_json(self) -> Dict:
        return {
            "prompt": self.prompt,
            "params": {
                "sampler_name": self.sampler_name,
                "cfg_scale": self.cfg_scale,
                "seed": str(self.seed),
                "height": self.height,
                "width": self.width,
                "post_processing": (
                    [] if (k := UPSCALE_MAP[self.upscale]) == None else [k]
                ),
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
            "dry_run": self.dry_run,
        }

    def __str__(self) -> str:
        return json.dumps({"ser": self.serialize(), "tj": self.to_json()})

    @classmethod
    def from_json(cls, data: Dict) -> Self:
        prompt: str = data.get("prompt", "")

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
            upscale=params.get("upscaler"),
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
    def deserialize(cls: type[Self], value: Dict) -> Self:
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
