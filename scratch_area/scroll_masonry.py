# This Python file uses the following encoding: utf-8
import datetime as dt
from PIL import Image, ExifTags
import tempfile
import re
import uuid
import human_readable as hr
from pathlib import Path
import json
import os
import random
import sys
import time
from typing import List, Dict, Optional, Self, Type
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QLineEdit,
    QWidget,
    QLayout,
    QSizePolicy,
    QLabel,
    QDockWidget,
    QScrollArea,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLayoutItem,
)
from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    QTimer,
    QStandardPaths,
    QRect,
    Qt,
    QUrl,
    QSize
)
from pyqttoast import Toast, ToastPreset, toast_enums
from PySide6.QtGui import QPixmap, QDesktopServices, QFont, QClipboard

from queue import Queue
import logging
import coloredlogs


class ImageWidget(QLabel):
    imageClicked = Signal(QPixmap)

    def __init__(self, path:Path):
        super().__init__()
        self.original_pixmap = QPixmap(path)
        self.setPixmap(self.original_pixmap)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
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
            self.imageClicked.emit(self.original_pixmap)
        super().mouseReleaseEvent(ev)


class ImagePopup(QDockWidget):

    # TODO: Implement buttons - Signal for each.
    def __init__(self, pixmap: QPixmap, parent):
        super().__init__("Image Viewer", parent)
        self._parent = parent
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        # Create a label to display the image
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Create buttons
        use_prompt = QPushButton("Use Prompt")
        use_all = QPushButton("Use All")
        copy_prompt = QPushButton("Copy Prompt")
        copy_all = QPushButton("Copy All")
        show_details = QPushButton("Show Details")

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
            return None # type: ignore

    def takeAt(self, index):
        return self.items.pop(index)

    def setGeometry(self, rect): # type: ignore
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
        self.column_width = (width - (self.num_columns - 1) * self.m_spacing) // self.num_columns
        self.column_heights = [0] * self.num_columns

    def arrangeItems(self):
        x_offsets = [i * (self.column_width + self.m_spacing) for i in range(self.num_columns)]
        for item in self.items:
            widget: ImageWidget = item.widget() # type: ignore
            pixmap = widget.pixmap()
            aspect_ratio = (pixmap.width() / pixmap.height() if pixmap
                            else widget.sizeHint().width() / widget.sizeHint().height())
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Create a container widget that will hold the MasonryLayout
        self.container_widget = ImageGalleryWidget()
        
        # Set the container widget as the widget for the scroll area
        self.scroll_area.setWidget(self.container_widget)
        
        # Set the scroll area as the central widget
        self.setCentralWidget(self.scroll_area)

        # Add some example ImageWidgets to the layout
        for p in os.listdir("/home/erospo/.local/share/Unit1208/Horde QT/images/"):
            image_widget = ImageWidget(Path("/home/erospo/.local/share/Unit1208/Horde QT/images/")/p)
            self.container_widget.m_layout.addWidget(image_widget)
            
        # self.resize(800,800)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
