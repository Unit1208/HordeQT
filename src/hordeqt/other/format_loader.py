from enum import IntEnum, auto
import json
import re
from typing import Optional

from PIL import Image
from PIL.ExifTags import Base

from hordeqt.classes.Job import Job
from hordeqt.classes.LocalJob import LocalJob


def _artbot(img: Image.Image):

    lines = str(img.info.get("Comment", "")).strip().splitlines()
    print(lines)

    prompt = lines[0].strip()
    param_line = 1
    if len(lines) == 2:
        negative_prompt = ""
    else:
        negative_prompt = lines[1].replace("Negative Prompt:", "").strip()
        param_line = 2
    parameters = {}
    for item in lines[param_line].split(","):
        key, value = item.split(":")
        parameters[key.strip()] = value.strip()

    output_dict = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "sampler_name": parameters["Sampler"],
        "cfg_scale": float(parameters["CFG scale"]),
        "seed": int(parameters["Seed"]),
        "width": int(parameters["Size"].split("x")[0]),
        "height": int(parameters["Size"].split("x")[1]),
        "clip_skip": 2 if "pony" in parameters["model"].lower() else 1,
        "steps": int(parameters["Steps"]),
        "model": parameters["model"].strip(),
    }
    return output_dict


def _hordeng(img: Image.Image):
    e = img.getexif()
    desc = e.get(Base.ImageDescription.value, None)
    if desc is not None:
        try:
            j: dict = json.loads(desc)
            return {
                "prompt": j.get("prompt", ""),
                "negative_prompt": j.get("negative_prompt", ""),
                "sampler_name": j.get("sampler", "k_euler"),
                "cfg_scale": j.get("cfgScale", 5),
                "seed": int(j.get("seed", 0)),
                "model": j.get("model"),
                "steps": j.get("steps", 20),
                "width": j.get("width", 1024),
                "height": j.get("height", 1024),
                "karras": j.get("karras", True),
                "hires_fix": j.get("highresFix", False),
            }

        except json.JSONDecodeError:
            # Canary
            raise ValueError("Invalid HordeNG jpeg")
        except KeyError:
            raise ValueError("Invalid HordeNG jpg")


def _from_nai_prompt(prompt: str):
    def process_weight(segment: str, multiplier=1.0):
        result = []
        i = 0
        while i < len(segment):
            if segment[i] == "{":
                count = 1
                j = i + 1
                while j < len(segment) and count > 0:
                    if segment[j] == "{":
                        count += 1
                    elif segment[j] == "}":
                        count -= 1
                    j += 1
                inner_segment = segment[i + 1 : j - 1]
                result.append(process_weight(inner_segment, multiplier * 1.05))
                i = j
            elif segment[i] == "[":
                count = 1
                j = i + 1
                while j < len(segment) and count > 0:
                    if segment[j] == "[":
                        count += 1
                    elif segment[j] == "]":
                        count -= 1
                    j += 1
                inner_segment = segment[i + 1 : j - 1]
                result.append(process_weight(inner_segment, multiplier / 1.05))
                i = j
            else:
                j = i
                while j < len(segment) and segment[j] not in "{}[]":
                    j += 1
                item = segment[i:j].strip().replace(" ", "_")
                if item:
                    if multiplier != 1.0:
                        result.append(f"({item}:{multiplier:.2f})")
                    else:
                        result.append(item)
                i = j
        return " ".join(result)

    cleaned_description = re.sub(r"\s*,\s*", ",", prompt)
    return process_weight(cleaned_description)


def _nai_png(img: Image.Image):

    line = str(img.info.get("Comment", "")).strip()
    j: dict = json.loads(line)
    return {
        "prompt": _from_nai_prompt(j.get("prompt", "")),
        "negative_prompt": _from_nai_prompt(j.get("uc", "")),
        "sampler_name": j.get("sampler", "k_euler"),
        "cfg_scale": j.get("scale", 5),
        "steps": j.get("steps", 20),
        "width": j.get("width", 1024),
        "height": j.get("height", 1024),
    }


def _hordeqt_image(img: Image.Image):
    exif = img.getexif()
    d = json.loads(exif[Base.ImageDescription])["job"]
    k = d.get("prompt").split("###")
    params = d.get("params", {})
    prompt = "Error while formatting prompt"
    neg_prompt = "No negative prompt"
    if len(k) == 2:
        prompt = k[0]
        neg_prompt = k[1]
    else:
        prompt = k[0]
        neg_prompt = False
    return {
        "prompt": prompt,
        "negative_prompt": f"{neg_prompt}\n" if neg_prompt else "\n",
        "sampler_name": params.get("sampler_name", "k_euler"),
        "cfg_scale": params.get("cfg_scale", 5),
        "seed": int(params.get("seed", 0)),
        "model": d.get("Model")[0],
        "clip_skip": int(params.get("clip_skip", 1)),
        "steps": params.get("steps", 20),
        "width": params.get("width", 1024),
        "height": params.get("height", 1024),
        "karras": params.get("karras", True),
        "hires_fix": params.get("hires_fix", False),
    }


class ImageType(IntEnum):
    HORDENG_JPG = auto()
    ARTBOT = auto()
    NAI_PNG = auto()
    HORDEQT = auto()


def detect_format(img: Image.Image):
    e = img.getexif()
    desc = e.get(Base.ImageDescription.value, None)
    if desc is not None:
        try:
            json.loads(desc)
            return ImageType.HORDENG_JPG
        except:
            pass
    sw = e[Base.Software]
    if "hordeqt" in sw:
        return ImageType.HORDEQT
    i = img.info
    if (sw := i.get("Software", None)) is not None:
        if "artbot" in str(sw).lower():
            return ImageType.ARTBOT
    if (comm := i.get("Comment", None)) is not None:
        try:
            json.loads(comm)
            return ImageType.NAI_PNG
        except:
            pass


def get_data(img: Image.Image):
    img_format = detect_format(img)
    match img_format:
        case ImageType.HORDENG_JPG:
            return _hordeng(img)
        case ImageType.ARTBOT:
            return _artbot(img)
        case ImageType.NAI_PNG:
            return _nai_png(img)
        case ImageType.HORDEQT:
            return _hordeqt_image(img)


def get_job_config(img: Image.Image) -> Optional[dict]:
    d = get_data(img)
    if d is not None:
        return {
            "prompt": d.get("prompt"),
            "negative_prompt": d.get("negative_prompt", ""),
            "sampler_name": d.get("sampler_name", "k_euler"),
            "cfg_scale": d.get("cfg_scale", 5),
            "seed": int(d.get("seed", 0)),
            "width": d.get("width", 1024),
            "height": d.get("height", 1024),
            "clip_skip": d.get("clip_skip", 1),
            "steps": d.get("steps", 20),
            "model": d.get("Model"),
            "images": 1,
            "hires_fix": d.get("hires_fix", True),
            "karras": d.get("karras", True),
            "upscale": "None",
        }
    return None
