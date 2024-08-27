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
        self.bpixmap = QPixmap(image_path)
        self.setPixmap(self.bpixmap)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        self.setPixmap(self.bpixmap.scaled(event.size()))


class MasonryLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=10):
        super(MasonryLayout, self).__init__(parent)
        self.margin = margin
        self.mspacing = spacing
        self.item_list: List[ImageWidget] = []
        self.column_heights = []
        self.num_columns = 0
        self.column_width = 0

    def addItem(self, item):
        self.item_list.append(item)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        return size

    def setGeometry(self, rect):
        super(MasonryLayout, self).setGeometry(rect)
        if not self.item_list:
            return

        self.calculateColumnLayout(rect.width())
        self.arrangeItems()

    def calculateColumnLayout(self, width):
        self.num_columns = max(
            1, width // (200 + self.mspacing)
        )  # Dynamically calculate number of columns
        self.column_width = (
            width - (self.num_columns - 1) * self.mspacing
        ) // self.num_columns
        self.column_heights = [0] * self.num_columns

    def arrangeItems(self):
        for item in self.item_list:
            widget = item.widget()
            pixmap = widget.pixmap()

            if pixmap:
                aspect_ratio = pixmap.width() / pixmap.height()
                height = self.column_width / aspect_ratio
            else:
                height = widget.sizeHint().height()

            min_col = self.column_heights.index(min(self.column_heights))
            x = min_col * (self.column_width + self.mspacing)
            y = self.column_heights[min_col]

            widget.setGeometry(QRect(x, y, self.column_width, height))
            self.column_heights[min_col] += height + self.mspacing

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None


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
