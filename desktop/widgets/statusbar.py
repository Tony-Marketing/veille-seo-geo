"""Barre d'etat du shell Desktop."""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class StatusBar(QWidget):
    """Affiche un message d'etat global."""

    def __init__(self) -> None:
        """Create the status bar."""

        super().__init__()
        self.setObjectName("StatusBar")

        self.label = QLabel("Prêt")
        self.label.setObjectName("StatusBarLabel")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.addWidget(self.label)

    def set_message(self, message: str) -> None:
        """Update the displayed status message."""

        self.label.setText(message)
