"""Page Monitoring du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from services.monitoring_service import MonitoringPaginatedPayload, MonitoringService, MonitoringServiceError


class MonitoringPage(QWidget):
    """Display consultative monitoring data returned by the REST API."""

    navigation_requested = Signal(str, object)

    CONNECTOR_COLUMNS = ["Connecteur", "Statut", "Actif", "Derniere sync", "Prochaine sync"]
    EVENT_COLUMNS = ["Date", "Type", "Severite", "Source", "Message"]
    SCHEDULE_COLUMNS = ["Nom", "Type", "Frequence", "Statut", "Actif", "Derniere", "Prochaine"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the monitoring page."""

        super().__init__()
        self.monitoring_service = MonitoringService(api_client)
        self.current_website: dict[str, Any] | None = None

        title = QLabel("Monitoring")
        title.setObjectName("PageTitle")

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)
        self.alerts_button = QPushButton("Ouvrir Alertes")
        self.alerts_button.clicked.connect(self.open_alerts)

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.cards: dict[str, QLabel] = {}
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        for index, (key, label) in enumerate(
            [
                ("total_events", "Evenements"),
                ("events_today", "Aujourd'hui"),
                ("warning_events", "Warnings"),
                ("error_events", "Erreurs"),
                ("critical_events", "Critiques"),
                ("active_sync_schedules", "Plans actifs"),
                ("inactive_sync_schedules", "Plans inactifs"),
                ("next_runs", "Prochaines sync"),
            ],
        ):
            card = self._card(label)
            self.cards[key] = card.findChild(QLabel, "CardValue") or QLabel("-")
            cards_layout.addWidget(card, index // 4, index % 4)

        self.connectors_table = self._table(self.CONNECTOR_COLUMNS)
        self.events_table = self._table(self.EVENT_COLUMNS)
        self.schedules_table = self._table(self.SCHEDULE_COLUMNS)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.alerts_button)

        main_tables_layout = QHBoxLayout()
        main_tables_layout.addWidget(self._section("Connecteurs", self.connectors_table), stretch=1)
        main_tables_layout.addWidget(self._section("Derniers evenements", self.events_table), stretch=2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(self.message)
        layout.addLayout(cards_layout)
        layout.addLayout(main_tables_layout, stretch=1)
        layout.addWidget(self._section("Planifications", self.schedules_table), stretch=1)

        self.load_data()

    def load_data(self) -> None:
        """Load monitoring data through the Desktop service."""

        self._set_busy(True)
        self.message.setText("Chargement du monitoring...")
        try:
            overview = self.monitoring_service.get_overview().data
            connectors = self.monitoring_service.list_connectors()
            events = self.monitoring_service.list_events(page_size=10)
            schedules = self.monitoring_service.list_sync_schedules(
                page_size=10,
                website_id=self._website_id(),
            )
        except MonitoringServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate_overview(overview)
            self._populate_connectors(connectors)
            self._populate_events(events)
            self._populate_schedules(schedules)
            self.message.setText("Monitoring a jour.")
        finally:
            self._set_busy(False)

    def _populate_overview(self, payload: dict[str, Any]) -> None:
        for key, label in self.cards.items():
            value = payload.get(key)
            if key == "next_runs" and isinstance(value, list):
                label.setText(str(len(value)))
            else:
                label.setText(str(value if value is not None else 0))

    def _populate_connectors(self, connectors: list[dict[str, Any]]) -> None:
        rows = [
            [
                item.get("name"),
                item.get("status"),
                item.get("enabled"),
                item.get("last_sync"),
                item.get("next_sync"),
            ]
            for item in connectors
        ]
        self._populate_table(self.connectors_table, rows)

    def _populate_events(self, result: MonitoringPaginatedPayload) -> None:
        rows = [
            [
                item.get("created_at"),
                item.get("event_type"),
                item.get("severity"),
                item.get("source"),
                item.get("message"),
            ]
            for item in result.items
        ]
        self._populate_table(self.events_table, rows)

    def _populate_schedules(self, result: MonitoringPaginatedPayload) -> None:
        rows = [
            [
                item.get("name"),
                item.get("sync_type"),
                item.get("frequency"),
                item.get("status"),
                item.get("is_active"),
                item.get("last_run_at"),
                item.get("next_run_at"),
            ]
            for item in result.items
        ]
        self._populate_table(self.schedules_table, rows)

    def _card(self, title: str) -> QGroupBox:
        group = QGroupBox(title)
        value = QLabel("-")
        value.setObjectName("CardValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(group)
        layout.addWidget(value)
        return group

    def _section(self, title: str, widget: QWidget) -> QGroupBox:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(widget)
        return group

    def _table(self, columns: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(columns))
        table.setObjectName("DataTable")
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def _populate_table(self, table: QTableWidget, rows: list[list[Any]]) -> None:
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                table.setItem(row_index, column_index, item)

    def _set_busy(self, busy: bool) -> None:
        self.refresh_button.setEnabled(not busy)

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        self.current_website = website

    def open_alerts(self) -> None:
        self.navigation_requested.emit("Alertes", {"website": self.current_website, "source": "orchestration"})

    def _website_id(self) -> int | None:
        website_id = self.current_website.get("id") if self.current_website is not None else None
        return website_id if isinstance(website_id, int) else None

    def _error_message(self, exc: MonitoringServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter le monitoring."
        if exc.code == "forbidden":
            return "Acces refuse : droits administrateur requis."
        if exc.code == "validation_error":
            return "Parametres de monitoring invalides."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement du monitoring."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant le monitoring : {exc}"
