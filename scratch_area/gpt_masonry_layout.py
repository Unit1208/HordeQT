import os
from typing import List
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLayout,
    QSizePolicy,
    QLabel,
    QVBoxLayout,
    QScrollArea,
)
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPixmap


class ImageWidget(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.original_pixmap = QPixmap(image_path)
        self.setPixmap(self.original_pixmap)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)


class MasonryLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=10):
        super(MasonryLayout, self).__init__(parent)
        self.margin = margin
        self.spacing = spacing
        self.items = []

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def sizeHint(self):
        return self.minimumSize()

    def itemAt(self, index):
        return self.items[index] if 0 <= index < len(self.items) else None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def setGeometry(self, rect):
        super(MasonryLayout, self).setGeometry(rect)
        self.updateGeometry()

    def updateGeometry(self):
        if not self.items:
            return
        width = self.geometry().width()
        self.calculateColumnLayout(width)
        self.arrangeItems()

    def calculateColumnLayout(self, width):
        self.num_columns = max(1, width // (200 + self.spacing))
        self.column_width = (
            width - (self.num_columns - 1) * self.spacing
        ) // self.num_columns
        self.column_heights = [0] * self.num_columns

    def arrangeItems(self):
        x_offsets = [
            i * (self.column_width + self.spacing) for i in range(self.num_columns)
        ]
        for item in self.items:
            widget = item.widget()
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
            self.column_heights[min_col] += height + self.spacing


class MasonryGallery(QWidget):
    def __init__(self):
        super().__init__()

        layout = MasonryLayout(self)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_widget.setLayout(layout)

        scroll_area.setWidget(content_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        for image_path in os.listdir("images"):
            ip = "images/" + image_path
            if image_path.endswith(".png"):
                image_widget = ImageWidget(ip)
                layout.addWidget(image_widget)


if __name__ == "__main__":
    app = QApplication([])

    gallery = MasonryGallery()
    gallery.show()

    app.exec()
