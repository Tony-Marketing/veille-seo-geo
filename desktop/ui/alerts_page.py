"""Page Alertes du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from services.alerts_service import AlertPaginatedPayload, AlertsService, AlertsServiceError


class AlertsPage(QWidget):
    """Display consultative alerts returned by the REST API."""

    navigation_requested = Signal(str, object)
    data_changed = Signal()

    COLUMNS = [
        "ID",
        "Severite",
        "Statut",
        "Categorie",
        "Source",
        "Titre",
        "Premiere vue",
        "Derniere vue",
    ]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the alerts page."""

        super().__init__()
        self.alerts_service = AlertsService(api_client)

        title = QLabel("Centre d'alertes")
        title.setObjectName("PageTitle")

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)
        self.refresh_from_monitoring_button = QPushButton("Analyser le monitoring")
        self.refresh_from_monitoring_button.clicked.connect(self.refresh_from_monitoring)
        self.acknowledge_button = QPushButton("Acquitter")
        self.acknowledge_button.clicked.connect(self.acknowledge_selected)
        self.resolve_button = QPushButton("Resoudre")
        self.resolve_button.clicked.connect(self.resolve_selected)
        self.dashboard_button = QPushButton("Ouvrir Dashboard V2")
        self.dashboard_button.clicked.connect(self.open_dashboard)

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.cards: dict[str, QLabel] = {}
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        for index, (key, label) in enumerate(
            [
                ("total", "Total"),
                ("active", "Actives"),
                ("acknowledged", "Acquittees"),
                ("resolved", "Resolues"),
                ("info", "Info"),
                ("warning", "Warnings"),
                ("critical", "Critiques"),
                ("last_alert_at", "Derniere alerte"),
            ],
        ):
            card = self._card(label)
            self.cards[key] = card.findChild(QLabel, "CardValue") or QLabel("-")
            cards_layout.addWidget(card, index // 4, index % 4)

        self.status_filter = self._combo(["", "Active", "Acknowledged", "Resolved"])
        self.severity_filter = self._combo(["", "Info", "Warning", "Critical"])
        self.category_filter = self._combo(["", "sync", "connector", "system", "auth", "import", "export"])
        self.source_filter = QLineEdit()
        self.source_filter.setPlaceholderText("Source")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche")
        self.apply_filters_button = QPushButton("Filtrer")
        self.apply_filters_button.clicked.connect(self.load_data)
        self.reset_filters_button = QPushButton("Reinitialiser")
        self.reset_filters_button.clicked.connect(self.reset_filters)

        self.table = self._table(self.COLUMNS)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_from_monitoring_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.dashboard_button)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Statut"))
        filters_layout.addWidget(self.status_filter)
        filters_layout.addWidget(QLabel("Severite"))
        filters_layout.addWidget(self.severity_filter)
        filters_layout.addWidget(QLabel("Categorie"))
        filters_layout.addWidget(self.category_filter)
        filters_layout.addWidget(self.source_filter)
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.apply_filters_button)
        filters_layout.addWidget(self.reset_filters_button)

        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        actions_layout.addWidget(self.acknowledge_button)
        actions_layout.addWidget(self.resolve_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(self.message)
        layout.addLayout(cards_layout)
        layout.addLayout(filters_layout)
        layout.addWidget(self._section("Alertes", self.table), stretch=1)
        layout.addLayout(actions_layout)

        self.load_data()

    def load_data(self) -> None:
        """Load alert summary and list through the Desktop service."""

        self._set_busy(True)
        self.message.setText("Chargement des alertes...")
        try:
            summary = self.alerts_service.get_summary().data
            alerts = self.alerts_service.list_alerts(
                status=self._current_filter(self.status_filter),
                severity=self._current_filter(self.severity_filter),
                category=self._current_filter(self.category_filter),
                source=self._text_filter(self.source_filter),
                search=self._text_filter(self.search_input),
            )
        except AlertsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate_summary(summary)
            self._populate_alerts(alerts)
            self.message.setText("Alertes a jour.")
        finally:
            self._set_busy(False)

    def refresh_from_monitoring(self) -> None:
        """Refresh alerts from monitoring data through the API."""

        self._set_busy(True)
        try:
            result = self.alerts_service.refresh_from_monitoring().data
        except AlertsServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self.message.setText(
            f"Monitoring analyse : {result.get('created', 0)} creee(s), {result.get('updated', 0)} mise(s) a jour.",
        )
        self._set_busy(False)
        self.load_data()
        self.data_changed.emit()

    def acknowledge_selected(self) -> None:
        """Acknowledge the selected alert through the API."""

        alert_id = self._selected_alert_id()
        if alert_id is None:
            self.message.setText("Selectionnez une alerte a acquitter.")
            return
        self._set_busy(True)
        try:
            self.alerts_service.acknowledge_alert(alert_id)
        except AlertsServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self.message.setText("Alerte acquittee.")
        self._set_busy(False)
        self.load_data()
        self.data_changed.emit()

    def resolve_selected(self) -> None:
        """Resolve the selected alert through the API."""

        alert_id = self._selected_alert_id()
        if alert_id is None:
            self.message.setText("Selectionnez une alerte a resoudre.")
            return
        self._set_busy(True)
        try:
            self.alerts_service.resolve_alert(alert_id)
        except AlertsServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self.message.setText("Alerte resolue.")
        self._set_busy(False)
        self.load_data()
        self.data_changed.emit()

    def reset_filters(self) -> None:
        """Clear all filters and reload alerts."""

        self.status_filter.setCurrentIndex(0)
        self.severity_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.source_filter.clear()
        self.search_input.clear()
        self.load_data()

    def _populate_summary(self, payload: dict[str, Any]) -> None:
        for key, label in self.cards.items():
            value = payload.get(key)
            label.setText(str(value if value is not None else 0))

    def _populate_alerts(self, result: AlertPaginatedPayload) -> None:
        rows = [
            [
                item.get("id"),
                item.get("severity"),
                item.get("status"),
                item.get("category"),
                item.get("source_type"),
                item.get("title"),
                item.get("first_seen_at"),
                item.get("last_seen_at"),
            ]
            for item in result.items
        ]
        self._populate_table(self.table, rows)

    def _selected_alert_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if item is None:
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

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

    def _combo(self, values: list[str]) -> QComboBox:
        combo = QComboBox()
        for value in values:
            combo.addItem(value or "Tous", value)
        return combo

    def _table(self, columns: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(columns))
        table.setObjectName("DataTable")
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setColumnHidden(0, True)
        return table

    def _populate_table(self, table: QTableWidget, rows: list[list[Any]]) -> None:
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if column_index == 1:
                    item.setForeground(self._severity_color(str(value)))
                table.setItem(row_index, column_index, item)

    def _severity_color(self, severity: str) -> QColor:
        if severity == "Critical":
            return QColor("#d13438")
        if severity == "Warning":
            return QColor("#f9a825")
        return QColor("#2563eb")

    def _current_filter(self, combo: QComboBox) -> str | None:
        value = combo.currentData()
        return str(value) if value else None

    def _text_filter(self, line_edit: QLineEdit) -> str | None:
        value = line_edit.text().strip()
        return value or None

    def _set_busy(self, busy: bool) -> None:
        for button in (
            self.refresh_button,
            self.refresh_from_monitoring_button,
            self.acknowledge_button,
            self.resolve_button,
            self.apply_filters_button,
            self.reset_filters_button,
        ):
            button.setEnabled(not busy)

    def set_navigation_context(self, context: dict[str, Any]) -> None:
        source = context.get("source")
        severity = context.get("severity")
        if isinstance(source, str):
            self.source_filter.setText(source)
        if isinstance(severity, str):
            index = self.severity_filter.findData(severity.title())
            if index >= 0:
                self.severity_filter.setCurrentIndex(index)
        self.load_data()

    def open_dashboard(self) -> None:
        self.navigation_requested.emit("Tableau de bord", {})

    def _error_message(self, exc: AlertsServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter les alertes."
        if exc.code == "forbidden":
            return "Acces refuse : droits administrateur requis."
        if exc.code == "validation_error":
            return "Parametres d'alertes invalides."
        if exc.code == "not_found":
            return "Alerte introuvable."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement des alertes."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant les alertes : {exc}"
