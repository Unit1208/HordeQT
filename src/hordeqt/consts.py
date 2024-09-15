import logging

import coloredlogs

ANON_API_KEY = "0000000000"
BASE_URL = "https://aihorde.net/api/v2/"
LOGGER = logging.getLogger("HordeQT")
coloredlogs.install("DEBUG", milliseconds=True)
