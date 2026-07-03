"""Page Tableau de bord."""

from typing import Any

from core.api_client import ApiClient
from core.config import APP_NAME, APP_VERSION
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    """Page d'accueil du client Desktop."""

    def __init__(self, api_client: ApiClient) -> None:
        """Create the dashboard page."""

        super().__init__()
        self.api_client = api_client
        self.backend_status = QLabel()
        self.backend_status.setObjectName("ValueLabel")
        self.backend_status.setText("Backend : non verifie")

        title = QLabel("Bienvenue")
        title.setObjectName("PageTitle")

        app_name = QLabel(APP_NAME)
        app_name.setObjectName("PageSubtitle")

        version = QLabel(f"Version {APP_VERSION}")
        version.setObjectName("ValueLabel")

        self.user_label = QLabel("Utilisateur : non connecte")
        self.user_label.setObjectName("ValueLabel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(app_name)
        layout.addWidget(version)
        layout.addWidget(self.backend_status)
        layout.addWidget(self.user_label)
        layout.addStretch()

    def refresh_backend_status(self) -> None:
        """Refresh backend availability information."""

        status = "connecté" if self.api_client.check_health() else "indisponible"
        self.backend_status.setText(f"Backend : {status}")

    def set_user(self, user: dict[str, Any] | None) -> None:
        """Update the displayed current user."""

        self.user_label.setText(f"Utilisateur : {self._user_label(user)}")

    def _user_label(self, user: dict[str, Any] | None) -> str:
        """Return a readable user label from the API payload."""

        if not user:
            return "non connecte"

        first_name = str(user.get("first_name") or "").strip()
        last_name = str(user.get("last_name") or "").strip()
        full_name = " ".join(part for part in (first_name, last_name) if part)
        if full_name:
            return full_name
        return str(user.get("email") or "utilisateur connecte")
