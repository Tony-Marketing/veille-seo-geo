"""Barre superieure du shell Desktop."""

from collections.abc import Callable

from core.config import APP_NAME
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class TopBar(QWidget):
    """Header principal de l'application."""

    def __init__(self, on_logout: Callable[[], None] | None = None) -> None:
        """Create the top bar widgets."""

        super().__init__()
        self.setObjectName("TopBar")

        title = QLabel(APP_NAME)
        title.setObjectName("TopBarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.user_label = QLabel("Non connecte")
        self.user_label.setObjectName("ValueLabel")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        self.website_label = QLabel("Website : aucun")
        self.website_label.setObjectName("ValueLabel")
        self.website_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        self.logout_button = QPushButton("Deconnexion")
        self.logout_button.setEnabled(False)
        if on_logout is not None:
            self.logout_button.clicked.connect(on_logout)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.website_label)
        layout.addWidget(self.user_label)
        layout.addWidget(self.logout_button)

    def set_user_label(self, label: str) -> None:
        """Update the displayed current user label."""

        self.user_label.setText(label)

    def set_logout_enabled(self, enabled: bool) -> None:
        """Enable or disable the logout action."""

        self.logout_button.setEnabled(enabled)

    def set_website_label(self, label: str) -> None:
        """Update the displayed Website context."""

        self.website_label.setText(f"Website : {label}")
