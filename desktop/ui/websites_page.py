"""Page Websites du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from services.websites_service import WebsitesService, WebsitesServiceError


class WebsitesPage(QWidget):
    """Affiche les sites recuperes depuis l'API REST."""

    COLUMNS = ["Nom", "URL", "Actif", "Entité"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the websites page and load the initial data."""

        super().__init__()
        self.websites_service = WebsitesService(api_client)

        title = QLabel("Websites")
        title.setObjectName("PageTitle")

        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.clicked.connect(self.load_websites)

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setObjectName("DataTable")
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.table)

        self.load_websites()

    def load_websites(self) -> None:
        """Load the paginated websites response and update the table."""

        self.refresh_button.setEnabled(False)
        self.message.setText("Chargement des sites...")
        try:
            result = self.websites_service.list_websites()
            items = result.items
            total = result.total
            page = result.page
            page_size = result.page_size
            pages = result.pages
        except WebsitesServiceError as exc:
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        except (TypeError, ValueError) as exc:
            self.table.setRowCount(0)
            self.message.setText(f"Réponse API inattendue : {exc}")
        else:
            self._populate_table(items)
            self.message.setText(f"{total} site(s) trouvé(s) - page {page}/{pages} - {page_size} par page")
            if not items:
                self.message.setText("Aucun site web a afficher.")
        finally:
            self.refresh_button.setEnabled(True)

    def _populate_table(self, websites: list[dict[str, Any]]) -> None:
        """Render websites in the table."""

        self.table.setRowCount(len(websites))
        for row, website in enumerate(websites):
            values = [
                str(website.get("name") or ""),
                str(website.get("url") or ""),
                "Oui" if website.get("is_active") else "Non",
                self._entity_label(website),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, column, item)

    def _entity_label(self, website: dict[str, Any]) -> str:
        """Return a readable entity label from current or future API fields."""

        entity = website.get("entity")
        if isinstance(entity, dict):
            return str(entity.get("name") or entity.get("id") or "-")
        return str(website.get("entity_id") or "-")

    def _error_message(self, exc: WebsitesServiceError) -> str:
        """Return a readable UI message for websites loading errors."""

        if exc.code == "unauthorized":
            return "Connexion requise pour afficher les sites."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter les sites."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant le chargement des sites."
        return f"Erreur inattendue pendant le chargement des sites : {exc}"
