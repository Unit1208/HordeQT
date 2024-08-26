# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

import keyring
import requests
from http import HTTPStatus

ANON_API_KEY = "0000000000"
BASE_URL = "https://aihorde.net/api/v2/"


def get_headers(api_key: str):
    return {
        "apikey": api_key,
        "Client-Agent": "https://github.com/Unit1208/HordeQt:0.0.1:Unit1208",
    }


class MainWindow(QMainWindow):
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_warn(self, message):
        QMessageBox.warning(self, "Warning", message)

    def show_info(self, message):

        QMessageBox.information(self, "Info", message)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.GenerateButton.clicked.connect(self.onGenerateClick)

    def onGenerateClick(self):
        self.show_info("Generate was clicked!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
