from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import QRect, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (QDockWidget, QHBoxLayout, QLabel, QLayout,
                               QLayoutItem, QPlainTextEdit, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)

from hordeqt.classes.LocalJob import LocalJob
from hordeqt.consts import LOGGER


class ImageWidget(QLabel):
    imageClicked = Signal(QPixmap)

    def __init__(self, lj: LocalJob):
        super().__init__()
        self.lj = lj
        self.original_pixmap = QPixmap(lj.path)
        self.setPixmap(self.original_pixmap)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.setPixmap(scaled_pixmap)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            LOGGER.debug(f"Gallery view item for {self.lj.id} was clicked")
            self.imageClicked.emit(self.original_pixmap)
        super().mouseReleaseEvent(ev)


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


class MasonryLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=10):
        super(MasonryLayout, self).__init__(parent)
        self.margin = margin
        self.m_spacing = spacing
        self.items: List[QLayoutItem] = []
        self.column_heights = []

    def addItem(self, arg__1):
        self.items.append(arg__1)

    def count(self):
        return len(self.items)

    def sizeHint(self):
        if not self.column_heights:
            self.updateGeometry()
        total_height = max(self.column_heights, default=0) + self.m_spacing
        return QSize(self.geometry().width(), total_height)

    def itemAt(self, index) -> QLayoutItem:
        try:
            return self.items[index]
        except IndexError:
            return None  # type: ignore

    def takeAt(self, index):
        return self.items.pop(index)

    def setGeometry(self, rect):  # type: ignore
        super(MasonryLayout, self).setGeometry(rect)
        self.updateGeometry()

    def updateGeometry(self):
        if not self.items:
            return
        width = self.geometry().width()
        self.calculateColumnLayout(width)
        self.arrangeItems()

    def calculateColumnLayout(self, width):
        self.num_columns = max(1, width // (200 + self.m_spacing))
        self.column_width = (
            width - (self.num_columns - 1) * self.m_spacing
        ) // self.num_columns
        self.column_heights = [0] * self.num_columns

    def delete_image(self, id: str):
        index = -1
        for i in range(len(self.items)):

            widget: ImageWidget = self.items[i].widget()  # type: ignore
            if id == widget.lj.id:
                index = i
                break
        if index == -1:
            LOGGER.warn(f"Image couldn't be found in gallery.")
            return
        del self.items[index]

    def arrangeItems(self):
        x_offsets = [
            i * (self.column_width + self.m_spacing) for i in range(self.num_columns)
        ]
        for item in self.items:
            widget: ImageWidget = item.widget()  # type: ignore
            pixmap = widget.pixmap()
            aspect_ratio = (
                pixmap.width() / pixmap.height()
                if pixmap
                else widget.sizeHint().width() / widget.sizeHint().height()
            )
            height = self.column_width / aspect_ratio
            min_col = self.column_heights.index(min(self.column_heights))
            x = x_offsets[min_col]
            y = self.column_heights[min_col]
            widget.setGeometry(QRect(x, y, self.column_width, height))
            self.column_heights[min_col] += height + self.m_spacing

        # Ensure the container widget height is adjusted based on the tallest column
        self.parentWidget().setMinimumHeight(max(self.column_heights) + self.m_spacing)


class ImageGalleryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.m_layout = MasonryLayout(self)
        self.setLayout(self.m_layout)
