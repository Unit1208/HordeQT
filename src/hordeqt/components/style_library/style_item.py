from __future__ import annotations

from typing import TYPE_CHECKING, Self

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from hordeqt.classes.Style import Style
from hordeqt.components.style_library.style_viewer import StyleViewer

if TYPE_CHECKING:
    from hordeqt.components.style_library.selected_styles import SelectedStyles

from PySide6.QtWidgets import QFrame


class StyleItem(QFrame):
    def __init__(self, parent: SelectedStyles, style: Style) -> None:
        super().__init__(parent)
        self._parent = parent
        self.style_data = style

        self._layout = QVBoxLayout()
        self._layout.addStretch()

        self.label = QLabel(self.style_data.name)
        self.edit_button = QPushButton("Edit style")
        self.edit_button.clicked.connect(
            lambda: StyleViewer(style, self._parent._parent)
        )
        self.delete_button = QPushButton("Remove Style")
        self.delete_button.clicked.connect(self.remove_style)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        self._layout.addWidget(self.label)
        self._layout.addLayout(buttons_layout)

        self.setLayout(self._layout)
        self.setFrameShadow(QFrame.Shadow.Sunken)

    def remove_style(self):
        self._parent.deleteStyle(self)

    @classmethod
    def deserialize(cls, val: dict, parent: SelectedStyles) -> Self:
        return cls(parent, Style.deserialize(val))
