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
from hordeqt.other.consts import LOGGER

if TYPE_CHECKING:
    from hordeqt.app import HordeQt


class StyleBrowser(QDockWidget):
    def __init__(self, parent: HordeQt):
        super().__init__("Style Browser", parent)
        self._parent = parent
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.query_box = QLineEdit()
        self.query_box.setClearButtonEnabled(True)
        self.query_box.setPlaceholderText("Search for Styles")
        self.query_box.textEdited.connect(self.search_for_styles)
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
        best_match_styles: Sequence[Tuple[str, int]] = process.extract(
            query, self._parent.styleLibrary.get_available_style_names(), limit=10
        )  # type: ignore
        LOGGER.debug(f"Best matches for {query}: {best_match_styles}")
        for style, ranking in best_match_styles:
            s = self._parent.styleLibrary.get_style(style)
            if s is not None and ranking > 10:  # Keep intellisense happy.
                self.styleListLayout.addWidget(self.create_widget_from_response(s))

    def create_widget_from_response(self, style: Style):
        styleWidget = QWidget()
        styleWidgetLayout = QHBoxLayout()
        name_label = QLabel(style.name)
        details_button = QPushButton("Details")
        details_button.clicked.connect(lambda: StyleViewer(style, self._parent))
        styleWidgetLayout.addWidget(name_label)
        styleWidgetLayout.addWidget(details_button)
        styleWidget.setLayout(styleWidgetLayout)
        self.curr_widgets.append(styleWidget)
        return styleWidget
