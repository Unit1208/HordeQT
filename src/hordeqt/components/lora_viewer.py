from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

import requests

from hordeqt.civit.civit_api import (CivitApi, CivitModel, ModelType,
                                     ModelVersion, SearchOptions)
from hordeqt.classes.LoRA import LoRA
from hordeqt.other.util import (get_bucketized_cache_path,
                                horde_model_to_civit_baseline)

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

import human_readable as hr
from PySide6.QtCore import QRect, QSize, Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QAbstractScrollArea, QComboBox, QDockWidget,
                               QFrame, QHBoxLayout, QLabel, QLineEdit,
                               QProgressDialog, QPushButton, QScrollArea,
                               QSizePolicy, QVBoxLayout, QWidget)

from hordeqt.other.consts import LOGGER


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
        self.curr_widgets: List[QWidget] = []
        self.search_for_loras()

    def search_for_loras(self):

        query = self.query_box.text().strip()
        if len(query) > 0:
            self.setWindowTitle(f"LoRA Browser ({query})")
        else:
            self.setWindowTitle("LoRA Browser")
        search_options = SearchOptions()
        search_options.query = query
        search_options.page = 1
        search_options.nsfw = self._parent.ui.NSFWCheckBox.isChecked()
        # Make sure it's not null.
        search_options.baseModel = horde_model_to_civit_baseline(
            self._parent.model_dict[self._parent.ui.modelComboBox.currentText()]
        )
        search_options.types = [ModelType.LORA]
        try:
            civitResponse = CivitApi().search_models(search_options)
            for curr_widget in self.curr_widgets:
                self.loraListLayout.removeWidget(curr_widget)
                curr_widget.deleteLater()

            self.curr_widgets = []
            for lora in civitResponse:
                self.loraListLayout.addWidget(self.create_widget_from_response(lora))
        except requests.HTTPError as e:
            self._parent.show_error_toast(
                "CivitAI error", f'An error occured with the CivitAI API: "{e}"'
            )

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
    images: List[QLabel] = []
    finished = 0
    needs = 0

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
