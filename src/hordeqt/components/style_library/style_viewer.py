from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from hordeqt.classes.Style import Style

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressDialog,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from hordeqt.other.consts import LOGGER


class StyleViewer(QDockWidget):

    def __init__(self, style: Style, parent: HordeQt):
        super().__init__(f"Style viewer ({style.name})", parent)
        LOGGER.debug(f"Opened Style viewer for {style.name}")

        self._parent = parent
        self.progress: Optional[QProgressDialog] = None
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.style_data = style

        name_label = QLabel(style.name)
        prompt_layout = QHBoxLayout()
        prompt_label = QLabel("Prompt")
        self.prompt_data = QLineEdit(self.style_data.prompt_format)
        prompt_layout.addWidget(prompt_label)
        prompt_layout.addWidget(self.prompt_data)

        model_layout = QHBoxLayout()
        model_label = QLabel("Model")
        self.model_data = QComboBox()
        for model in parent.model_dict.keys():
            self.model_data.addItem(model)
        self.model_data.setCurrentText(self.style_data.model)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_data)

        cfg_layout = QHBoxLayout()
        cfg_label = QLabel("Guidence")
        self.cfg_data = QDoubleSpinBox()
        self.cfg_data.setDecimals(1)
        cfg_layout.addWidget(cfg_label)
        cfg_layout.addWidget(self.cfg_data)

        steps_layout = QHBoxLayout()
        steps_label = QLabel("Steps")
        self.steps_data = QSpinBox()
        steps_layout.addWidget(steps_label)
        steps_layout.addWidget(self.steps_data)

        width_layout = QHBoxLayout()
        width_label = QLabel("Width")
        self.width_data = QSpinBox()
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_data)

        height_layout = QHBoxLayout()
        height_label = QLabel("Height")
        self.height_data = QSpinBox()
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_data)

        use_button = QPushButton("Use Style")
        save_button = QPushButton("Save Style")
        duplicate_button = QPushButton("Duplicate Style")
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(use_button)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(duplicate_button)

        layout = QVBoxLayout()
        layout.addWidget(name_label)
        layout.addLayout(prompt_layout)
        layout.addLayout(model_layout)
        layout.addLayout(cfg_layout)
        layout.addLayout(steps_layout)

        layout.addLayout(buttons_layout)

        # Create a central widget to set the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the widget for the QDockWidget
        self.setWidget(widget)
        self.setFloating(True)
        self.resize(400, 400)
        self.show()
