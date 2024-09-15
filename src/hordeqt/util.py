import importlib.metadata
import re
import sys
import uuid
from pathlib import Path
from typing import List

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication

from hordeqt.consts import LOGGER


def get_metadata():
    app_module = sys.modules["__main__"].__package__
    # Retrieve the app's metadata
    if app_module is None:
        raise Exception("Invalid package metadata")
    metadata = importlib.metadata.metadata(app_module)
    return metadata


# This whole function just feels... wrong.
def get_dynamic_constants():
    global SAVED_IMAGE_DIR_PATH, SAVED_DATA_DIR_PATH, SAVED_DATA_PATH, app
    metadata = get_metadata()

    if "app" not in globals():
        app = QApplication(sys.argv)
        app.setApplicationDisplayName(metadata["Formal-Name"])
        app.setApplicationName(metadata["Name"])
        app.setOrganizationName(metadata["Author"])

    SAVED_DATA_DIR_PATH = Path(
        QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    )
    SAVED_IMAGE_DIR_PATH = SAVED_DATA_DIR_PATH / "images"
    SAVED_DATA_PATH = SAVED_DATA_DIR_PATH / "saved_data.json"

    LOGGER.debug(f"Saved data path: {SAVED_DATA_PATH}")
    LOGGER.debug(f"Saved data dir: {SAVED_DATA_DIR_PATH}")
    LOGGER.debug(f"Saved images dir: {SAVED_IMAGE_DIR_PATH}")

    return app, SAVED_DATA_DIR_PATH, SAVED_DATA_PATH, SAVED_IMAGE_DIR_PATH  # type: ignore


# Ensure these are really loaded
get_dynamic_constants()


def create_uuid():
    return str(uuid.uuid4())


def get_headers(api_key: str):
    version = get_metadata()["Version"]
    return {
        "apikey": api_key,
        "Client-Agent": f"HordeQt:{version}:Unit1208",
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def prompt_matrix(prompt: str) -> List[str]:
    # fails with nested brackets, but that shouldn't be an issue?
    # Writing this out, {{1|2}|{3|4}} would evalutate to e.g [1,2,3,4], and I doubt that anyone would the former. If they do, I'll fix it. Maybe.
    # {{1|2|3|4}} should evalutate to [1,2,3,4] as well.
    matched_matrix = re.finditer(r"\{.+?\}", prompt, re.M)

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

        return generated_prompts

    matches = [match.group() for match in matched_matrix]
    result_prompts = generate_prompts(prompt, matches)

    # If no valid combinations were generated, return the original prompt
    return result_prompts if result_prompts else [prompt]
