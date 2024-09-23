from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from hordeqt.civit.civit_api import CivitModel, ModelVersion
from hordeqt.classes.LoRA import LoRA
from hordeqt.other.util import get_bucketized_cache_path

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

import human_readable as hr
from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QComboBox, QDockWidget, QHBoxLayout, QLabel,
                               QProgressDialog, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from hordeqt.other.consts import LOGGER


class LoraViewer(QDockWidget):
    version_mapping: Dict[str, ModelVersion]
    images: List[QLabel] = []
    finished = 0
    needs = 0

    def __init__(self, model: CivitModel, parent: HordeQt):
        super().__init__(f"LoRA viewer ({model.name})", parent)
        LOGGER.debug(f"Opened LoRA viewer from model: {model.name}")

        self._parent = parent
        self.progress: Optional[QProgressDialog] = None
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.model = model
        self.images = []

        # Create a label to display the image

        name_label = QLabel(model.name)
        creator_layout = QHBoxLayout()
        creator_image_url = model.creator.image
        creator_image = QLabel("Loading")
        self.image_gallery_layout = QVBoxLayout()

        gallery_widget = QWidget()
        gallery_widget.setLayout(self.image_gallery_layout)

        gallery_scroll_area = QScrollArea()
        gallery_scroll_area.setWidgetResizable(True)
        gallery_scroll_area.setWidget(gallery_widget)

        if creator_image_url is not None:

            path = get_bucketized_cache_path(creator_image_url)

            def _set_pixmap_closure(path: Path):
                self._set_creator_image(creator_image, path)

            if path.exists():
                self._set_creator_image(creator_image, path)
            else:

                self._parent.download_thread.download_to_cache(
                    creator_image_url, _set_pixmap_closure
                )

        creator_username = QLabel(model.creator.username)
        creator_layout.addWidget(creator_username)
        creator_layout.addWidget(creator_image)
        nsfw_layout = QHBoxLayout()
        nsfw_label = QLabel("NSFW:")
        nsfw_value = QLabel("Yes" if model.nsfw else "No")

        nsfw_layout.addWidget(nsfw_label)
        nsfw_layout.addWidget(nsfw_value)

        tags_list_layout = QHBoxLayout()

        tags_list_label = QLabel("Tags:")
        tags_list_value = QLabel(hr.listing(model.tags, ","))

        tags_list_layout.addWidget(tags_list_label)
        tags_list_layout.addWidget(tags_list_value)

        LoRA_version_label = QLabel("Version:")
        self.LoRA_version_combobox = QComboBox()
        self.version_mapping = {}
        for version in model.modelVersions:
            self.LoRA_version_combobox.addItem(
                k := f"{version.name} ({version.baseModel})"
            )
            self.version_mapping[k] = version
        if len(model.modelVersions) > 0:
            self.update_on_version_change(self.LoRA_version_combobox.currentText())
        LoRA_version_layout = QHBoxLayout()
        LoRA_version_layout.addWidget(LoRA_version_label)
        LoRA_version_layout.addWidget(self.LoRA_version_combobox)

        self.LoRA_version_combobox.currentTextChanged.connect(
            self.update_on_version_change
        )

        use_button = QPushButton("Use LoRA")
        use_button.clicked.connect(self.use_LoRA)
        # Create a main vertical layout and add widgets

        layout = QVBoxLayout()
        layout.addWidget(name_label)
        layout.addLayout(creator_layout)
        layout.addLayout(tags_list_layout)
        layout.addLayout(nsfw_layout)
        layout.addLayout(LoRA_version_layout)
        layout.addWidget(use_button)
        layout.addWidget(gallery_scroll_area)

        # Create a central widget to set the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the widget for the QDockWidget
        self.setWidget(widget)
        self.setFloating(True)
        self.resize(400, 400)
        self.show()

    def _set_creator_image(self, creator_image: QLabel, path: Path):
        im = QPixmap(path)
        self.set_pixmap(creator_image, im, QSize(64, 64))

        creator_image.setText("")

    def update_on_version_change(self, version_str: str):
        version = self.version_mapping[version_str]
        for child in self.images:
            self.image_gallery_layout.removeWidget(child)
            child.deleteLater()
        self.images = []
        self.needs = len(version.images)
        self.finished = 0

        # Create progress dialog
        self.progress = QProgressDialog(
            "Loading images...", "Cancel", 0, self.needs, self
        )
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)

        for vi in version.images:
            url = vi.url
            path = get_bucketized_cache_path(url)

            label = QLabel()
            self.images.append(label)

            # Signal-slot connection
            self._parent.download_thread.download_to_cache(
                url, lambda _: self.image_downloaded(label, path)
            )

    @Slot()
    def image_downloaded(self, label, path):
        self.finished += 1
        self.load_version_pixmap(path, label)
        self.image_gallery_layout.addWidget(label)

        # Update progress bar
        if self.progress is not None:
            self.progress.setValue(self.finished)

            if self.finished >= self.needs:
                self.progress.setValue(self.needs)
                self.progress.close()

    def load_version_pixmap(self, path, label):
        pixmap = QPixmap(path)
        label.setPixmap(pixmap)
        label.setScaledContents(True)

    def set_pixmap(self, label: QLabel, image: QPixmap, size: QSize):
        label.setPixmap(
            image.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def use_LoRA(self):
        version_str = self.LoRA_version_combobox.currentText()

        version = self.version_mapping[version_str]

        LOGGER.debug(f"Using LoRA version: {version.id}")
        self._parent.ui.loraListView.addItem(
            LoRA.from_ModelVersion(self.model.name, version).to_ListWidgetItem()
        )
