from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Optional

import requests
from PySide6.QtCore import QMutex, QThread, QWaitCondition, Signal

from hordeqt.other.consts import ANON_API_KEY, BASE_URL, LOGGER
from hordeqt.other.util import get_headers


class OfflineComponent(IntEnum):
    HordeOffline = auto()
    InvalidHordeResponse = auto()
    RequestError = auto()
    DeviceOffline = auto()
    ConnectTimeout = auto()
    HTTPError = auto()
    ConnectionError = auto()


@dataclass
class OnlineStatus:
    online: bool
    offline_comp: Optional[OfflineComponent]


def oc_to_description(oc: Optional[OfflineComponent]) -> str:
    match oc:
        case OfflineComponent.HordeOffline:
            return "The Horde is currently offline."
        case OfflineComponent.InvalidHordeResponse:
            return (
                "Received an invalid response from the Horde. Please try again later."
            )
        case OfflineComponent.RequestError:
            return "There was an error processing the request."
        case OfflineComponent.DeviceOffline:
            return "The device is currently offline. Ensure that it is connected to the network."
        case OfflineComponent.ConnectTimeout:
            return (
                "The connection attempt timed out. Please check your network settings."
            )
        case OfflineComponent.HTTPError:
            return "An HTTP error occurred while attempting to connect."
        case OfflineComponent.ConnectionError:
            return "A connection error occurred. Please check your network connection and try again."
        case None:
            return "No error occurred."


class CheckConnectionThread(QThread):
    onlineUpdate = Signal(OnlineStatus)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.running = True
        self.wait_condition = QWaitCondition()
        self.mutex = QMutex()

    def run(self):
        while self.running:
            self.mutex.lock()
            if not self.running:
                self.mutex.unlock()
                break
            status = self.checkConnection()
            self.onlineUpdate.emit(status)  # Emit the status update
            self.wait_condition.wait(self.mutex, 10000)
            self.mutex.unlock()

    def checkConnection(self) -> OnlineStatus:
        try:
            r = requests.get(
                BASE_URL + "status/heartbeat",
                headers=get_headers(ANON_API_KEY, False),
                timeout=10,
            )
            r.raise_for_status()  # Raise an error for bad HTTP responses
        except requests.exceptions.Timeout:
            return OnlineStatus(False, OfflineComponent.ConnectTimeout)
        except requests.exceptions.ConnectionError:
            return OnlineStatus(False, OfflineComponent.ConnectionError)
        except requests.exceptions.HTTPError as e:
            LOGGER.error(f"HTTP error occurred: {e}")  # Log HTTP errors
            return OnlineStatus(False, OfflineComponent.HTTPError)
        except requests.exceptions.RequestException as e:
            LOGGER.error(
                f"Request error occurred: {e}"
            )  # General request exception logging
            return OnlineStatus(False, OfflineComponent.RequestError)

        try:
            b = r.json()
        except requests.exceptions.JSONDecodeError:
            LOGGER.error("Invalid response received; unable to decode JSON.")
            return OnlineStatus(False, OfflineComponent.InvalidHordeResponse)

        # Check for specific conditions in the response (you may adjust according to your API's response structure)
        if not b.get("message", {}) == "OK":
            LOGGER.warning("Horde is offline.")
            return OnlineStatus(False, OfflineComponent.HordeOffline)
        return OnlineStatus(True, None)  # If everything is okay, return online status

    def stop(self):
        self.mutex.lock()
        self.running = False
        self.wait_condition.wakeAll()  # Wake the thread immediately to exit
        self.mutex.unlock()
        self.wait()
