from __future__ import annotations

from typing import TYPE_CHECKING, Self

from hordeqt.civit.civit_api import CivitModel, ModelVersion
from hordeqt.classes.LoRA import LoRA

if TYPE_CHECKING:
    from hordeqt.components.loras.selected_loras import SelectedLoRAs

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QDoubleSpinBox, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QVBoxLayout)


class LoRAItem(QFrame):
    def __init__(
        self, parent: SelectedLoRAs, LoRAModel: CivitModel, LoRAVersion: ModelVersion
    ) -> None:
        super().__init__(parent)
        self._parent = parent
        self.loraModel = LoRAModel
        self.loraVersion = LoRAVersion

        LoRATitle = QLabel(
            f"{LoRAModel.name} - {LoRAVersion.name} ({self.loraVersion.id})"
        )
        modelStrengthLabel = QLabel("LoRA Strength (Model)")
        self.modelStrength = QDoubleSpinBox()
        self.modelStrength.setMinimum(-5)
        self.modelStrength.setMaximum(5)
        self.modelStrength.setDecimals(2)
        self.modelStrength.setValue(1)

        modelLayout = QHBoxLayout()
        modelLayout.addWidget(modelStrengthLabel)
        modelLayout.addWidget(self.modelStrength)

        CLIPStrengthLabel = QLabel("LoRA Strength (CLIP)")
        self.CLIPStrength = QDoubleSpinBox()
        self.CLIPStrength.setMinimum(-5)
        self.CLIPStrength.setMaximum(5)
        self.CLIPStrength.setDecimals(2)
        self.CLIPStrength.setValue(1)

        CLIPLayout = QHBoxLayout()
        CLIPLayout.addWidget(CLIPStrengthLabel)
        CLIPLayout.addWidget(self.CLIPStrength)

        injectTriggerLabel = QLabel("Inject Trigger")
        self.injectTrigger = QLineEdit("any")
        self.injectTrigger.setMaxLength(30)
        injectTriggerLayout = QHBoxLayout()
        injectTriggerLayout.addWidget(injectTriggerLabel)
        injectTriggerLayout.addWidget(self.injectTrigger)

        RemoveLoraButton = QPushButton(
            QIcon.fromTheme(QIcon.ThemeIcon.EditDelete), "Remove LoRA"
        )

        CLIPLayout = QHBoxLayout()
        CLIPLayout.addWidget(CLIPStrengthLabel)
        CLIPLayout.addWidget(self.CLIPStrength)

        self.lora_layout = QVBoxLayout()
        self.lora_layout.addWidget(LoRATitle)
        self.lora_layout.addLayout(modelLayout)
        self.lora_layout.addLayout(CLIPLayout)
        self.lora_layout.addLayout(injectTriggerLayout)
        self.lora_layout.addWidget(RemoveLoraButton)
        self.setLayout(self.lora_layout)
        self.setFrameShadow(QFrame.Shadow.Sunken)

    def remove_lora(self):
        self._parent.deleteLoRA(self)

    def to_LoRA_obj(self) -> LoRA:
        return LoRA(
            self.loraModel.name,
            self.loraVersion.id,
            self.modelStrength.value(),
            self.CLIPStrength.value(),
            self.loraVersion,
        )

    def serialize(self) -> dict:
        return {
            "loraModel": self.loraModel.serialize(),
            "loraVersion": self.loraVersion.serialize(),
        }

    @classmethod
    def deserialize(cls, val: dict, parent: SelectedLoRAs) -> Self:
        return cls(
            parent,
            CivitModel.deserialize(val.get("loraModel", {})),
            ModelVersion.deserialize(val.get("loraVersion", {})),
        )
