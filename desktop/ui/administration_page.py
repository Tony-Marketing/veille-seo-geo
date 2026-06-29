"""Page Administration."""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AdministrationPage(QWidget):
    """Placeholder du module Administration."""

    def __init__(self) -> None:
        """Create the page."""

        super().__init__()
        label = QLabel("Module en cours de développement.")
        label.setObjectName("PlaceholderLabel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(label)
        layout.addStretch()
