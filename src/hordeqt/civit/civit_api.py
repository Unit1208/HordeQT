from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

from hordeqt.civit.civit_enums import *

# TRANSLATED FROM HORDENG's implementation


class ModelVersionStats:
    def __init__(self, downloadCount: int, ratingCount: int, rating: float):
        self.downloadCount = downloadCount
        self.ratingCount = ratingCount
        self.rating = rating

    @staticmethod
    def deserialize(data: dict):
        return ModelVersionStats(
            downloadCount=data.get("downloadCount", None),
            ratingCount=data.get("ratingCount", None),
            rating=data.get("rating", None),
        )

    def serialize(self):
        return {
            "downloadCount": self.downloadCount,
            "ratingCount": self.ratingCount,
            "rating": self.rating,
        }


class ModelVersionFileMetadata:
    def __init__(
        self, fp: Optional[FP], size: Optional[ModelSize], format: Optional[ModelFormat]
    ):
        self.fp = fp
        self.size = size
        self.format = format

    @staticmethod
    def deserialize(data: dict):

        return ModelVersionFileMetadata(
            fp=FP(str(data.get("fp"))) if data.get("fp", None) is not None else None,
            size=(
                ModelSize(str(data.get("size")))
                if data.get("size", None) is not None
                else None
            ),
            format=(
                ModelFormat(str(data.get("format")))
                if data.get("format", None) is not None
                else None
            ),
        )

    def serialize(self) -> dict:
        d: Dict[str, ModelFormat | ModelSize | FP] = {}
        if self.fp is not None:
            d["fp"] = self.fp
        if self.size is not None:
            d["size"] = self.size
        if self.format is not None:
            d["format"] = self.format
        return d


class ModelVersionFile:
    def __init__(
        self,
        id: int,
        sizeKb: float,
        name: str,
        type: str,
        pickleScanResult: ScanResult,
        virusScanResult: ScanResult,
        scannedAt: Optional[str],
        primary: Optional[bool],
        metadata: ModelVersionFileMetadata,
        downloadURL: str,
        hashes: Dict[str, str],
    ):
        self.id = id
        self.sizeKb = sizeKb
        self.name = name
        self.type = type
        self.pickleScanResult = pickleScanResult
        self.virusScanResult = virusScanResult
        self.scannedAt = scannedAt
        self.primary = primary
        self.metadata = metadata
        self.downloadURL = downloadURL
        self.hashes = hashes

    @staticmethod
    def deserialize(data: dict):
        return ModelVersionFile(
            id=data.get("id", -1),
            sizeKb=data.get("sizeKb", 1),
            name=data.get("name", ""),
            type=data.get("type", "Model"),
            pickleScanResult=ScanResult(data.get("pickleScanResult", None)),
            virusScanResult=ScanResult(data.get("virusScanResult", None)),
            scannedAt=data.get("scannedAt"),
            primary=data.get("primary"),
            metadata=ModelVersionFileMetadata.deserialize(data.get("metadata", {})),
            downloadURL=data.get("downloadURL", ""),
            hashes=data.get("hashes", {}),
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "sizeKb": self.sizeKb,
            "name": self.name,
            "type": self.type,
            "pickleScanResult": self.pickleScanResult,
            "virusScanResult": self.virusScanResult,
            "scannedAt": self.scannedAt,
            "primary": self.primary,
            "metadata": self.metadata.serialize(),
            "downloadURL": self.downloadURL,
            "hashes": self.hashes,
        }


class ModelVersionImage:
    def __init__(
        self,
        id: int,
        url: str,
        nsfw: bool,
        width: int,
        height: int,
        hash: str,
        type: str,
    ):
        self.id = id
        self.url = url
        self.nsfw = nsfw
        self.width = width
        self.height = height
        self.hash = hash
        self.type = type

    @staticmethod
    def deserialize(data: dict):
        return ModelVersionImage(
            id=data.get("id", -1),
            url=data.get("url", ""),
            nsfw=data.get("nsfw", True),
            width=data.get("width", 1024),
            height=data.get("height", 1024),
            hash=data.get("hash", ""),
            type=data.get("type", "image"),
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "nsfw": self.nsfw,
            "width": self.width,
            "height": self.height,
            "hash": self.hash,
            "type": self.type,
        }


