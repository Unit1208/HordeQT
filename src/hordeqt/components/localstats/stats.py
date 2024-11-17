import gzip
import os
from math import ceil
from pathlib import Path
from typing import Tuple

import human_readable as hr

from hordeqt.other.consts import CACHE_PATH, SAVED_DATA_PATH, SAVED_IMAGE_DIR_PATH
from hordeqt.other.util import get_size


def calculate_cache_size() -> str:
    if CACHE_PATH.exists():
        size = get_size(str(CACHE_PATH.resolve()))
        return hr.file_size(size)
    else:
        return "No files stored in cache"


def _total_size():
    return get_size(str(SAVED_IMAGE_DIR_PATH.resolve()))


def _total_images():
    return len(
        [
            x
            for x in os.listdir(SAVED_IMAGE_DIR_PATH)
            if x.endswith(("png", "jpg", "jpeg", "webp"))
        ]
    )


def calculate_images_size() -> str:
    if SAVED_IMAGE_DIR_PATH.exists():
        size = _total_size()
        return hr.file_size(size)
    else:
        return "No images saved"


def calculate_total_images() -> int:
    if SAVED_IMAGE_DIR_PATH.exists():
        n = _total_images()
        return n
    else:
        return 0


def calculate_average_image_size() -> str:
    if SAVED_IMAGE_DIR_PATH.exists():
        return hr.file_size(ceil(_total_size() / _total_images()), formatting=".1f")
    else:
        return "No images saved"


def _get_image_sizes():
    return [
        (x, os.stat(SAVED_IMAGE_DIR_PATH / x).st_size)
        for x in os.listdir(SAVED_IMAGE_DIR_PATH)
        if x.endswith(("png", "jpg", "jpeg", "webp"))
    ]


def calculate_largest_image() -> Tuple[str, Path | None]:
    if SAVED_IMAGE_DIR_PATH.exists():
        image_sizes = _get_image_sizes()
        image_sizes_sorted = sorted(image_sizes, key=lambda v: v[1], reverse=True)
        biggest = image_sizes_sorted[0]
        return (
            f"{biggest[0]} ({hr.file_size(biggest[1])})",
            SAVED_IMAGE_DIR_PATH / biggest[0],
        )
    else:
        return ("No Images Saved", None)


def calculate_smallest_image() -> Tuple[str, Path | None]:
    if SAVED_IMAGE_DIR_PATH.exists():
        image_sizes = _get_image_sizes()
        image_sizes_sorted = sorted(image_sizes, key=lambda v: v[1])
        smallest = image_sizes_sorted[0]
        return (
            f"{smallest[0]} ({hr.file_size(smallest[1])})",
            SAVED_IMAGE_DIR_PATH / smallest[0],
        )
    else:
        return ("No Images Saved", None)


def _uncompressed_save_file_size():
    try:
        with gzip.open(SAVED_DATA_PATH.with_suffix(".json.gz"), "rt") as f:
            return len(f.read())
    except FileNotFoundError:
        return -1


def _compressed_save_file_size():
    try:
        return os.stat(SAVED_DATA_PATH.with_suffix(".json.gz")).st_size
    except FileNotFoundError:
        return -1


def calculate_size_of_save_file() -> str:
    s = _uncompressed_save_file_size()
    if s == -1:
        return "No save file found"
    else:
        return hr.file_size(s)


def calculate_size_of_compressed_save_file():
    s = _compressed_save_file_size()
    if s == -1:
        return "No save file found"
    else:
        return hr.file_size(s)


def calculate_compression_ratio():
    compressed = _compressed_save_file_size()
    uncompressed = _uncompressed_save_file_size()
    if compressed == -1 or uncompressed == -1:
        return 0
    else:
        return compressed / uncompressed
