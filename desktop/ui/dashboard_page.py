"""Page Tableau de bord."""

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

        title = QLabel("Bienvenue")
        title.setObjectName("PageTitle")

        app_name = QLabel(APP_NAME)
        app_name.setObjectName("PageSubtitle")

        version = QLabel(f"Version {APP_VERSION}")
        version.setObjectName("ValueLabel")

        user = QLabel("Utilisateur : Admin")
        user.setObjectName("ValueLabel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(app_name)
        layout.addWidget(version)
        layout.addWidget(self.backend_status)
        layout.addWidget(user)
        layout.addStretch()

        self.refresh_backend_status()

    def refresh_backend_status(self) -> None:
        """Refresh backend availability information."""

        status = "connecté" if self.api_client.check_health() else "indisponible"
        self.backend_status.setText(f"Backend : {status}")
