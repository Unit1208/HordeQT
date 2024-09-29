from __future__ import annotations

from typing import TYPE_CHECKING, List

from hordeqt.civit.civit_api import CivitModel, ModelVersion
from hordeqt.classes.LoRA import LoRA
from hordeqt.components.loras.lora_item import LoRAItem

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from hordeqt.other.consts import LOGGER


class SelectedLoRAs(QWidget):
    updated = Signal()

    def __init__(self, parent: HordeQt) -> None:
        super().__init__(parent)
        self._parent = parent
        self.loras: List[LoRAItem] = []
        self.loraLayout = QVBoxLayout()
        self.setLayout(self.loraLayout)

    def add_lora_widget(self, LoRAModel: CivitModel, LoRAVersion: ModelVersion):
        LOGGER.debug(f"Adding LoRA {LoRAModel.name}")
        loraItem = LoRAItem(self, LoRAModel, LoRAVersion)
        self.loraLayout.addWidget(loraItem)
        self.loras.append(loraItem)
        self.updated.emit()

    def deleteLoRA(self, lora: LoRAItem):
        lora.hide()
        self.loras.remove(lora)
        self.loraLayout.removeWidget(lora)
        self.updated.emit()
        lora.deleteLater()
        del lora
        self.loraLayout.update()

    def to_LoRA_list(self) -> List[LoRA]:
        return [lora.to_LoRA_obj() for lora in self.loras]
