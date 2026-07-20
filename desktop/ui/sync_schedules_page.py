"""Page Desktop des planifications de synchronisation."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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
from services.sync_schedules_service import (
    PaginatedSyncSchedulesResponse,
    SyncSchedulesService,
    SyncSchedulesServiceError,
)


class SyncSchedulesPage(QWidget):
    """Display synchronization schedules returned by the REST API."""

    COLUMNS = [
        "ID",
        "Nom",
        "Type",
        "Frequence",
        "Statut",
        "Actif",
        "Site",
        "Target ID",
        "Target type",
        "Derniere execution",
        "Prochaine execution",
        "Message",
    ]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the synchronization schedules page."""

        super().__init__()
        self.sync_schedules_service = SyncSchedulesService(api_client)
        self.current_page = SyncSchedulesService.DEFAULT_PAGE
        self.page_size = SyncSchedulesService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("Planifications")
        title.setObjectName("PageTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche")
        self.search_input.returnPressed.connect(self.search)

        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous types", None)
        for sync_type in ("GSC", "GA4", "Bing", "Crawl", "SEO", "GEO"):
            self.type_filter.addItem(sync_type, sync_type)

        self.frequency_filter = QComboBox()
        self.frequency_filter.addItem("Toutes frequences", None)
        for frequency in ("Manuel", "Horaire", "Quotidien", "Hebdomadaire", "Mensuel"):
            self.frequency_filter.addItem(frequency, frequency)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous statuts", None)
        for status in ("Active", "Desactivee", "En attente", "Erreur"):
            self.status_filter.addItem(status, status)

        self.active_filter = QComboBox()
        self.active_filter.addItem("Tous etats", None)
        self.active_filter.addItem("Actives", True)
        self.active_filter.addItem("Desactivees", False)

        self.website_id_input = QLineEdit()
        self.website_id_input.setPlaceholderText("website_id")
        self.website_id_input.setMaximumWidth(120)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom")

        self.form_type = QComboBox()
        for sync_type in ("GSC", "GA4", "Bing", "Crawl", "SEO", "GEO"):
            self.form_type.addItem(sync_type, sync_type)

        self.form_frequency = QComboBox()
        for frequency in ("Manuel", "Horaire", "Quotidien", "Hebdomadaire", "Mensuel"):
            self.form_frequency.addItem(frequency, frequency)

        self.target_id_input = QLineEdit()
        self.target_id_input.setPlaceholderText("target_id")

        self.target_type_input = QLineEdit()
        self.target_type_input.setPlaceholderText("target_type")

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)

        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search)

        self.create_button = QPushButton("Creer")
        self.create_button.clicked.connect(self.create_schedule)

        self.update_button = QPushButton("Enregistrer")
        self.update_button.clicked.connect(self.update_selected)

        self.enable_button = QPushButton("Activer")
        self.enable_button.clicked.connect(self.enable_selected)

        self.disable_button = QPushButton("Desactiver")
        self.disable_button.clicked.connect(self.disable_selected)

        self.previous_button = QPushButton("Precedent")
        self.previous_button.clicked.connect(self.previous_page)
        self.previous_button.setEnabled(False)

        self.next_button = QPushButton("Suivant")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)

        self.page_label = QLabel("Page -/-")
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
        self.table.itemSelectionChanged.connect(self.populate_form_from_selection)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.enable_button)
        header_layout.addWidget(self.disable_button)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.type_filter)
        filters_layout.addWidget(self.frequency_filter)
        filters_layout.addWidget(self.status_filter)
        filters_layout.addWidget(self.active_filter)
        filters_layout.addWidget(self.website_id_input)
        filters_layout.addWidget(self.search_button)

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.form_type)
        form_layout.addWidget(self.form_frequency)
        form_layout.addWidget(self.target_id_input)
        form_layout.addWidget(self.target_type_input)
        form_layout.addWidget(self.create_button)
        form_layout.addWidget(self.update_button)

        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.previous_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addLayout(filters_layout)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.table, stretch=1)
        layout.addLayout(pagination_layout)

        self.load_data()

    def load_data(self) -> None:
        """Load synchronization schedules from the service."""

        self._set_busy(True)
        self.message.setText("Chargement des planifications...")
        try:
            result = self.sync_schedules_service.list_schedules(
                page=self.current_page,
                page_size=self.page_size,
                search=self._input_value(self.search_input),
                sync_type=self._combo_value(self.type_filter),
                frequency=self._combo_value(self.frequency_filter),
                status=self._combo_value(self.status_filter),
                is_active=self.active_filter.currentData(),
                website_id=self._optional_int(self.website_id_input),
            )
        except SyncSchedulesServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate(result)
            self.message.setText("Planifications chargees.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def search(self) -> None:
        """Restart listing from the first page with current filters."""

        self.current_page = SyncSchedulesService.DEFAULT_PAGE
        self.load_data()

    def previous_page(self) -> None:
        """Load the previous page when available."""

        if self.current_page <= 1:
            return
        self.current_page -= 1
        self.load_data()

    def next_page(self) -> None:
        """Load the next page when available."""

        if self.total_pages and self.current_page >= self.total_pages:
            return
        self.current_page += 1
        self.load_data()

    def enable_selected(self) -> None:
        """Enable the selected schedule through the REST API."""

        schedule_id = self._selected_schedule_id()
        if schedule_id is None:
            self.message.setText("Selectionnez une planification.")
            return
        self._run_action(lambda: self.sync_schedules_service.enable_schedule(schedule_id))

    def create_schedule(self) -> None:
        """Create a schedule through the REST API."""

        payload = self._form_payload(require_name=True)
        if payload is None:
            return
        self._run_action(lambda: self.sync_schedules_service.create_schedule(payload))

    def update_selected(self) -> None:
        """Update the selected schedule through the REST API."""

        schedule_id = self._selected_schedule_id()
        if schedule_id is None:
            self.message.setText("Selectionnez une planification.")
            return
        payload = self._form_payload(require_name=False)
        if payload is None:
            return
        self._run_action(lambda: self.sync_schedules_service.update_schedule(schedule_id, payload))

    def disable_selected(self) -> None:
        """Disable the selected schedule through the REST API."""

        schedule_id = self._selected_schedule_id()
        if schedule_id is None:
            self.message.setText("Selectionnez une planification.")
            return
        self._run_action(lambda: self.sync_schedules_service.disable_schedule(schedule_id))

    def _run_action(self, action: Any) -> None:
        self._set_busy(True)
        try:
            action()
        except SyncSchedulesServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_data()
        finally:
            self._set_busy(False)

    def _populate(self, result: PaginatedSyncSchedulesResponse) -> None:
        rows = [
            [
                item.get("id"),
                item.get("name"),
                item.get("sync_type"),
                item.get("frequency"),
                item.get("status"),
                item.get("is_active"),
                item.get("website_id"),
                item.get("target_id"),
                item.get("target_type"),
                item.get("last_run_at"),
                item.get("next_run_at"),
                item.get("last_run_message"),
            ]
            for item in result.items
        ]
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row_index, column_index, item)
        self.current_page = result.page
        self.page_size = result.page_size
        self.total_pages = result.pages

    def _selected_schedule_id(self) -> int | None:
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

    def populate_form_from_selection(self) -> None:
        """Fill edition fields from the selected table row."""

        row = self.table.currentRow()
        if row < 0:
            return
        self.name_input.setText(self._table_text(row, 1))
        self._select_combo_value(self.form_type, self._table_text(row, 2))
        self._select_combo_value(self.form_frequency, self._table_text(row, 3))
        self.target_id_input.setText(self._table_text(row, 7))
        self.target_type_input.setText(self._table_text(row, 8))

    def _form_payload(self, *, require_name: bool) -> dict[str, Any] | None:
        name = self._input_value(self.name_input)
        if require_name and name is None:
            self.message.setText("Saisissez un nom de planification.")
            return None
        payload: dict[str, Any] = {
            "sync_type": self._combo_value(self.form_type),
            "frequency": self._combo_value(self.form_frequency),
        }
        if name is not None:
            payload["name"] = name
        target_id = self._input_value(self.target_id_input)
        if target_id is not None:
            payload["target_id"] = target_id
        target_type = self._input_value(self.target_type_input)
        if target_type is not None:
            payload["target_type"] = target_type
        return payload

    def _set_busy(self, busy: bool) -> None:
        self.refresh_button.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.create_button.setEnabled(not busy)
        self.update_button.setEnabled(not busy)
        self.enable_button.setEnabled(not busy)
        self.disable_button.setEnabled(not busy)
        self.previous_button.setEnabled(not busy and self.current_page > 1)
        self.next_button.setEnabled(not busy and self.total_pages > 0 and self.current_page < self.total_pages)
        self.search_input.setEnabled(not busy)
        self.type_filter.setEnabled(not busy)
        self.frequency_filter.setEnabled(not busy)
        self.status_filter.setEnabled(not busy)
        self.active_filter.setEnabled(not busy)
        self.website_id_input.setEnabled(not busy)
        self.name_input.setEnabled(not busy)
        self.form_type.setEnabled(not busy)
        self.form_frequency.setEnabled(not busy)
        self.target_id_input.setEnabled(not busy)
        self.target_type_input.setEnabled(not busy)

    def _update_pagination_actions(self) -> None:
        pages_label = self.total_pages if self.total_pages else 0
        self.page_label.setText(f"Page {self.current_page}/{pages_label}")
        self.previous_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.total_pages > 0 and self.current_page < self.total_pages)

    def _combo_value(self, combo: QComboBox) -> str | None:
        value = combo.currentData()
        return value if isinstance(value, str) else None

    def _select_combo_value(self, combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _table_text(self, row: int, column: int) -> str:
        item = self.table.item(row, column)
        return item.text() if item is not None else ""

    def _input_value(self, input_widget: QLineEdit) -> str | None:
        value = input_widget.text().strip()
        return value or None

    def _optional_int(self, input_widget: QLineEdit) -> int | None:
        value = input_widget.text().strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        """Apply the Website filter already supported by the schedules API."""

        website_id = website.get("id") if website is not None else None
        self.website_id_input.setText(str(website_id) if isinstance(website_id, int) else "")

    def _error_message(self, exc: SyncSchedulesServiceError) -> str:
        if exc.code == "bad_request":
            return "Requete de planification invalide."
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter les planifications."
        if exc.code == "forbidden":
            return "Acces refuse : droits administrateur requis."
        if exc.code == "not_found":
            return "Planification introuvable."
        if exc.code == "conflict":
            return "Action impossible dans l'etat actuel de la planification."
        if exc.code == "validation_error":
            return "Donnees de planification invalides."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement des planifications."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant les planifications : {exc}"
