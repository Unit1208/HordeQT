"""
{
            "prompt": "Foo"
            "negative_prompt": "Bar",
            "sampler_name": "k_euler",
            "cfg_scale": 5.0,
            "seed": 3735928559,
            "width": 1024,
            "height": 1024,
            "clip_skip": 1,
            "steps": 20,
            "model": "AlbedoBase XL (SDXL)",
        }
"""

import enum
import json
import re
from PIL import Image
from PIL.ExifTags import Base


# from PIL import
### WILL WORK:
# ARTBOT pngs jpegs
# HORDENG jpegs
def _artbot(img: Image.Image):

    lines = img.info.get("Comment").strip().splitlines()
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


def _hordeng_jpeg(img: Image.Image):
    e = img.getexif()
    desc = e.get(Base.ImageDescription.value, None)
    if desc is not None:
        try:
            j: dict = json.loads(desc)
            return {
                "prompt": j.get("prompt"),
                "negative_prompt": j.get("negative_prompt"),
                "sampler_name": j.get("sampler"),
                "cfg_scale": j.get("cfgScale"),
                "seed": j.get("seed"),
                "model": j.get("model"),
                "steps": j.get("steps"),
                "width": j.get("width"),
                "height": j.get("height"),
            }
        except json.JSONDecodeError:
            raise ValueError("Invalid hordeNG jpeg")
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

    line = img.info.get("Comment").strip()
    j: dict = json.loads(line)
    return {
        "prompt": _from_nai_prompt(j.get("prompt")),
        "negative_prompt": _from_nai_prompt(j.get("uc")),
        "sampler_name": j.get("sampler"),
        "cfg_scale": j.get("scale"),
        "seed": 0,
        "model": "AMPonyXL",
        "clip_skip": 2,
        "steps": j.get("steps"),
        "width": j.get("width"),
        "height": j.get("height"),
    }


class ImageType(enum.IntEnum):
    HORDENG_JPG = 0
    ARTBOT = 1
    NAI_PNG = 2


def _detect_format(img: Image.Image):
    e = img.getexif()
    desc = e.get(Base.ImageDescription.value, None)
    if desc is not None:
        try:
            json.loads(desc)
            return ImageType.HORDENG_JPG
        except:
            pass
    i = img.info
    if (sw := i.get("Software", None)) is not None:
        if "ArtBot" in sw:
            return ImageType.ARTBOT

    if (comm := i.get("Comment", None)) is not None:
        try:
            json.loads(comm)
            return ImageType.NAI_PNG
        except:
            pass


def get_prompt(img: Image.Image):
    img_format = _detect_format(img)
    match img_format:
        case ImageType.HORDENG_JPG:
            return _hordeng_jpeg(img)
        case ImageType.ARTBOT:
            return _artbot(img)
        case ImageType.NAI_PNG:
            return _nai_png(img)
