from __future__ import annotations

from typing import TYPE_CHECKING, List, Sequence, Tuple

from fuzzywuzzy import process
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from hordeqt.classes.Style import Style
from hordeqt.components.style_library.style_viewer import StyleViewer

if TYPE_CHECKING:
    from hordeqt.app import HordeQt


class StyleBrowser(QDockWidget):
    def __init__(self, parent: HordeQt):
        super().__init__("Style Browser", parent)
        self._parent = parent
        self.styles = parent.styleLibrary
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.query_box = QLineEdit()
        self.query_box.setClearButtonEnabled(True)
        self.query_box.setPlaceholderText("Search for Styles")
        self.query_box.editingFinished.connect(self.search_for_styles)
        self.scrollArea = QScrollArea()
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setGeometry(QRect(10, 10, 951, 901))
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.scrollArea.setSizePolicy(sizePolicy)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())

        self.scrollArea.setFrameShadow(QFrame.Shadow.Sunken)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored
        )
        self.scrollArea.setWidgetResizable(True)
        self.styleList = QWidget()
        self.styleListLayout = QVBoxLayout()
        self.styleList.setLayout(self.styleListLayout)
        self.scrollArea.setWidget(self.styleList)
        self.formWidget = QWidget()
        self.formWidgetLayout = QVBoxLayout()
        self.formWidgetLayout.addWidget(self.query_box)
        self.formWidgetLayout.addWidget(self.scrollArea)

        self.formWidget.setLayout(self.formWidgetLayout)
        self.setWidget(self.formWidget)
        self.setFloating(True)
        self.show()
        self.resize(400, 400)
        self.curr_widgets: List[QWidget] = []
        self.search_for_styles()

    def search_for_styles(self):
        query = self.query_box.text().strip()
        if len(query) > 0:
            self.setWindowTitle(f"Style Browser ({query})")
        else:
            self.setWindowTitle("Style Browser")
        for curr_widget in self.curr_widgets:
            self.styleListLayout.removeWidget(curr_widget)
            curr_widget.deleteLater()

        self.curr_widgets = []
        best_match_styles: Sequence[Tuple[int, str]] = process.extract(
            query, self.styles.get_available_style_names(), limit=10
        )  # type: ignore
        for ranking, style in best_match_styles:
            s = self.styles.get_style(style)
            if s is not None:  # Keep intellisense happy.
                self.styleListLayout.addWidget(self.create_widget_from_response(s))

    def create_widget_from_response(self, style: Style):
        loraWidget = QWidget()
        loraWidgetLayout = QHBoxLayout()
        name_label = QLabel(style.name)
        details_button = QPushButton("Details")
        details_button.clicked.connect(lambda: StyleViewer(style, self._parent))
        loraWidgetLayout.addWidget(name_label)
        loraWidgetLayout.addWidget(details_button)
        loraWidget.setLayout(loraWidgetLayout)
        self.curr_widgets.append(loraWidget)
        return loraWidget
