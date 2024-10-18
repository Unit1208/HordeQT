from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Self


@dataclass
class StyleLora:
    name: str
    is_version: Optional[bool]
    strength: Optional[float]
    clip_strength: Optional[float]

    @staticmethod
    def parse_from_json(v: dict):
        return StyleLora(
            name=v["name"],
            is_version=v.get("is_version", False),
            strength=v.get("model", 1),
            clip_strength=v.get("clip", 1),
        )

    def serialize(self):
        return {
            "name": self.name,
            "is_version": self.is_version,
            "strength": self.strength,
            "clip_strength": self.clip_strength,
        }

    @classmethod
    def deserialize(cls, val: Dict[str, Any]) -> Self:
        return cls(
            name=val.get("name", ""),
            is_version=val.get("is_version"),
            strength=val.get("strength"),
            clip_strength=val.get("clip_strength"),
        )


@dataclass
class Style:
    name: str
    prompt_format: str
    model: str

    width: Optional[int]
    height: Optional[int]
    cfg_scale: Optional[float]
    karras: Optional[bool]
    sampler: Optional[str]
    steps: Optional[int]
    clip_skip: Optional[int]
    hires_fix: Optional[bool]
    loras: Optional[List[StyleLora]]
    is_built_in: bool

    def serialize(self) -> Dict:
        return {
            "name": self.name,
            "prompt_format": self.prompt_format,
            "model": self.model,
            "width": self.width,
            "height": self.height,
            "cfg_scale": self.cfg_scale,
            "karras": self.karras,
            "sampler": self.sampler,
            "steps": self.steps,
            "clip_skip": self.clip_skip,
            "hires_fix": self.hires_fix,
            "loras": [lora.serialize() for lora in (self.loras or [])],
        }

    @classmethod
    def deserialize(cls, val: dict) -> Self:
        return cls(
            name=val.get("name", None),
            prompt_format=val.get("prompt_format", None),
            model=val.get("model", None),
            width=val.get("width", None),
            height=val.get("height", None),
            cfg_scale=val.get("cfg_scale", None),
            karras=val.get("karras", None),
            sampler=val.get("sampler", None),
            steps=val.get("steps", None),
            clip_skip=val.get("clip_skip", None),
            hires_fix=val.get("hires_fix", None),
            loras=[StyleLora.deserialize(lora) for lora in val.get("loras", [])],
            is_built_in=False,
        )

    @classmethod
    def parse_from_json(cls, name: str, v: dict, is_built_in: bool) -> Self:
        return cls(
            name=name,
            prompt_format=v["prompt"],
            model=v["model"],
            is_built_in=is_built_in,
            width=v.get("width", None),
            height=v.get("height", None),
            cfg_scale=v.get("cfg_scale", None),
            karras=v.get("karras", None),
            sampler=v.get("sampler_name", None),
            steps=v.get("steps", None),
            clip_skip=v.get("clip_skip", None),
            hires_fix=v.get("hires_fix", None),
            loras=[StyleLora.parse_from_json(x) for x in v.get("loras", [])],
        )
