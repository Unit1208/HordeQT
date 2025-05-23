from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hordeqt.app import HordeQt

from PySide6.QtCore import QMutex, QThread, QWaitCondition

from hordeqt.other.consts import LOGGER


class SaveThread(QThread):
    def __init__(self, app: HordeQt, parent=None):
        super().__init__(parent)
        self.app = app
        self.running = True
        self.wait_condition = QWaitCondition()  # Condition variable
        self.mutex = QMutex()  # Mutex for synchronization

    def save(self):
        LOGGER.debug("Autosaving")
        self.app.savedData.update(
            self.app.api_thread,
            self.app.ui.NSFWCheckBox.isChecked(),
            self.app.ui.maxJobsSpinBox.value(),
            self.app.ui.saveMetadataCheckBox.isChecked(),
            self.app.job_download_thread,
            self.app.download_thread,
            self.app.save_job_config(),
            self.app.ui.shareImagesCheckBox.isChecked(),
            self.app.ui.tabWidget.currentIndex(),
            self.app.ui.saveFormatComboBox.currentText(),
            self.app.warned_models,
            self.app.ui.showDoneImagesCheckbox.isChecked(),
            self.app.ui.notifyAfterNFinishedSpinBox.value(),
            self.app.styleLibrary.get_user_styles(),
        )
        self.app.savedData.write()

    def run(self):
        interval = 30  # seconds
        while self.running:
            # Acquire the mutex to check for stop conditions
            self.mutex.lock()
            if not self.running:
                self.mutex.unlock()
                break

            self.save()

            # Wait for the condition variable for the specified interval or until interrupted
            self.wait_condition.wait(
                self.mutex, interval * 1000
            )  # Qt uses milliseconds
            self.mutex.unlock()

    def stop(self):
        self.mutex.lock()
        self.running = False
        self.wait_condition.wakeAll()  # Wake the thread immediately to exit
        self.mutex.unlock()

    def trigger_save(self):
        """Call this to wake the thread to save immediately, if needed."""
        self.mutex.lock()
        self.wait_condition.wakeAll()  # Wake the thread to run `save()` before the interval
        self.mutex.unlock()
