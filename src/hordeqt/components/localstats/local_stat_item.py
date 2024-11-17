from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, Tuple, TypeVar

from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy

if TYPE_CHECKING:
    from hordeqt.components.localstats.local_stats import LocalStats

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

T = TypeVar("T")


class LocalStatItem(Generic[T]):
    current_value: T

    def __init__(
        self, parent: LocalStats, name: str, update_function: Callable[[], T]
    ) -> None:

        self.label = QLabel(name + ":")
        self.update_function = update_function
        self.display_value = QLabel("")
        self.update_value()

    def update_value(self):
        self.current_value = self.update_function()
        self._set_display(self.current_value)

    def _set_display(self, current_value: T):
        if isinstance(current_value, int):
            self.display_value = QLabel()
            self.display_value.setText(str(current_value))
        elif isinstance(current_value, float):
            self.display_value = QLabel()
            self.display_value.setText(f"{current_value:.2f}")
        elif isinstance(current_value, str):
            self.display_value = QLabel()
            self.display_value.setText(current_value)
        elif isinstance(current_value, Tuple) and len(current_value) == 2:
            # (display value, path to open on click)
            self._set_display(current_value[0])
            tmp = self.display_value
            if tmp is not None and current_value[1] is not None:
                if not isinstance(self.display_value, QLabel):
                    raise NotImplementedError("Nested buttons are not supported.")
                self.display_value = QPushButton(self.display_value.text())
                self.display_value.setSizePolicy(
                    QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
                )
                self.display_value.pressed.connect(
                    lambda: QDesktopServices.openUrl(
                        QUrl.fromLocalFile(current_value[1])
                    )
                )

        else:
            raise NotImplementedError(
                f"Value ({self.current_value}) of type {type(self.current_value)} is not supported yet."
            )
