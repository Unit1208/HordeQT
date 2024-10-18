from __future__ import annotations

from enum import IntEnum, auto

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from hordeqt.components.gallery.masonry_layout import MasonryLayout


class GallerySortOptions(IntEnum):
    OldestFirst = auto()
    NewestFirst = auto()
    LargestFirst = auto()
    SmallestFirst = auto()
    ModelNameAZ = auto()
    ModelNameZA = auto()


class ImageGalleryWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.m_layout = MasonryLayout(self)
        galLayout = QVBoxLayout()
        configLayout = QHBoxLayout()

        sortOptionsLabel = QLabel("Gallery sort by")

        self.sortOptionBox = QComboBox()
        self.sortOptionBox.addItem("Oldest First", GallerySortOptions.OldestFirst)
        self.sortOptionBox.addItem("Newest First", GallerySortOptions.NewestFirst)
        self.sortOptionBox.addItem("Largest First", GallerySortOptions.LargestFirst)
        self.sortOptionBox.addItem("Smallest First", GallerySortOptions.SmallestFirst)
        self.sortOptionBox.addItem("Model name (A-Z)", GallerySortOptions.LargestFirst)
        self.sortOptionBox.addItem("Model name (Z-A)", GallerySortOptions.SmallestFirst)

        sortOptionLayout = QHBoxLayout()
        sortOptionLayout.addWidget(sortOptionsLabel)
        sortOptionLayout.addWidget(self.sortOptionBox)

        configLayout.addLayout(sortOptionLayout)

        galLayout.addLayout(configLayout)
        galLayout.addLayout(self.m_layout)

        self.setLayout(galLayout)
