import logging

import coloredlogs

ANON_API_KEY = "0000000000"
BASE_URL = "https://aihorde.net/api/v2/"
LOGGER = logging.getLogger("HordeQT")
coloredlogs.install("DEBUG", milliseconds=True)

UPSCALE_MAP={
    None:None,
    "None":None,
    "RealESRGAN 2x":"RealESRGAN_x2plus",
    "RealESRGAN 4x":"RealESRGAN_x4plus",
    "RealESRGAN 4x Anime":"RealESRGAN_x4plus_anime_6B",
    "NMKD Siax":"NMKD_Siax",
    "Anime 4x":"4x_AnimeSharp"
}