import hashlib
import importlib.metadata
import sys
import uuid
from typing import Tuple

from hordeqt.civit.civit_api import BaseModel
from hordeqt.classes.Model import Model
from hordeqt.other.consts import CACHE_PATH
from hordeqt.VERSION import APPVERSION


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


def size_presets(index: int, needs_1024: bool) -> Tuple[int, int]:
    match index:
        case 0:
            pass
        case 1:
            # LANDSCAPE (16:9)
            return (1024, 576)
        case 2:
            # LANDSCAPE (3:2)
            if needs_1024:
                return (1024, 504)
            else:
                return (768, 512)
        case 3:
            # PORTRAIT (2:3)
            if needs_1024:
                return (704, 1024)
            else:
                return (512, 768)
        case 4:
            # PHONE BACKGROUND (9:21)
            return (448, 1024)
        case 5:
            # ULTRAWIDE (21:9)
            return (1024, 448)
        case 6:
            # SQUARE (1:1)
            if needs_1024:
                return (1024, 1024)
            else:
                return (512, 512)
    return (1024, 1024)


def get_headers(api_key: str, include_api_key: bool = True):
    t = {
        "Client-Agent": f"HordeQt:{APPVERSION}:Unit1208",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    if include_api_key:
        t["apikey"] = api_key
    return t
