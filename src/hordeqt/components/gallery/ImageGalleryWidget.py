from __future__ import annotations

from PySide6.QtWidgets import QWidget

from hordeqt.components.gallery.MasonryLayout import MasonryLayout


class ImageGalleryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.m_layout = MasonryLayout(self)
        self.setLayout(self.m_layout)
