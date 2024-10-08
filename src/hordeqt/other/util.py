import hashlib
import importlib.metadata
import re
import sys
import uuid
from typing import List

from hordeqt.civit.civit_api import BaseModel
from hordeqt.classes.Model import Model
from hordeqt.other.consts import CACHE_PATH


def get_metadata():
    app_module = sys.modules["__main__"].__package__
    # Retrieve the app's metadata
    if app_module is None:
        raise Exception("Invalid package metadata")
    metadata = importlib.metadata.metadata(app_module)
    return metadata


def create_uuid():
    return str(uuid.uuid4())


def get_hash(b: bytes | str) -> str:
    if isinstance(b, bytes):
        return hashlib.sha256(b).hexdigest()
    else:
        return get_hash(str(b).encode("utf-8"))


def get_bucketized_cache_path(s: str):
    h = get_hash(s)
    pdir = h[0:2]
    cfile = h[2:]
    bdir = CACHE_PATH / "bucketized"
    npdir = bdir / pdir
    npdir.mkdir(parents=True, exist_ok=True)
    return npdir / cfile


def horde_model_to_civit_baseline(model: Model) -> BaseModel:
    bl = model.details.get("baseline")
    if bl == "stable diffusion 2":
        return BaseModel.StableDiffusion2_1
    elif bl == "stable diffusion 1":
        return BaseModel.StableDiffusion1_5
    elif bl == "stable_diffusion_xl":
        # Hack fix, but it should work.
        if "pony" in model.name.lower():
            return BaseModel.Pony
        else:
            return BaseModel.SDXL_1_0
    elif bl == "stable_cascade":
        return BaseModel.StableCascade
    else:
        return BaseModel.Other
    # current_model_needs_1024 = model_dict[
    # self.ui.modelComboBox.currentText()
    # ].details.get("baseline", None) in ["stable_diffusion_xl", "stable_cascade"]


def get_headers(api_key: str, include_api_key: bool = True):
    version = get_metadata()["Version"]
    t = {
        "Client-Agent": f"HordeQt:{version}:Unit1208",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    if include_api_key:
        t["apikey"] = api_key
    return t


def prompt_matrix(prompt: str) -> List[str]:
    matched_matrix = re.finditer(r"\{[^\{]+?\}", prompt, re.M)

    def generate_prompts(current_prompt: str, matches: List[str]) -> List[str]:
        if not matches:
            return [current_prompt]

        matched = matches[0]
        remaining_matches = matches[1:]

        # Strip brackets and split by '|'
        options = matched[1:-1].split("|")

        # Recursively generate all combinations.
        # If you hit the stack limit, that's on you, it shouldn't happen.
        generated_prompts = []
        for option in options:
            new_prompt = current_prompt.replace(matched, option, 1)
            generated_prompts.extend(generate_prompts(new_prompt, remaining_matches))

        a = []
        [
            a.extend(prompt_matrix(generated_prompt))
            for generated_prompt in generated_prompts
        ]
        a = list(set(a))
        return a

    matches = [match.group() for match in matched_matrix]

    result_prompts = generate_prompts(prompt, matches)

    # If no valid combinations were generated, return the original prompt
    return result_prompts if result_prompts else [prompt]
