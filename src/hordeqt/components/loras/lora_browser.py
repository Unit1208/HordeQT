from __future__ import annotations

from typing import TYPE_CHECKING, List

import requests
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import (QAbstractScrollArea, QDockWidget, QFrame,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from hordeqt.civit.civit_api import (CivitApi, CivitModel, ModelType,
                                     SearchOptions)
from hordeqt.components.loras.lora_viewer import LoraViewer
from hordeqt.other.util import horde_model_to_civit_baseline


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
        search_options = SearchOptions(
            query,
            1,
            horde_model_to_civit_baseline(
                self._parent.model_dict[self._parent.ui.modelComboBox.currentText()]
            ),
            [ModelType.LORA],
            self._parent.ui.NSFWCheckBox.isChecked(),
        )

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
