from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

import requests

from hordeqt.civit.civit_api import (BaseModel, CivitApi, CivitModel,
                                     ModelType, ModelVersion, SearchOptions)
from hordeqt.components.gallery import ImageGalleryWidget
from hordeqt.other.util import (CACHE_PATH, get_bucketized_cache_path,
                                horde_model_to_civit_baseline)

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import QRect, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (QAbstractScrollArea, QComboBox, QDockWidget,
                               QFrame, QHBoxLayout, QLabel, QLayout,
                               QLayoutItem, QLineEdit, QPlainTextEdit,
                               QPushButton, QScrollArea, QSizePolicy,
                               QVBoxLayout, QWidget)

from hordeqt.other.consts import LOGGER


def _format_tags(tags: List[str]) -> str:
    b = ""
    if len(tags) > 0:
        b = ",".join([f'"{tag}"' for tag in tags])

    return b


class LoraBrowser(QDockWidget):
    def __init__(self, parent: HordeQt):
        super().__init__("LoRA Browser", parent)
        self._parent = parent
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.query_box = QLineEdit()
        self.query_box.setClearButtonEnabled(True)
        self.query_box.setPlaceholderText("Search for LoRAs from CivitAI")
        self.query_box.editingFinished.connect(self.search_for_loras)
        self.scrollArea = QScrollArea()
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setGeometry(QRect(10, 10, 951, 901))
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.scrollArea.setSizePolicy(sizePolicy)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())

        self.scrollArea.setFrameShadow(QFrame.Shadow.Sunken)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored
        )
        self.scrollArea.setWidgetResizable(True)
        self.loraList = QWidget()
        self.loraListLayout = QVBoxLayout()
        self.loraList.setLayout(self.loraListLayout)
        self.scrollArea.setWidget(self.loraList)
        self.formWidget = QWidget()
        self.formWidgetLayout = QVBoxLayout()
        self.formWidgetLayout.addWidget(self.query_box)
        self.formWidgetLayout.addWidget(self.scrollArea)

        self.formWidget.setLayout(self.formWidgetLayout)
        self.setWidget(self.formWidget)
        self.setFloating(True)
        self.show()
        self.resize(400, 400)
        self.curr_widgets = []
        self.search_for_loras()

    def search_for_loras(self):

        query = self.query_box.text()
        search_options = SearchOptions()
        search_options.query = query
        search_options.page = 1
        search_options.nsfw = self._parent.ui.NSFWCheckBox.isChecked()
        search_options.baseModel = horde_model_to_civit_baseline(
            self._parent.model_dict[self._parent.ui.modelComboBox.currentText()]
        )
        search_options.types = [ModelType.LORA]
        civitResponse = CivitApi().search_models(search_options)
        for curr_widget in self.curr_widgets:
            self.loraListLayout.removeWidget(curr_widget)
        self.curr_widgets = []
        for lora in civitResponse:
            self.loraListLayout.addWidget(self.create_widget_from_response(lora))

    def create_widget_from_response(self, resp: CivitModel):

        loraWidget = QWidget()
        loraWidgetLayout = QHBoxLayout()
        name_label = QLabel(resp.name)
        details_button = QPushButton("Details")
        details_button.clicked.connect(lambda: LoraViewer(resp, self._parent))
        loraWidgetLayout.addWidget(name_label)
        loraWidgetLayout.addWidget(details_button)
        loraWidget.setLayout(loraWidgetLayout)
        self.curr_widgets.append(loraWidget)
        return loraWidget


class LoraViewer(QDockWidget):
    version_mapping: Dict[str, ModelVersion]
    images: List[QPixmap]

    def update_on_version_change(self, version_str: str):
        version = self.version_mapping[version_str]
        for vi in version.images:
            url = vi.url

            path = get_bucketized_cache_path(url)
            if path.exists():
                self.add_image(path)

            def _set_pixmap_closure(resp: requests.Response):
                with open(path, "wb") as f:
                    f.write(resp.content)
                self.add_image(path)

            self._parent.download_thread.prepare_dl(url, "GET", {}, _set_pixmap_closure)

    def add_image(self, path: Path):
        im = QPixmap(path)
        l = QLabel()
        l.setPixmap(
            im.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
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
        creator_image = QLabel("Loading")

        if creator_image_url is not None:

            path = get_bucketized_cache_path(creator_image_url)
            if path.exists():
                self._set_creator_image(creator_image, path)

            def _set_pixmap_closure(resp: requests.Response):
                with open(path, "wb") as f:
                    f.write(resp.content)
                self._set_creator_image(creator_image, path)

            self._parent.download_thread.prepare_dl(
                creator_image_url, "GET", {}, _set_pixmap_closure
            )

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
        self.version_mapping = {}
        for version in model.modelVersions:
            self.LoRA_version_combobox.addItem(
                k := f"{version.name} ({version.baseModel})"
            )
            self.version_mapping[k] = version
        LoRA_version_layout = QHBoxLayout()
        LoRA_version_layout.addWidget(LoRA_version_label)
        LoRA_version_layout.addWidget(self.LoRA_version_combobox)
        self.images = []
        self.imageGallery = ImageGalleryWidget()

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
        im = QPixmap(path)
        creator_image.setPixmap(
            im.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        creator_image.setText("")  # Adjust the size of the popup window
