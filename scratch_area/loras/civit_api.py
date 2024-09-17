import enum
from typing import List, Optional
import requests


## TRANSLATED FROM HORDENG's implementation
class BaseModel(enum):
    StableDiffusion1_4 = "SD 1.4"
    StableDiffusion1_5 = "SD 1.5"
    StableDiffusion1_5_LCM = "SD 1.5 LCM"
    StableDiffusion2_0 = "SD 2.0"
    StableDiffusion2_0_768 = "SD 2.0 768"
    StableDiffusion2_1 = "SD 2.1"
    StableDiffusion2_1_768 = "SD 2.1 768"
    StableDiffusion2_1_Unclip = "SD 2.1 Unclip"
    SDXL_0_9 = "SDXL 0.9"
    SDXL_1_0 = "SDXL 1.0"
    Pony = "Pony"
    SDXL_1_0_LCM = "SDXL 1.0 LCM"
    SDXL_Distilled = "SDXL Distilled"
    SDXL_Turbo = "SDXL Turbo"
    SDXL_Lightning = "SDXL Lightning"
    StableCascade = "Stable Cascade"
    SVD = "SVD"
    SVD_XT = "SVD XT"
    PlaygroundV2 = "Playground V2"
    PixArtA = "PixArt A"
    Other = "Other"
    Flux1S = "Flux.1 S"
    Flux1D = "Flux.1 D"


class ScanResult(enum):
    Pending = "Pending"
    Success = "Success"
    Danger = "Danger"
    Error = "Error"


class FP(enum):
    fp16 = "fp16"
    fp32 = "fp32"


class ModelSize(enum):
    full = "full"
    pruned = "pruned"


class ModelFormat(enum):
    SafeTensor = "SafeTensor"
    PickleTensor = "PickleTensor"
    Other = "Other"


class ModelType(enum):
    Checkpoint = "Checkpoint"
    TextualInversion = "TextualInversion"
    Hypernetwork = "Hypernetwork"
    AestheticGradient = "AestheticGradient"
    LORA = "LORA"
    Controlnet = "Controlnet"
    Poses = "Poses"


class ModelVersionStats:
    downloadCount: int
    ratingCount: int
    rating: float
    thumbsUpCount: int
    thumbsDownCount: int


class ModelVersionFileMetadata:
    fp: Optional[FP]
    size: Optional[ModelSize]
    format: Optional[ModelFormat]


class ModelVersionFile:
    id: int
    sizeKb: float
    name: str
    type: str
    pickleScanResult: ScanResult
    pickleScanMessage: Optional[str]
    virusScanResult: ScanResult
    virusScanMessage: Optional[str]
    scannedAt: Optional[str]
    primary: Optional[bool]
    metadata: ModelVersionFileMetadata
    downloadURL: str
    hashes: dict[str, str]


class ModelVersionImage:
    id: int
    url: str
    nsfw: bool
    width: int
    height: int
    hash: str
    type: str


class ModelVersion:
    id: int
    name: str
    status: str
    baseModel: BaseModel
    description: Optional[str]
    stats: ModelVersionStats
    files: List[ModelVersionFile]
    images: List[ModelVersionImage]
    downloadURL: str


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
    username: str
    image: Optional[str]


class CivitModel:
    id: int
    name: str
    description: str
    poi: bool
    type: ModelType
    nsfw: bool
    tags: List[str]
    creator: Creator
    modelVersions: List[ModelVersion]
