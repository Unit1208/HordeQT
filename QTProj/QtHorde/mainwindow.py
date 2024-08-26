# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import QThread, Signal, Slot, QObject
from queue import Queue

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


class APIManager:
    max_requests = 10
    current_requests = []

    def __init__(self, api_key: str, max_requests: int) -> None:
        self.max_requests = max_requests
        self.api_key = api_key
        self.current_requests = []
        self.job_queue = Queue()

    def add_job(self, job):
        self.job_queue.put(job)

    def handle_queue(self):
        pass


class MainWindow(QMainWindow):
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_warn(self, message):
        QMessageBox.warning(self, "Warning", message)

    def show_info(self, message):

        QMessageBox.information(self, "Info", message)

    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        self.clipboard=app.clipboard()
        
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)
        if (k := keyring.get_password("QTHorde", "QTHordeUser")) != None:
            self.ui.apiKeyEntry.setText(k)

        self.ui.GenerateButton.clicked.connect(self.on_generate_click)
        self.ui.apiKeyEntry.returnPressed.connect(self.save_api_key)
        self.ui.saveAPIkey.clicked.connect(self.save_api_key)
        self.ui.copyAPIkey.clicked.connect(self.copy_api_key)
    def on_generate_click(self):
        self.show_info("Generate was clicked!")

    def save_api_key(self):
        self.api_key = self.ui.apiKeyEntry.text()
        keyring.set_password("QTHorde", "QTHordeUser", self.api_key)
        self.show_info("API Key saved!")
    def copy_api_key(self):
        # Is this confusing to the user? Would they expect the copy to copy what's currently in the api key, or the last saved value?
        self.clipboard.setText(self.api_key)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow(app)
    widget.show()
    sys.exit(app.exec())
