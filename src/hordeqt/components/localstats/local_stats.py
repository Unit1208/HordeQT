from __future__ import annotations

from typing import TYPE_CHECKING, List

from PySide6.QtWidgets import QFormLayout, QPushButton

from hordeqt.components.localstats.local_stat_item import LocalStatItem
from hordeqt.components.localstats.stats import (
    calculate_average_image_size,
    calculate_cache_size,
    calculate_compression_ratio,
    calculate_images_size,
    calculate_largest_image,
    calculate_size_of_compressed_save_file,
    calculate_size_of_save_file,
    calculate_smallest_image,
    calculate_total_images,
)
from hordeqt.other.consts import LOGGER

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtWidgets import QFrame


class LocalStats(QFrame):
    def __init__(self, parent: HordeQt) -> None:
        super().__init__(parent)
        self._parent = parent

        self._layout = QFormLayout()
        self.stats: List[LocalStatItem] = [
            LocalStatItem(self, "Cache Size", calculate_cache_size),
            LocalStatItem(self, "Total images size", calculate_images_size),
            LocalStatItem(self, "Total number of images", calculate_total_images),
            LocalStatItem(self, "Average image size", calculate_average_image_size),
            LocalStatItem(self, "Largest image", calculate_largest_image),
            LocalStatItem(self, "Smallest image", calculate_smallest_image),
            LocalStatItem(
                self, "Saved data size (uncompressed)", calculate_size_of_save_file
            ),
            LocalStatItem(
                self,
                "Saved data size (compressed)",
                calculate_size_of_compressed_save_file,
            ),
            LocalStatItem(
                self, "Saved data compression ratio", calculate_compression_ratio
            ),
        ]
        for widget in self.stats:
            LOGGER.debug(
                f"Adding {widget.label.text()} ({widget.display_value.text()})"
            )
            self._layout.addRow(widget.label, widget.display_value)
        self.refresh_button = QPushButton("Refresh statistics")
        self.refresh_button.clicked.connect(self.update_stats)
        self._layout.addWidget(self.refresh_button)
        self.setLayout(self._layout)

    def update_stats(self):
        for stat in self.stats:
            old = stat.display_value.text()
            stat.update_value()
            LOGGER.debug(
                f"Refreshing {stat.label.text()}  OLD: {old} NEW: {stat.display_value.text()}"
            )
