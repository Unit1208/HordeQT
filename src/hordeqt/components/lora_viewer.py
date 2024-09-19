from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

import requests

from hordeqt.civit.civit_api import CivitModel, ModelVersion
from hordeqt.components.gallery import ImageGalleryWidget
from hordeqt.other.util import CACHE_PATH, get_bucketized_cache_path

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import QRect, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLayoutItem,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from hordeqt.other.consts import LOGGER


def _format_tags(tags: List[str]) -> str:
    b = ""
    if len(tags) > 0:
        b = ",".join([f'"{tag}"' for tag in tags])

    return b


class LoraViewer(QDockWidget):
    version_mapping: Dict[str, ModelVersion]
    images: List[QPixmap]

    def update_on_version_change(self, version_str: str):
        version = self.version_mapping[version_str]
        for vi in version.images:
            url = vi.url
            
            path=get_bucketized_cache_path(url)
            if path.exists():
                self.add_image(path)
            def _set_pixmap_closure(resp:requests.Response):
                with open(path,"wb") as f:
                    f.write(resp.content)
                self.add_image(path)
                    
            self._parent.download_thread.prepare_dl(url,"GET",{},_set_pixmap_closure)

    def add_image(self, path:Path):
        im=QPixmap(path)
        l=QLabel()
        l.setPixmap(im
                .scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        self.imageGallery.m_layout.addWidget(l)

    def __init__(self, model: CivitModel, parent: HordeQt):
        super().__init__("LoRA viewer", parent)
        self._parent = parent
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.model = model
        # Create a label to display the image

        name_label = QLabel(model.name)
        creator_layout = QHBoxLayout()
        creator_image_url = model.creator.image
        creator_image=QLabel("Loading")
        
        if creator_image_url is not None:
            
            path=get_bucketized_cache_path(creator_image_url)
            if path.exists():
                self._set_creator_image(creator_image, path)
            def _set_pixmap_closure(resp:requests.Response):
                with open(path,"wb") as f:
                    f.write(resp.content)
                self._set_creator_image(creator_image, path)
            self._parent.download_thread.prepare_dl(creator_image_url,"GET",{},_set_pixmap_closure)

        creator_username = QLabel(model.creator.username)
        creator_layout.addWidget(creator_username)

        nsfw_layout = QHBoxLayout()
        nsfw_label = QLabel("NSFW:")
        nsfw_value = QLabel("Yes" if model.nsfw else "No")

        nsfw_layout.addWidget(nsfw_label)
        nsfw_layout.addWidget(nsfw_value)

        tags_list_layout = QHBoxLayout()

        tags_list_label = QLabel("Tags:")
        tags_list_value = QLabel(_format_tags(model.tags))

        tags_list_layout.addWidget(tags_list_label)
        tags_list_layout.addWidget(tags_list_value)

        LoRA_version_label = QLabel("Version:")
        self.LoRA_version_combobox = QComboBox()
        for version in model.modelVersions:
            self.LoRA_version_combobox.addItem(
                k := f"{version.name} ({version.baseModel})"
            )
            self.version_mapping[k] = version
        LoRA_version_layout = QHBoxLayout()
        LoRA_version_layout.addWidget(LoRA_version_label)
        LoRA_version_layout.addWidget(self.LoRA_version_combobox)
        self.images = []
        self.imageGallery=ImageGalleryWidget()
        
        self.LoRA_version_combobox.currentTextChanged.connect(
            self.update_on_version_change
        )

        # Create a main vertical layout and add widgets

        layout = QVBoxLayout()
        layout.addWidget(name_label)
        layout.addLayout(creator_layout)
        layout.addLayout(nsfw_layout)
        layout.addLayout(LoRA_version_layout)
        layout.addWidget(self.imageGallery)

        # Create a central widget to set the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the widget for the QDockWidget
        self.setWidget(widget)

        self.setFloating(True)
        self.resize(400, 400) 

    def _set_creator_image(self, creator_image, path):
        im=QPixmap(path)
        creator_image.setPixmap(im
                        .scaled(
                        self.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    ))
        creator_image.setText("") # Adjust the size of the popup window
