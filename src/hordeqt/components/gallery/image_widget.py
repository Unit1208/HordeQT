from PIL import Image
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

from hordeqt.classes.LocalJob import LocalJob
from hordeqt.other.consts import LOGGER


class ImageWidget(QLabel):
    imageClicked = Signal(QPixmap)
    valid: bool = True

    def __init__(self, lj: LocalJob):
        super().__init__()
        self.lj = lj
        if not lj.path.exists():
            self.valid = False
            return
        try:
            Image.open(lj.path).close()
        except Image.UnidentifiedImageError:
            self.valid = False
            return
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
