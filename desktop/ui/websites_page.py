"""Page Websites du client Desktop."""

from typing import Any

from core.api_client import ApiClient, ApiClientError
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


class WebsitesPage(QWidget):
    """Affiche les sites recuperes depuis l'API REST."""

    COLUMNS = ["Nom", "URL", "Actif", "Entité"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the websites page and load the initial data."""

        super().__init__()
        self.api_client = api_client

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
        try:
            payload = self.api_client.get("/websites", params={"page": 1, "page_size": 100})
            items, total, page, page_size, pages = self._parse_paginated_response(payload)
        except ApiClientError as exc:
            self.table.setRowCount(0)
            self.message.setText(f"API indisponible : {exc}")
        except (TypeError, ValueError) as exc:
            self.table.setRowCount(0)
            self.message.setText(f"Réponse API inattendue : {exc}")
        else:
            self._populate_table(items)
            self.message.setText(f"{total} site(s) trouvé(s) - page {page}/{pages} - {page_size} par page")
        finally:
            self.refresh_button.setEnabled(True)

    def _parse_paginated_response(self, payload: Any) -> tuple[list[dict[str, Any]], int, int, int, int]:
        """Validate and return the paginated website response fields."""

        if not isinstance(payload, dict):
            raise ValueError("la réponse n'est pas un objet paginé")

        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise ValueError(f"champ(s) manquant(s) : {fields}")

        items = payload["items"]
        if not isinstance(items, list):
            raise ValueError("le champ items n'est pas une liste")

        normalized_items = [item for item in items if isinstance(item, dict)]
        return (
            normalized_items,
            int(payload["total"]),
            int(payload["page"]),
            int(payload["page_size"]),
            int(payload["pages"]),
        )

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
