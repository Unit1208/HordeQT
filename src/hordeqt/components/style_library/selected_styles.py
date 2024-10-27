from __future__ import annotations

from typing import TYPE_CHECKING

from hordeqt.classes.Style import Style

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from typing import TYPE_CHECKING, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from hordeqt.components.style_library.style_item import StyleItem
from hordeqt.other.consts import LOGGER


class SelectedStyles(QWidget):
    updated = Signal()

    def __init__(self, parent: HordeQt) -> None:
        super().__init__(parent)
        self._parent = parent
        self.styles: List[StyleItem] = []
        # TODO: Make a scroll area for styles.
        self.styles_layout = QVBoxLayout()
        self.setLayout(self.styles_layout)

    def add_style_widget(self, style: Style):
        LOGGER.debug(f"Adding Style {style.name}")
        loraItem = StyleItem(self, style)
        self.styles_layout.addWidget(loraItem)
        self.styles.append(loraItem)
        self.updated.emit()

    def to_style_list(self) -> List[Style]:
        return [s.style_data for s in self.styles]

    def deleteStyle(self, style: StyleItem):
        style.hide()
        self.styles.remove(style)
        self.styles_layout.removeWidget(style)
        self.updated.emit()
        style.deleteLater()
        del style
        self.styles_layout.update()
