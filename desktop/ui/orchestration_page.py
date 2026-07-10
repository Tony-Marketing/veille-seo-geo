"""Page Orchestrateur du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt
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
from services.orchestration_service import (
    OrchestrationPaginatedPayload,
    OrchestrationService,
    OrchestrationServiceError,
)


class OrchestrationPage(QWidget):
    """Display processing orchestration data returned by the REST API."""

    COLUMNS = [
        "ID",
        "Type",
        "Statut",
        "Planification",
        "Tentatives",
        "Disponible",
        "Debut",
        "Fin",
        "Worker",
        "Message",
    ]
    LOG_COLUMNS = ["Niveau", "Evenement", "Message", "Date"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the orchestration page."""

        super().__init__()
        self.orchestration_service = OrchestrationService(api_client)

        title = QLabel("Orchestrateur")
        title.setObjectName("PageTitle")

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)
        self.run_scheduler_button = QPushButton("Cycle scheduler")
        self.run_scheduler_button.clicked.connect(self.run_scheduler_once)
        self.retry_button = QPushButton("Relancer")
        self.retry_button.clicked.connect(self.retry_selected)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.cancel_selected)

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.cards: dict[str, QLabel] = {}
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        for index, (key, label) in enumerate(
            [
                ("pending", "En attente"),
                ("running", "En cours"),
                ("retry_scheduled", "Retries"),
                ("succeeded", "Reussis"),
                ("failed", "Erreurs"),
                ("cancelled", "Annules"),
                ("blocked", "Bloques"),
                ("active_workers", "Workers"),
            ],
        ):
            card = self._card(label)
            self.cards[key] = card.findChild(QLabel, "CardValue") or QLabel("-")
            cards_layout.addWidget(card, index // 4, index % 4)

        self.status_filter = self._combo(
            ["", "pending", "reserved", "running", "retry_scheduled", "succeeded", "failed"],
        )
        self.type_filter = self._combo(["", "gsc", "ga4", "bing", "crawl", "seo_analysis", "geo_analysis"])
        self.schedule_filter = QLineEdit()
        self.schedule_filter.setPlaceholderText("Planification ID")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche")
        self.apply_filters_button = QPushButton("Filtrer")
        self.apply_filters_button.clicked.connect(self.load_data)
        self.reset_filters_button = QPushButton("Reinitialiser")
        self.reset_filters_button.clicked.connect(self.reset_filters)

        self.jobs_table = self._table(self.COLUMNS)
        self.jobs_table.itemSelectionChanged.connect(self.load_selected_logs)
        self.logs_table = self._table(self.LOG_COLUMNS)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.run_scheduler_button)
        header_layout.addWidget(self.refresh_button)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Statut"))
        filters_layout.addWidget(self.status_filter)
        filters_layout.addWidget(QLabel("Type"))
        filters_layout.addWidget(self.type_filter)
        filters_layout.addWidget(self.schedule_filter)
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.apply_filters_button)
        filters_layout.addWidget(self.reset_filters_button)

        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        actions_layout.addWidget(self.retry_button)
        actions_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(self.message)
        layout.addLayout(cards_layout)
        layout.addLayout(filters_layout)
        layout.addWidget(self._section("Jobs", self.jobs_table), stretch=2)
        layout.addWidget(self._section("Journal", self.logs_table), stretch=1)
        layout.addLayout(actions_layout)

        self.load_data()

    def load_data(self) -> None:
        """Load orchestration summary and jobs through the Desktop service."""

        self._set_busy(True)
        self.message.setText("Chargement de l'orchestrateur...")
        try:
            summary = self.orchestration_service.get_summary().data
            jobs = self.orchestration_service.list_jobs(
                status=self._current_filter(self.status_filter),
                job_type=self._current_filter(self.type_filter),
                schedule_id=self._schedule_filter(),
                search=self._text_filter(self.search_input),
            )
        except OrchestrationServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate_summary(summary)
            self._populate_jobs(jobs)
            self.message.setText("Orchestrateur a jour.")
        finally:
            self._set_busy(False)

    def load_selected_logs(self) -> None:
        """Load logs for the selected job."""

        job_id = self._selected_job_id()
        if job_id is None:
            self.logs_table.setRowCount(0)
            return
        try:
            logs = self.orchestration_service.list_job_logs(job_id)
        except OrchestrationServiceError as exc:
            self.message.setText(self._error_message(exc))
            return
        rows = [
            [item.get("level"), item.get("event"), item.get("message"), item.get("created_at")]
            for item in logs.items
        ]
        self._populate_table(self.logs_table, rows)

    def run_scheduler_once(self) -> None:
        """Run one scheduler cycle through the API."""

        self._set_busy(True)
        try:
            result = self.orchestration_service.run_scheduler_once().data
        except OrchestrationServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self.message.setText(
            f"Cycle termine : {result.get('created', 0)} cree(s), {result.get('skipped', 0)} ignore(s).",
        )
        self._set_busy(False)
        self.load_data()

    def retry_selected(self) -> None:
        """Retry the selected job through the API."""

        job_id = self._selected_job_id()
        if job_id is None:
            self.message.setText("Selectionnez un job a relancer.")
            return
        self._set_busy(True)
        try:
            self.orchestration_service.retry_job(job_id)
        except OrchestrationServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self.message.setText("Relance planifiee.")
        self._set_busy(False)
        self.load_data()

    def cancel_selected(self) -> None:
        """Cancel the selected job through the API."""

        job_id = self._selected_job_id()
        if job_id is None:
            self.message.setText("Selectionnez un job a annuler.")
            return
        self._set_busy(True)
        try:
            self.orchestration_service.cancel_job(job_id)
        except OrchestrationServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self.message.setText("Job annule.")
        self._set_busy(False)
        self.load_data()

    def reset_filters(self) -> None:
        """Clear filters and reload jobs."""

        self.status_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.schedule_filter.clear()
        self.search_input.clear()
        self.load_data()

    def _populate_summary(self, payload: dict[str, Any]) -> None:
        for key, label in self.cards.items():
            value = payload.get(key)
            label.setText(str(value if value is not None else 0))

    def _populate_jobs(self, result: OrchestrationPaginatedPayload) -> None:
        rows = [
            [
                item.get("id"),
                item.get("job_type"),
                item.get("status"),
                item.get("schedule_id"),
                f"{item.get('attempts', 0)}/{item.get('max_attempts', 0)}",
                item.get("available_at"),
                item.get("started_at"),
                item.get("finished_at"),
                item.get("worker_id"),
                item.get("message"),
            ]
            for item in result.items
        ]
        self._populate_table(self.jobs_table, rows)

    def _selected_job_id(self) -> int | None:
        row = self.jobs_table.currentRow()
        if row < 0:
            return None
        item = self.jobs_table.item(row, 0)
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
        if columns == self.COLUMNS:
            table.setColumnHidden(0, True)
        return table

    def _populate_table(self, table: QTableWidget, rows: list[list[Any]]) -> None:
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if table is self.jobs_table and column_index == 2:
                    item.setForeground(self._status_color(str(value)))
                table.setItem(row_index, column_index, item)

    def _status_color(self, value: str) -> QColor:
        if value == "failed":
            return QColor("#d13438")
        if value in {"retry_scheduled", "cancelled"}:
            return QColor("#f9a825")
        if value == "succeeded":
            return QColor("#107c10")
        return QColor("#2563eb")

    def _current_filter(self, combo: QComboBox) -> str | None:
        value = combo.currentData()
        return str(value) if value else None

    def _text_filter(self, line_edit: QLineEdit) -> str | None:
        value = line_edit.text().strip()
        return value or None

    def _schedule_filter(self) -> int | None:
        value = self.schedule_filter.text().strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def _set_busy(self, busy: bool) -> None:
        for button in (
            self.refresh_button,
            self.run_scheduler_button,
            self.retry_button,
            self.cancel_button,
            self.apply_filters_button,
            self.reset_filters_button,
        ):
            button.setEnabled(not busy)

    def _error_message(self, exc: OrchestrationServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter l'orchestrateur."
        if exc.code == "forbidden":
            return "Acces refuse : droits administrateur requis."
        if exc.code == "validation_error":
            return "Parametres d'orchestration invalides."
        if exc.code == "not_found":
            return "Job introuvable."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement de l'orchestrateur."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant l'orchestration : {exc}"
