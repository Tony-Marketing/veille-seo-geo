"""Barre superieure du shell Desktop."""

from core.config import APP_NAME
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TopBar(QWidget):
    """Header principal de l'application."""

    def __init__(self) -> None:
        """Create the top bar widgets."""

        super().__init__()
        self.setObjectName("TopBar")

        title = QLabel(APP_NAME)
        title.setObjectName("TopBarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.addWidget(title)
