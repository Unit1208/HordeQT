from __future__ import annotations

from os import PathLike
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDockWidget, QLabel, QSizePolicy, QVBoxLayout, QWidget

from hordeqt.other.consts import LOGGER


class ImagePopup(QDockWidget):
    def __init__(self, path: PathLike[str], parent: HordeQt):
        super().__init__("Image Viewer", parent)
        LOGGER.debug(f"Opening {path}")
        self._parent = parent
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        # Create a label to display the image

        self.label = QLabel(self)
        self.label.setPixmap(QPixmap(path))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        # Create a main vertical layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        # Create a central widget to set the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the widget for the QDockWidget
        self.setWidget(widget)

        self.setFloating(True)
        self.resize(400, 400)  # Adjust the size of the popup window
        self.show()
