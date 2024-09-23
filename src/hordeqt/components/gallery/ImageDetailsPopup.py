from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDockWidget, QPlainTextEdit, QSizePolicy,
                               QVBoxLayout, QWidget)

from hordeqt.classes.LocalJob import LocalJob


class ImageDetailsPopup(QDockWidget):
    def __init__(self, lj: LocalJob, parent):
        super().__init__(f"Image details for {lj.id}", parent)
        self._parent = parent
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.lj = lj
        self.info_widget = QPlainTextEdit(self)
        self.info_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.info_widget.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        self.info_widget.setPlainText(self.lj.pretty_format())
        layout = QVBoxLayout()
        layout.addWidget(self.info_widget)
        widget = QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setFloating(True)
