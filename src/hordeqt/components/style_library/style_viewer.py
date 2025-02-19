from __future__ import annotations

import copy
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from hordeqt.classes.Style import Style
from hordeqt.components.clickable_label import ClickableLabel
from hordeqt.components.style_library.image_popup import ImagePopup

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from hordeqt.other.consts import LOGGER


class StyleViewer(QDockWidget):

    def save_style(self):
        # TODO: check if saving would overwrite existing style.

        if self.style_data.is_built_in:
            self._parent.show_warn_toast(
                "Failed to save style: Can't overwrite builtin styles.",
                "Please duplicate the style and try saving again",
            )
            return
        old_style_name = self.style_data.name

        new_style = Style(
            name=self.name_data.text().strip(),
            prompt_format=self.prompt_data.toPlainText().strip(),
            model=(
                self.model_data.currentText()
                if self.model_data.currentText() != "None"
                else None
            ),
            width=self.width_data.value() if self.width_data.value() != -1 else None,
            height=self.height_data.value() if self.height_data.value() != -1 else None,
            steps=self.steps_data.value() if self.steps_data.value() != -1 else None,
            cfg_scale=self.cfg_data.value() if self.cfg_data.value() != -1 else None,
            clip_skip=(
                self.clip_skip_data.value()
                if self.clip_skip_data.value() != -1
                else None
            ),
            karras=True,  # FIXME: add Karras toggle
            sampler="k_euler",  # FIXME: add sampler spinbox
            hires_fix=False,  # FIXME: Add Hires fix toggle
            loras=[],  # FIXME: LoRA editor (mini-selectedLoras?)
            is_built_in=False,
        )
        if old_style_name.strip() != new_style.name:
            save_name_confirmation = QMessageBox()
            save_name_confirmation.setIcon(QMessageBox.Icon.Question)
            save_name_confirmation.setInformativeText(
                f'Style name was changed. Would you like to rename "{old_style_name}" to "{new_style.name}"?'
            )
            save_name_confirmation.setStandardButtons(
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Abort
            )
            save_name_confirmation.setDefaultButton(QMessageBox.StandardButton.Abort)
            ret = save_name_confirmation.exec()
            if ret == QMessageBox.StandardButton.Yes:
                self._parent.styleLibrary.delete_style(old_style_name)
            elif ret == QMessageBox.StandardButton.No:
                pass
            elif ret == QMessageBox.StandardButton.Abort:
                self._parent.show_info_toast(
                    "Style not deleted",
                    f"{self.style_data.name} was not deleted",
                )
                return
        self._parent.styleLibrary.set_style(new_style)
        self.style_data = new_style
        self.reinitialize(new_style)
        self._parent.show_success_toast(
            "Saved style",
            f'Style "{self.style_data.name}" saved.',
        )

    def duplicate_style(self):
        new_style = copy.deepcopy(self.style_data)
        base_name = copy.copy(new_style.name)
        new_style.name = base_name + " copy"
        n = 0
        while self._parent.styleLibrary.get_style(new_style.name) is not None:
            n += 1
            new_style.name = base_name + " copy " + str(n)
        new_style.is_built_in = False
        self._parent.styleLibrary.set_style(new_style)
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
        confirm_box.setIcon(QMessageBox.Icon.Warning)
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
            self._delete_style()
        elif ret == QMessageBox.StandardButton.No:
            self._parent.show_info_toast(
                "Style not deleted",
                f"{self.style_data.name} was not deleted",
            )

    def _delete_style(self):
        self._parent.styleLibrary.delete_style(self.style_data)
        self.close()

    def use_style(self):
        self._parent.selectedStyles.add_style_widget(self.style_data)
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
        self.setup_ui()

    def setup_ui(self):
        self._layout = QVBoxLayout()
        self._layout.addStretch()

        # Create the UI layout components
        self.name_data = self.create_line_edit(self.style_data.name, "Name")
        self.prompt_data = self.create_text_edit(
            self.style_data.prompt_format, "Prompt"
        )
        self._layout.addWidget(
            QLabel('Enter -1 or "None" to leave items at their default value')
        )
        self.model_data = self.create_combo_box(
            [_ for _ in self._parent.model_dict.keys()],
            self.style_data.model or "None",
            "Model",
        )
        self.cfg_data = self.create_double_spin_box(
            self.style_data.cfg_scale, "Guidence", 1, 0.05, 0, 20
        )
        self.steps_data = self.create_spin_box(
            self.style_data.steps, "Steps", 1, 1, 100
        )
        self.width_data = self.create_spin_box(
            self.style_data.width, "Width", 64, 64, 3072
        )
        self.height_data = self.create_spin_box(
            self.style_data.height, "Height", 64, 64, 3072
        )
        self.clip_skip_data = self.create_spin_box(
            self.style_data.clip_skip, "CLIP skip", 1, 1, 12
        )
        self.previews_layout = QHBoxLayout()
        previews = self._parent.styleLibrary.previews.get(self.style_data.name, None)
        if previews is None:
            LOGGER.info(f"No previews for {self.style_data.name}")
        else:
            for preview_type in ["person", "place", "thing"]:
                if (preview_url := previews.get(preview_type)) is not None:
                    self.create_image(
                        preview_type.capitalize(), preview_url, QSize(256, 256)
                    )
        self._layout.addLayout(self.previews_layout)

        # Create and set buttons
        self.create_buttons()

        # Finalize the layout
        self.finalize_layout()

    def create_line_edit(self, text: str, label: str) -> QLineEdit:
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        line_edit = QLineEdit(text)
        layout.addWidget(label_widget)
        layout.addWidget(line_edit)
        self._layout.addLayout(layout)
        return line_edit

    def create_text_edit(self, text: str, label: str) -> QTextEdit:
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        text_edit = QTextEdit(text)
        layout.addWidget(label_widget)
        layout.addWidget(text_edit)
        self._layout.addLayout(layout)
        return text_edit

    def create_combo_box(
        self, items: list, current_text: Optional[str], label: str
    ) -> QComboBox:
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        combo_box = QComboBox()
        combo_box.addItem("None")
        for item in items:
            combo_box.addItem(item)
        combo_box.setMaxVisibleItems(10)
        combo_box.setCurrentText(current_text if current_text else "None")
        layout.addWidget(label_widget)
        layout.addWidget(combo_box)
        self._layout.addLayout(layout)
        return combo_box

    def create_double_spin_box(
        self,
        value: Optional[float],
        label: str,
        decimals: int,
        step: float,
        min_v: float,
        max_v: float,
    ) -> QDoubleSpinBox:
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        spin_box = QDoubleSpinBox()
        spin_box.setDecimals(decimals)
        spin_box.setMinimum(min(-1, min_v))
        spin_box.setMaximum(max_v)
        spin_box.setSingleStep(step)
        spin_box.setValue(value if value is not None else -1)
        layout.addWidget(label_widget)
        layout.addWidget(spin_box)
        self._layout.addLayout(layout)
        return spin_box

    def create_spin_box(
        self, value: Optional[int], label: str, step: int, min_v: int, max_v: int
    ) -> QSpinBox:
        if min_v > max_v:
            max_v, min_v = min_v, max_v
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        spin_box = QSpinBox()
        spin_box.setMinimum(min(-1, min_v))
        spin_box.setMaximum(max_v)
        spin_box.setValue(value if value is not None else -1)
        spin_box.setSingleStep(step)
        layout.addWidget(label_widget)
        layout.addWidget(spin_box)
        self._layout.addLayout(layout)
        return spin_box

    def create_image(self, name: str, image: str, size: QSize):
        layout = QVBoxLayout()
        label_widget = QLabel(name)
        image_widget = ClickableLabel("Loading preview")

        def set_preview_image(path: Path):
            im = QPixmap(path)
            image_widget.setPixmap(
                im.scaled(
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            image_widget.setText("")
            image_widget.clicked.connect(lambda: ImagePopup(path, self._parent))

        self._parent.download_thread.download_to_cache(image, set_preview_image)
        layout.addWidget(label_widget)
        layout.addWidget(image_widget)
        self.previews_layout.addLayout(layout)

    def create_buttons(self):
        use_button = QPushButton("Use Style")
        save_button = QPushButton("Save Style")
        duplicate_button = QPushButton("Duplicate Style")
        delete_button = QPushButton("Delete Style")

        duplicate_button.clicked.connect(self.duplicate_style)
        save_button.clicked.connect(self.save_style)
        delete_button.clicked.connect(self.delete_style)
        use_button.clicked.connect(self.use_style)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(use_button)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(duplicate_button)
        buttons_layout.addWidget(delete_button)

        self._layout.addLayout(buttons_layout)

    def finalize_layout(self):
        widget = QWidget()
        widget.setLayout(self._layout)
        self.setWidget(widget)
        self.setFloating(True)
        self.resize(600, 600)
        self.show()

    def reinitialize(self, new_style: Style):
        # Update style data and UI elements
        self.style_data = new_style
        self.name_data.setText(self.style_data.name)
        self.prompt_data.setText(self.style_data.prompt_format)
        self.model_data.setCurrentText(self.style_data.model or "None")
        self.cfg_data.setValue(self.style_data.cfg_scale or -1)
        self.steps_data.setValue(self.style_data.steps or -1)
        self.width_data.setValue(self.style_data.width or -1)
        self.height_data.setValue(self.style_data.height or -1)
        self.clip_skip_data.setValue(self.style_data.clip_skip or -1)
