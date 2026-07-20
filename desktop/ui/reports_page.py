"""Reports placeholder connected to the existing CRUD list endpoint."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Signal
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
from services.reports_service import ReportsService, ReportsServiceError


class ReportsPage(QWidget):
    """Keep Reports limited to existing persisted CRUD data."""

    navigation_requested = Signal(str, object)

    def __init__(self, api_client: ApiClient) -> None:
        """Create the limited Reports integration page."""

        super().__init__()
        self.reports_service = ReportsService(api_client)
        self.current_website: dict[str, Any] | None = None
        self.current_entity_id: int | None = None

        title = QLabel("Reports")
        title.setObjectName("PageTitle")
        self.context_label = QLabel("Contexte Entity : aucun")
        self.context_label.setObjectName("PageSubtitle")
        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)
        self.monitoring_button = QPushButton("Ouvrir Monitoring")
        self.monitoring_button.clicked.connect(self.open_monitoring)
        self.table = QTableWidget(0, 4)
        self.table.setObjectName("DataTable")
        self.table.setHorizontalHeaderLabels(["Titre", "Type", "Statut", "Entity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = QHBoxLayout()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.monitoring_button)
        header.addWidget(self.refresh_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addLayout(header)
        layout.addWidget(self.context_label)
        layout.addWidget(self.message)
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self) -> None:
        """Load existing reports and apply the Entity context locally."""

        self.refresh_button.setEnabled(False)
        self.message.setText("Chargement des rapports existants...")
        try:
            result = self.reports_service.list_reports()
        except ReportsServiceError as exc:
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        else:
            items = result.items
            if self.current_entity_id is not None:
                items = [item for item in items if item.get("entity_id") == self.current_entity_id]
            self._populate(items)
            if not items:
                self.message.setText("Aucun rapport existant pour ce contexte.")
            elif result.total > result.page_size and self.current_entity_id is not None:
                self.message.setText("Rapports charges avec donnees partielles sur la premiere page API.")
            else:
                self.message.setText(f"{len(items)} rapport(s) existant(s) charge(s).")
        finally:
            self.refresh_button.setEnabled(True)

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        self.current_website = website
        entity_id = website.get("entity_id") if website is not None else None
        self.current_entity_id = entity_id if isinstance(entity_id, int) else None
        label = str(self.current_entity_id) if self.current_entity_id is not None else "aucun"
        self.context_label.setText(f"Contexte Entity : {label}")

    def set_navigation_context(self, context: dict[str, Any]) -> None:
        entity_id = context.get("entity_id")
        if isinstance(entity_id, int):
            self.current_entity_id = entity_id
            self.context_label.setText(f"Contexte Entity : {entity_id}")
            self.load_data()

    def open_monitoring(self) -> None:
        self.navigation_requested.emit("Monitoring", {"website": self.current_website})

    def _populate(self, items: list[dict[str, Any]]) -> None:
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [item.get("title"), item.get("report_type"), item.get("status"), item.get("entity_id")]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem("" if value is None else str(value)))

    def _error_message(self, exc: ReportsServiceError) -> str:
        if exc.status_code == 401:
            return "Connexion requise pour consulter Reports."
        if exc.status_code == 403:
            return "Acces refuse a Reports."
        if exc.status_code is not None and exc.status_code >= 500:
            return "Erreur serveur pendant le chargement Reports."
        return str(exc)