class ModelVersion:
    def __init__(
        self,
        id: int,
        name: str,
        status: str,
        baseModel: BaseModel,
        description: Optional[str],
        stats: ModelVersionStats,
        files: List[ModelVersionFile],
        images: List[ModelVersionImage],
        downloadURL: str,
    ):
        self.id = id
        self.name = name
        self.status = status
        self.baseModel = baseModel
        self.description = description
        self.stats = stats
        self.files = files
        self.images = images
        self.downloadURL = downloadURL

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "baseModel": self.baseModel,
            "description": self.description,
            "stats": self.stats.serialize(),
            "files": [file.serialize() for file in self.files],
            "images": [image.serialize() for image in self.images],
            "downloadURL": self.downloadURL,
        }

    @staticmethod
    def deserialize(data: dict):
        return ModelVersion(
            id=data.get("id", int),
            name=data.get("name", ""),
            status=data.get("status", ""),
            baseModel=BaseModel(data.get("baseModel")),
            description=data.get("description", None),
            stats=ModelVersionStats.deserialize(data.get("stats", {})),
            files=[
                ModelVersionFile.deserialize(file) for file in data.get("files", {})
            ],
            images=[
                ModelVersionImage.deserialize(image) for image in data.get("images", {})
            ],
            downloadURL=data.get("downloadURL", ""),
        )


@dataclass
class ModelVersionDetail(ModelVersion):
    modelID: int
    updatedAt: str
    trainedWords: List[str]
    trainingStatus: Optional[str]
    name: str
    type: str
    nsfw: bool
    poi: bool


class Creator:
    def __init__(self, username: str, image: Optional[str]):
        self.username = username
        self.image = image

    @staticmethod
    def deserialize(data: dict):
        return Creator(username=data["username"], image=data.get("image", None))


class CivitModel:
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        poi: bool,
        type: ModelType,
        nsfw: bool,
        tags: List[str],
        creator: Creator,
        modelVersions: List[ModelVersion],
    ):
        self.id = id
        self.name = name
        self.description = description
        self.poi = poi
        self.type = type
        self.nsfw = nsfw
        self.tags = tags
        self.creator = creator
        self.modelVersions = modelVersions

    @staticmethod
    def deserialize(data: dict):

        return CivitModel(
            id=data.get("id", -1),
            name=data.get("name", ""),
            description=data.get("description", ""),
            poi=data.get("poi", False),
            type=ModelType(data.get("type")),
            nsfw=data.get("nsfw", True),
            tags=data.get("tags", []),
            creator=Creator.deserialize(data.get("creator", {"username": "Unknown"})),
            modelVersions=[
                ModelVersion.deserialize(version)
                for version in data.get("modelVersions", [])
            ],
        )


@dataclass
class SearchOptions:
    query: Optional[str]
    page: Optional[int]
    baseModel: Optional[BaseModel]
    types: List[ModelType]
    nsfw: bool = False


class CivitApi:

    def search_models(self, options: SearchOptions) -> List[CivitModel]:
        options.query = options.query or ""
        options.page = options.page or 1
        options.nsfw = options.nsfw or False
        options.baseModel = options.baseModel or BaseModel.StableDiffusion2_1
        if len(options.baseModel) > 0:
            base_model_string = "&baseModels=" + options.baseModel
        else:
            base_model_string = ""
        types_string = "&".join([f"types={x}" for x in options.types])
        nsfw_string = "true" if options.nsfw else "false"

        url = f"https://civitai.com/api/v1/models?{types_string}&sort=Highest%20Rated&limit=20&page={options.page}&nsfw={nsfw_string}&query={options.query.lower()}{base_model_string}"
        r = requests.get(url)
        r.raise_for_status()
        j = r.json()["items"]
        return [CivitModel.deserialize(b) for b in j]
