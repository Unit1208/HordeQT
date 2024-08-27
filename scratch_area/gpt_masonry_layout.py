from PySide6.QtWidgets import QApplication, QWidget, QLayout, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import QRect, QSize

class MasonryLayout(QLayout):
    def __init__(self, parent=None):
        super(MasonryLayout, self).__init__(parent)
        self.item_list = []

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
        
        # Get the width of the available space
        max_width = rect.width()
        num_columns = max_width // 200  # Assuming a fixed column width
        column_width = max_width // num_columns

        # Initialize column heights
        column_heights = [0] * num_columns
        
        for item in self.item_list:
            # Find the column with the minimum height
            min_col = column_heights.index(min(column_heights))
            x = min_col * column_width
            y = column_heights[min_col]
            
            # Place the item in the layout
            item.widget().setGeometry(QRect(x, y, column_width, item.sizeHint().height()))
            
            # Update the height of the column
            column_heights[min_col] += item.sizeHint().height()

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

class MasonryWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set the layout to MasonryLayout
        self.setLayout(MasonryLayout())

        # Add some widgets
        for i in range(10):
            button = QPushButton(f"Button {i}")
            self.layout().addWidget(button)

if __name__ == "__main__":
    app = QApplication([])

    window = MasonryWidget()
    window.show()

    app.exec()
