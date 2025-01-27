import os
from pathlib import Path

from PIL import Image

from hordeqt.classes.LocalJob import LocalJob
from hordeqt.other.consts import LOGGER, SAVED_IMAGE_DIR_PATH
from hordeqt.other.format_loader import get_local_job


def _get_possible_path(base: Path):
    suffixes = [".png", ".jpeg", ".jpg", ".webp"]
    for suffix in suffixes:
        if (t := base.with_suffix(suffix)).exists():
            return t


def rescan_jobs(current_jobs: list[LocalJob]):
    saved_images = os.listdir(SAVED_IMAGE_DIR_PATH)
    saved_id_set = set([(SAVED_IMAGE_DIR_PATH / x).stem for x in saved_images])
    curr_known_saved_images = set([job.id for job in current_jobs])
    unknown_images = list(saved_id_set - curr_known_saved_images)
    new_data = current_jobs
    for img_id in unknown_images:
        base = (SAVED_IMAGE_DIR_PATH / img_id).resolve()
        possible_path = _get_possible_path(base)
        if possible_path is None:
            # we will continue to try to scan for this and fail every time, but I'm not sure if there's an elegant way to solve it (non-destructively)
            LOGGER.warning(f'Unknown or invalid file in image directory: "{base}"')
            continue
        possible_path = possible_path.resolve()
        local_job = get_local_job(Image.open(possible_path))
        if local_job is not None:
            new_data.append(local_job)
        else:
            LOGGER.warning(
                f'Unknown or invalid image type in image directory: "{str(possible_path)}"'
            )
    return new_data
