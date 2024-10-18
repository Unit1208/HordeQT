from typing import List

from PySide6.QtCore import QRect, QSize
from PySide6.QtWidgets import QLabel, QLayout, QLayoutItem

from hordeqt.components.gallery.image_widget import ImageWidget
from hordeqt.other.consts import LOGGER


class MasonryLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=10) -> None:
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
        if len(self.items) == 0:
            return False
        width = self.geometry().width()
        self.calculateColumnLayout(width)
        self.arrangeItems()
        return True

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
            LOGGER.warning("Image couldn't be found in gallery.")
            return
        del self.items[index]

    def arrangeItems(self):
        x_offsets = [
            i * (self.column_width + self.m_spacing) for i in range(self.num_columns)
        ]
        for item in self.items:
            widget: QLabel = item.widget()  # type: ignore
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
