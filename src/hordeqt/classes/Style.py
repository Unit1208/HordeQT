from dataclasses import dataclass
from typing import List, Optional


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

    @staticmethod
    def parse_from_json(name: str, v: dict):
        return Style(
            name=name,
            prompt_format=v["prompt"],
            model=v["model"],
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
