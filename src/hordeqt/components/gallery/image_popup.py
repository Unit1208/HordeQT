from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from hordeqt.classes.LocalJob import LocalJob
from hordeqt.components.gallery.image_details_popup import ImageDetailsPopup
from hordeqt.other.consts import LOGGER


class ImagePopup(QDockWidget):
    def copy_prompt(self):
        LOGGER.debug(f"Copying prompt for {self.lj.id}")
        self._parent.clipboard.setText(self.lj.original.prompt)

    def delete_image(self):
        LOGGER.debug(f"Deleting image {self.lj.id}")
        self._parent.delete_image(self.lj)
        self.close()

    def copy_all(self):
        LOGGER.debug(f"Copying all details for {self.lj.id}")

        self._parent.clipboard.setText(self.lj.pretty_format())

    def use_prompt(self):
        self._parent.ui.PromptBox.setPlainText(self.lj.original.prompt.split("###")[0])
        self._parent.ui.tabWidget.setCurrentIndex(0)

    def use_all(self):
        self._parent.last_job_config = self._parent.save_job_config()
        self._parent.ui.undoResetButton.setEnabled(True)
        self._parent.ui.tabWidget.setCurrentIndex(0)
        self._parent.restore_job_config(self.lj.original.to_job_config())

    def open_details(self):
        LOGGER.debug(f"Opening details for {self.lj.id}")
        popup = ImageDetailsPopup(self.lj, self._parent)
        self._parent.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, popup)
        popup.show()

    def open_in_native_menu(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.lj.path))

    def __init__(self, pixmap: QPixmap, lj: LocalJob, parent: HordeQt):
        super().__init__("Image Viewer", parent)
        self._parent = parent
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.lj = lj
        # Create a label to display the image

        self.label = QLabel(self)
        self.label.setPixmap(
            pixmap.scaled(
                512,
                512,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.label.setMaximumSize(512, 512)

        # Create buttons
        use_prompt = QPushButton("Use Prompt")
        use_prompt.clicked.connect(self.use_prompt)
        use_all = QPushButton("Use All")
        use_all.clicked.connect(self.use_all)
        copy_prompt = QPushButton("Copy Prompt")
        copy_prompt.clicked.connect(self.copy_prompt)
        copy_all = QPushButton("Copy All")
        copy_all.clicked.connect(self.copy_all)
        show_details = QPushButton("Show Details")
        show_details.clicked.connect(self.open_details)
        delete_image = QPushButton("Delete Image")
        delete_image.clicked.connect(self.delete_image)
        open_in_native = QPushButton("Open with OS picture viewer")
        open_in_native.clicked.connect(self.open_in_native_menu)
        # Create horizontal layouts for button pairs
        copy_layout = QHBoxLayout()
        copy_layout.addWidget(copy_prompt)
        copy_layout.addWidget(copy_all)

        use_layout = QHBoxLayout()
        use_layout.addWidget(use_prompt)
        use_layout.addWidget(use_all)

        # Create a main vertical layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(copy_layout)
        layout.addLayout(use_layout)
        layout.addWidget(show_details)
        layout.addWidget(delete_image)
        layout.addWidget(open_in_native)

        # Create a central widget to set the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the widget for the QDockWidget
        self.setWidget(widget)

        self.setFloating(True)
        self.resize(400, 400)  # Adjust the size of the popup window
