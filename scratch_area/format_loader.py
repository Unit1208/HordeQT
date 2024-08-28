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
            "model": "AlbedoBase (SDXL)",
        }
"""

import enum
import json
from PIL import Image
from PIL.ExifTags import Base


# from PIL import
### WILL WORK:
# ARTBOT pngs jpegs
# HORDENG jpegs
def _artbot_png(img: Image.Image):
    "Comment"
    """
    A brilliant sunflower, beautiful detailed oil painting, bright yellow sunflowers, verdant leaves, by (Vincent Van Gogh:1.4),
Steps: 20, Sampler: k_euler, CFG scale: 5, Seed: 3758616032, Size: 448x1024, model: AlbedoBase XL (SDXL)"""
    pass


def _artbot_jpeg(img: Image.Image):
    "Comment"
    """A brilliant sunflower, beautiful detailed oil painting, bright yellow sunflowers, verdant leaves, by (Vincent Van Gogh:1.4),
Steps: 20, Sampler: k_euler, CFG scale: 5, Seed: 3775856534, Size: 512x768, model: AlbedoBase XL (SDXL)"""
    pass


def _hordeng_jpeg(img: Image.Image):
    "EXIF"
    """
    {"id":"c807827b-46d6-4942-a3a9-60d3d8cd3598","worker":{"id":"121514dd-b317-47f6-8d9b-bdcb7d679a51","name":"Conczins ReGen Dreamer"},"requestId":"e8039e84-0150-4ae6-9241-13294174da24","prompt":"A beautiful oil painting of the Devil with thick messy brush strokes, motif of death, somber, the Devil waits with his firey sword, angry, souls of the damned flowing up from below, death, epic oil painting, mural","negativePrompt":"(worst quality, low quality:1.4), EasyNegative, bad anatomy, bad hands, cropped, missing fingers, missing toes, too many toes, too many fingers, missing arms, long neck, Humpbacked, deformed, disfigured, poorly drawn face, distorted face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, malformed hands, out of focus, long body, monochrome, symbol, text, logo, door frame, window frame, mirror frame","sampler":"k_dpm_fast","cfgScale":2,"denoisingStrength":0.75,"height":960,"width":576,"steps":20,"model":"AlbedoBase XL (SDXL)","karras":true,"postProcessors":[],"seed":"661455155","hiresFix":false,"faceFixerStrength":0.75,"nsfw":false,"censorNsfw":false,"slowWorkers":true,"trustedWorkers":false,"allowDowngrade":false,"clipSkip":1,"loraList":[],"styleName":null,"onlyMyWorkers":false,"amount":1,"textualInversionList":[],"qrCode":{"text":null,"positionY":null,"positionX":null,"markersPrompt":null},"transparent":false,"generator":"HordeNG (https://horde-ng.org)"}"""
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


class ImageType(enum.IntEnum):
    HORDENG_JPG = 0
    ARTBOT_PNG = 1


def _detect_format(img: Image.Image):
    e = img.getexif()
    desc = e.get(Base.ImageDescription.value, None)
    if desc is not None:
        try:
            json.loads(desc)
            return ImageType.HORDENG_JPG
        except:
            pass


def get_prompt(img: Image.Image):
    img_format = _detect_format(img)
    match img_format:
        case ImageType.HORDENG_JPG:
            return _hordeng_jpeg(img)
        case ImageType.ARTBOT_PNG:
            return _artbot_png(img)
