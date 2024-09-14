from typing import Optional
from PySide6.QtCore import Qt
from hordeqt.ui_prompt_library import Ui_Dialog as PromptLibraryWidget
from hordeqt.ui_prompt_item import Ui_Form as PromptItemWidget

from PySide6.QtWidgets import QDialog, QWidget


class PromptItem(QWidget):
    def __init__(self, parent: Optional[QWidget], name: str, value: str) -> None:
        super().__init__(parent)
        self.ui: PromptItemWidget = PromptItemWidget()
        self.ui.setupUi(self)
        self.ui.fieldLineEdit.setText(name)
        self.ui.plainTextEdit.setPlainText(value)


class PromptLibrary(QDialog):
    def __init__(self, parent: Optional[QWidget], f: Qt.WindowType) -> None:
        super().__init__(parent, f)
        self.ui: PromptLibraryWidget = PromptLibraryWidget()
        self.ui.setupUi(self)

    def add_item(self, ui_type: str, ui_value: str):
        self.ui.verticalLayout.addWidget(PromptItem(None, ui_type, ui_value))
