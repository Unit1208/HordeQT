from __future__ import annotations

from typing import TYPE_CHECKING, List

from hordeqt.civit.civit_api import CivitModel, ModelVersion
from hordeqt.classes.LoRA import LoRA
from hordeqt.components.loras.lora_item import LoRAItem

if TYPE_CHECKING:
    from hordeqt.app import HordeQt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Signal
from hordeqt.other.consts import LOGGER


class SelectedLoRAs(QWidget):
    updated=Signal()
    def __init__(self, parent: HordeQt) -> None:
        super().__init__(parent)
        self._parent = parent
        self.loras:List[LoRAItem]=[]
        self.loraLayout=QVBoxLayout()
        self.setLayout(self.loraLayout)
    def add_lora_widget(self,LoRAModel: CivitModel, LoRAVersion: ModelVersion):
        LOGGER.debug(f"Adding LoRA {LoRAModel.name}")
        l=LoRAItem(self,LoRAModel,LoRAVersion)
        self.loraLayout.addWidget(l)
        self.loras.append(l)
        self.updated.emit()
    def deleteLoRA(self,lora:LoRAItem):
        lora.hide()
        self.loras.remove(lora)
        self.loraLayout.removeWidget(lora)
        self.updated.emit()
        lora.deleteLater()
        del lora
        self.loraLayout.update()
    def to_LoRA_list(self)->List[LoRA]:
        return [l.to_LoRA_obj() for l in self.loras]