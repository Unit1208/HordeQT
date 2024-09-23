from typing import Optional, Self

from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtWidgets import QListWidgetItem

from hordeqt.civit.civit_api import ModelVersion


class LoRA:
    name: str
    version_id: int
    strength: float
    clip_strength: float
    inject_trigger: Optional[str] = None
    model_version: ModelVersion

    @classmethod
    def from_ModelVersion(
        cls,
        name: str,
        modelVersion: ModelVersion,
        strength: float = 1,
        clip_strength: float = 1,
        inject_trigger: Optional[str] = None,
    ) -> Self:
        c = cls()
        c.name = name
        c.model_version = modelVersion
        c.version_id = modelVersion.id
        c.strength = strength
        c.clip_strength = clip_strength
        c.inject_trigger = inject_trigger
        return c

    def to_job_format(self) -> dict:
        base = {
            "name": str(self.version_id),
            "model": self.strength,
            "clip": self.clip_strength,
            "is_version": True,
        }
        if self.inject_trigger is not None:
            base["inject_trigger"] = self.inject_trigger
        return base

    def to_ListWidgetItem(self) -> QListWidgetItem:
        b = QListWidgetItem()
        b.setText(f"{self.name} - {self.model_version.name} ({self.model_version.id})")

        return b

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "id": self.version_id,
            "strength": self.strength,
            "clip_strength": self.clip_strength,
            "inject_trigger": self.inject_trigger,
            "model_version": self.model_version.serialize(),
        }

    @classmethod
    def deserialize(cls, val: dict) -> Self:
        c = cls()
        c.version_id = val.get("id", -1)
        c.strength = val.get("strength", 1)
        c.clip_strength = val.get("clip_strength", 1)
        c.inject_trigger = val.get("inject_trigger", None)
        c.model_version = ModelVersion.deserialize(val.get("model_version", {}))
        c.name = val.get("name", "")
        return c
