from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from hordeqt.app import HordeQt
import requests
from PySide6.QtCore import QObject, QStandardPaths, QThread, Signal

from hordeqt.consts import LOGGER
from hordeqt.util import SAVED_DATA_DIR_PATH,SAVED_DATA_PATH,SAVED_IMAGE_DIR_PATH
from hordeqt.saved_data import SavedData
class SaveThread(QThread):
    def __init__(self, app:HordeQt,parent: QObject | None =None) -> None:
        super().__init__(parent)
        self.app=app
        self.running=True
    def save(self):
        self.app.savedData.update(
            self.app.api_thread,
            self.app.ui.NSFWCheckBox.isChecked(),
            self.app.ui.maxJobsSpinBox.value(),
            self.app.ui.saveMetadataCheckBox.isChecked(),
            self.app.download_thread,
            self.app.save_job_config(),
            self.app.ui.shareImagesCheckBox.isChecked(),
            self.app.ui.tabWidget.currentIndex(),
            self.app.ui.saveFormatComboBox.currentText(),
            self.app.warned_models,
        )
        self.app.savedData.write()
    def run(self):
        
        while self.running:
            self.save()
            time.sleep(30)