from __future__ import annotations

import copy
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
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from hordeqt.other.consts import LOGGER


class StyleViewer(QDockWidget):
    def save_style(self):
        if self.style_data.is_built_in:
            self._parent.show_warn_toast(
                "Failed to save style: Can't overwrite builtin styles.",
                "Please duplicate the style and try saving again",
            )
            return
        new_style = Style(
            name=self.name_data.text(),
            prompt_format=self.prompt_data.text(),
            model=self.model_data.currentText(),
            width=self.width_data.value(),
            height=self.height_data.value(),
            steps=self.steps_data.value(),
            cfg_scale=self.cfg_data.value(),
            karras=True,  # FIXME: add Karras toggle
            sampler="k_euler",  # FIXME: add sampler spinbox
            clip_skip=self.clip_skip_data.value(),
            hires_fix=False,  # FIXME: Add Hires fix toggle
            loras=[],
            is_built_in=False,
        )
        self._parent.styleLibrary.update_style(new_style)

    def duplicate_style(self):
        new_style = copy.deepcopy(self.style_data)
        base_name = copy.copy(new_style.name)
        new_style.name = base_name + " copy"
        n = 0
        while self._parent.styleLibrary.get_style(new_style.name) is not None:
            n += 1
            new_style.name = base_name + " copy " + str(n)
        new_style.is_built_in = False
        self._parent.styleLibrary.add_style(new_style)
        self._parent.show_success_toast(
            "Duplicated style",
            f'Copy of style "{self.style_data.name}" created, "{new_style.name}"',
        )
        StyleViewer(new_style, self._parent)

    def delete_style(self):
        if self.style_data.is_built_in:
            self._parent.show_warn_toast(
                "Failed to delete style",
                "Builtin styles can not be deleted",
            )
            return
        confirm_box = QMessageBox()
        confirm_box.setText("Deleted styles can not be recovered")
        confirm_box.setInformativeText(
            f'Are you sure you want to delete the style "{self.style_data.name}"'
        )
        confirm_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirm_box.setDefaultButton(QMessageBox.StandardButton.No)
        ret = confirm_box.exec()
        if ret == QMessageBox.StandardButton.Yes:
            pass
        elif ret == QMessageBox.StandardButton.No:
            self._parent.show_info_toast(
                "Style not deleted",
                f"{self.style_data.name} was not deleted",
            )

    def _delete_style(self):
        self._parent.styleLibrary.delete_style(self.style_data)
        self.close()

    def __init__(self, style: Style, parent: HordeQt):
        super().__init__(f"Style viewer ({style.name})", parent)
        LOGGER.debug(f"Opened Style viewer for {style.name}")

        self._parent = parent
        self.progress: Optional[QProgressDialog] = None
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.style_data = style

        name_layout = QHBoxLayout()
        name_label = QLabel("Name")
        self.name_data = QLineEdit(self.style_data.name)

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_data)

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
        # FIXME: set bounds
        cfg_layout = QHBoxLayout()
        cfg_label = QLabel("Guidence")
        self.cfg_data = QDoubleSpinBox()
        self.cfg_data.setDecimals(1)
        self.cfg_data.setValue(self.style_data.cfg_scale or 5.0)
        cfg_layout.addWidget(cfg_label)
        cfg_layout.addWidget(self.cfg_data)
        # FIXME: set bounds

        steps_layout = QHBoxLayout()
        steps_label = QLabel("Steps")
        self.steps_data = QSpinBox()
        self.steps_data.setValue(self.style_data.steps or 20)
        steps_layout.addWidget(steps_label)
        steps_layout.addWidget(self.steps_data)
        # FIXME: set bounds and step size (64)

        width_layout = QHBoxLayout()
        width_label = QLabel("Width")
        self.width_data = QSpinBox()
        self.width_data.setValue(self.style_data.width or 1024)
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_data)
        # FIXME: set bounds and step size (64)

        height_layout = QHBoxLayout()
        height_label = QLabel("Height")
        self.height_data = QSpinBox()
        self.height_data.setValue(self.style_data.height or 1024)
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_data)

        # FIXME: set bounds
        clip_skip_layout = QHBoxLayout()
        clip_skip_label = QLabel("CLIP skip")
        self.clip_skip_data = QSpinBox()
        self.clip_skip_data.setValue(self.style_data.clip_skip or 1)
        clip_skip_layout.addWidget(clip_skip_label)
        clip_skip_layout.addWidget(self.clip_skip_data)

        if self.style_data.is_built_in:
            self.name_data.setEnabled(False)
            self.prompt_data.setEnabled(False)
            self.model_data.setEnabled(False)
            self.cfg_data.setEnabled(False)
            self.steps_data.setEnabled(False)
            self.width_data.setEnabled(False)
            self.height_data.setEnabled(False)
            self.clip_skip_data.setEnabled(False)

        use_button = QPushButton("Use Style")
        save_button = QPushButton("Save Style")
        duplicate_button = QPushButton("Duplicate Style")
        delete_button = QPushButton("Delete Style")

        duplicate_button.clicked.connect(self.duplicate_style)
        save_button.clicked.connect(self.save_style)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(use_button)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(duplicate_button)
        buttons_layout.addWidget(delete_button)

        layout = QVBoxLayout()
        layout.addLayout(name_layout)
        layout.addLayout(prompt_layout)
        layout.addLayout(model_layout)
        layout.addLayout(cfg_layout)
        layout.addLayout(steps_layout)
        layout.addLayout(width_layout)
        layout.addLayout(height_layout)
        layout.addLayout(clip_skip_layout)

        layout.addLayout(buttons_layout)

        # Create a central widget to set the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the widget for the QDockWidget
        self.setWidget(widget)
        self.setFloating(True)
        self.resize(600, 600)
        self.show()
