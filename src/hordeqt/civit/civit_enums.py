from enum import StrEnum


class BaseModel(StrEnum):
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


class ScanResult(StrEnum):
    Pending = "Pending"
    Success = "Success"
    Danger = "Danger"
    Error = "Error"


class FP(StrEnum):
    fp16 = "fp16"
    fp32 = "fp32"


class ModelSize(StrEnum):
    full = "full"
    pruned = "pruned"


class ModelFormat(StrEnum):
    SafeTensor = "SafeTensor"
    PickleTensor = "PickleTensor"
    Other = "Other"


class ModelType(StrEnum):
    Checkpoint = "Checkpoint"
    TextualInversion = "TextualInversion"
    Hypernetwork = "Hypernetwork"
    AestheticGradient = "AestheticGradient"
    LORA = "LORA"
    Controlnet = "Controlnet"
    Poses = "Poses"
