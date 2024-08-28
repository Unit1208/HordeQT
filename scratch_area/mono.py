from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QFont

app = QApplication([])

label = QLabel("This is a monospace font!")
font = QFont()
font.setStyleHint(QFont.Monospace)  # Set the style hint to Monospace
font.setFamily("Monospace")  # This ensures a fallback to a common monospace font
font.setPointSize(12)  # Set the font size (optional)
label.setFont(font)

label.show()
app.exec()
