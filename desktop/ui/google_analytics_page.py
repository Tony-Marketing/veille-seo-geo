"""Page Google Analytics 4 du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from services.google_analytics_service import (
    GoogleAnalyticsBreakdownPayload,
    GoogleAnalyticsService,
    GoogleAnalyticsServiceError,
    GoogleAnalyticsSummaryPayload,
    PaginatedGoogleAnalyticsResponse,
)


class GoogleAnalyticsPage(QWidget):
    """Display Google Analytics 4 data returned by the REST API."""

    navigation_requested = Signal(str, object)
    data_changed = Signal()

    PROPERTY_COLUMNS = ["ID", "Site", "Property ID", "Nom", "Compte", "Measurement", "Actif", "Token expire"]
    OVERVIEW_COLUMNS = [
        "Rows",
        "Sessions",
        "Users",
        "New users",
        "Engaged",
        "Views",
        "Avg duration",
        "Engagement rate",
        "Conversions",
        "Revenue",
    ]
    METRIC_COLUMNS = [
        "Date",
        "Propriete",
        "Import",
        "Source",
        "Medium",
        "Campagne",
        "Device",
        "Pays",
        "Users",
        "New users",
        "Sessions",
        "Engaged",
        "Views",
        "Avg duration",
        "Engagement rate",
        "Conversions",
        "Revenue",
    ]
    BREAKDOWN_COLUMNS = [
        "Dimension",
        "Rows",
        "Sessions",
        "Users",
        "New users",
        "Engaged",
        "Views",
        "Avg duration",
        "Engagement rate",
        "Conversions",
        "Revenue",
    ]
    HISTORY_COLUMNS = [
        "ID",
        "Propriete",
        "Nom",
        "GA4",
        "Statut",
        "Lignes",
        "Debut",
        "Fin",
        "Duree",
        "Erreur",
    ]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the Google Analytics page and load initial data."""

        super().__init__()
        self.google_analytics_service = GoogleAnalyticsService(api_client)
        self.current_website: dict[str, Any] | None = None
        self.properties: list[dict[str, Any]] = []
        self.current_page = GoogleAnalyticsService.DEFAULT_PAGE
        self.page_size = GoogleAnalyticsService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("Google Analytics 4")
        title.setObjectName("PageTitle")

        self.property_filter = QComboBox()
        self.property_filter.setMinimumWidth(260)

        self.website_id_input = QLineEdit()
        self.website_id_input.setPlaceholderText("website_id")
        self.website_id_input.setMaximumWidth(110)

        self.date_from_input = QLineEdit()
        self.date_from_input.setPlaceholderText("date_from YYYY-MM-DD")

        self.date_to_input = QLineEdit()
        self.date_to_input.setPlaceholderText("date_to YYYY-MM-DD")

        self.import_id_input = QLineEdit()
        self.import_id_input.setPlaceholderText("import_id")
        self.import_id_input.setMaximumWidth(110)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche")
        self.search_input.returnPressed.connect(self.search)

        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("source")

        self.medium_input = QLineEdit()
        self.medium_input.setPlaceholderText("medium")

        self.campaign_input = QLineEdit()
        self.campaign_input.setPlaceholderText("campaign")

        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("device_category")

        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("country")
        self.country_input.setMaximumWidth(130)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous statuts", None)
        for status in ("PENDING", "RUNNING", "COMPLETED", "PARTIAL", "FAILED"):
            self.status_filter.addItem(status, status)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)

        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search)

        self.import_button = QPushButton("Importer maintenant")
        self.import_button.clicked.connect(self.run_manual_import)

        self.bing_button = QPushButton("Ouvrir Bing Webmaster Tools")
        self.bing_button.clicked.connect(self.open_bing)

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

        self.properties_table = self._table(self.PROPERTY_COLUMNS)
        self.overview_table = self._table(self.OVERVIEW_COLUMNS)
        self.metrics_table = self._table(self.METRIC_COLUMNS)
        self.traffic_table = self._table(self.BREAKDOWN_COLUMNS)
        self.acquisition_table = self._table(self.BREAKDOWN_COLUMNS)
        self.engagement_table = self._table(self.BREAKDOWN_COLUMNS)
        self.conversions_table = self._table(self.BREAKDOWN_COLUMNS)
        self.revenue_table = self._table(self.BREAKDOWN_COLUMNS)
        self.history_table = self._table(self.HISTORY_COLUMNS)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.properties_table, "Proprietes")
        self.tabs.addTab(self.overview_table, "Overview")
        self.tabs.addTab(self.metrics_table, "Metrics")
        self.tabs.addTab(self.traffic_table, "Traffic")
        self.tabs.addTab(self.acquisition_table, "Acquisition")
        self.tabs.addTab(self.engagement_table, "Engagement")
        self.tabs.addTab(self.conversions_table, "Conversions")
        self.tabs.addTab(self.revenue_table, "Revenue")
        self.tabs.addTab(self.history_table, "History")
        self.tabs.currentChanged.connect(self.change_tab)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.import_button)
        header_layout.addWidget(self.bing_button)

        filters_first_row = QHBoxLayout()
        filters_first_row.addWidget(self.property_filter)
        filters_first_row.addWidget(self.website_id_input)
        filters_first_row.addWidget(self.date_from_input)
        filters_first_row.addWidget(self.date_to_input)
        filters_first_row.addWidget(self.import_id_input)
        filters_first_row.addWidget(self.status_filter)

        filters_second_row = QHBoxLayout()
        filters_second_row.addWidget(self.search_input)
        filters_second_row.addWidget(self.source_input)
        filters_second_row.addWidget(self.medium_input)
        filters_second_row.addWidget(self.campaign_input)
        filters_second_row.addWidget(self.device_input)
        filters_second_row.addWidget(self.country_input)
        filters_second_row.addWidget(self.search_button)

        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.previous_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addLayout(filters_first_row)
        layout.addLayout(filters_second_row)
        layout.addWidget(self.message)
        layout.addWidget(self.tabs, stretch=1)
        layout.addLayout(pagination_layout)

        self.load_data()

    def load_data(self) -> None:
        """Load every Google Analytics section from the service."""

        self._set_busy(True)
        self.message.setText("Chargement Google Analytics 4...")
        try:
            properties = self.google_analytics_service.list_properties(
                page=self._page_for_tab("Proprietes"),
                page_size=self.page_size,
                search=self._current_search(),
            )
            self._populate_properties(properties)
            self._populate_overview(self.google_analytics_service.overview(**self._metric_filters()))
            self._populate_metrics(
                self.google_analytics_service.list_metrics(
                    page=self._page_for_tab("Metrics"),
                    page_size=self.page_size,
                    search=self._current_search(),
                    **self._metric_filters(),
                ),
            )
            self._populate_breakdown(
                self.traffic_table,
                self.google_analytics_service.traffic(**self._metric_filters()),
            )
            self._populate_breakdown(
                self.acquisition_table,
                self.google_analytics_service.acquisition(**self._metric_filters()),
            )
            self._populate_breakdown(
                self.engagement_table,
                self.google_analytics_service.engagement(**self._metric_filters()),
            )
            self._populate_breakdown(
                self.conversions_table,
                self.google_analytics_service.conversions(**self._metric_filters()),
            )
            self._populate_breakdown(
                self.revenue_table,
                self.google_analytics_service.revenue(**self._metric_filters()),
            )
            self._populate_history(
                self.google_analytics_service.history(
                    page=self._page_for_tab("History"),
                    page_size=self.page_size,
                    search=self._current_search(),
                    property_id=self._selected_property_id(),
                    status=self._selected_status(),
                ),
            )
        except GoogleAnalyticsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.message.setText("Donnees Google Analytics 4 chargees.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def search(self) -> None:
        """Restart listing from the first page with current filters."""

        self.current_page = GoogleAnalyticsService.DEFAULT_PAGE
        self.load_data()

    def change_tab(self, _index: int) -> None:
        """Reset pagination when the visible Google Analytics tab changes."""

        self.current_page = GoogleAnalyticsService.DEFAULT_PAGE
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

    def run_manual_import(self) -> None:
        """Run a manual import for the selected property through the service."""

        property_id = self._selected_property_id()
        if property_id is None:
            self.message.setText("Selectionnez une propriete avant de lancer l'import.")
            return

        start_date = self.date_from_input.text().strip()
        end_date = self.date_to_input.text().strip()
        if not start_date or not end_date:
            self.message.setText("Saisissez date_from et date_to avant de lancer l'import.")
            return

        self._set_busy(True)
        self.message.setText("Import Google Analytics 4 en cours...")
        try:
            self.google_analytics_service.run_manual_import(
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
            )
        except GoogleAnalyticsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.current_page = GoogleAnalyticsService.DEFAULT_PAGE
            self._populate_history(
                self.google_analytics_service.history(
                    page=self.current_page,
                    page_size=self.page_size,
                    property_id=property_id,
                    status=self._selected_status(),
                    search=self._current_search(),
                ),
            )
            self.message.setText("Import manuel Google Analytics 4 lance.")
            self.data_changed.emit()
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def _populate_properties(self, result: PaginatedGoogleAnalyticsResponse) -> None:
        self.properties = result.items
        current_property_id = self._selected_property_id()
        self.property_filter.blockSignals(True)
        self.property_filter.clear()
        self.property_filter.addItem("Toutes les proprietes", None)
        for item in self.properties:
            label = str(item.get("property_name") or item.get("property_id") or item.get("id") or "")
            self.property_filter.addItem(label, item.get("id"))
        if current_property_id is not None:
            index = self.property_filter.findData(current_property_id)
            if index >= 0:
                self.property_filter.setCurrentIndex(index)
        website_id = self.current_website.get("id") if self.current_website is not None else None
        if isinstance(website_id, int):
            match = next((item.get("id") for item in result.items if item.get("website_id") == website_id), None)
            index = self.property_filter.findData(match)
            if index >= 0:
                self.property_filter.setCurrentIndex(index)
        self.property_filter.blockSignals(False)

        rows = [
            [
                item.get("id"),
                item.get("website_id"),
                item.get("property_id"),
                item.get("property_name"),
                item.get("account_name"),
                item.get("measurement_id"),
                item.get("enabled"),
                item.get("token_expires_at"),
            ]
            for item in result.items
        ]
        self._populate_table(self.properties_table, rows)
        self._sync_pagination("Proprietes", result)

    def _populate_overview(self, result: GoogleAnalyticsSummaryPayload) -> None:
        data = result.data
        self._populate_table(
            self.overview_table,
            [
                [
                    data.get("rows"),
                    data.get("sessions"),
                    data.get("users"),
                    data.get("new_users"),
                    data.get("engaged_sessions"),
                    data.get("screen_page_views"),
                    data.get("average_session_duration"),
                    data.get("engagement_rate"),
                    data.get("conversions"),
                    data.get("total_revenue"),
                ],
            ],
        )

    def _populate_metrics(self, result: PaginatedGoogleAnalyticsResponse) -> None:
        rows = [
            [
                item.get("date"),
                item.get("property_id"),
                item.get("import_id"),
                item.get("source"),
                item.get("medium"),
                item.get("campaign"),
                item.get("device_category"),
                item.get("country"),
                item.get("users"),
                item.get("new_users"),
                item.get("sessions"),
                item.get("engaged_sessions"),
                item.get("screen_page_views"),
                item.get("average_session_duration"),
                item.get("engagement_rate"),
                item.get("conversions"),
                item.get("total_revenue"),
            ]
            for item in result.items
        ]
        self._populate_table(self.metrics_table, rows)
        self._sync_pagination("Metrics", result)

    def _populate_breakdown(self, table: QTableWidget, result: GoogleAnalyticsBreakdownPayload) -> None:
        rows = [
            [
                item.get("dimension"),
                item.get("rows"),
                item.get("sessions"),
                item.get("users"),
                item.get("new_users"),
                item.get("engaged_sessions"),
                item.get("screen_page_views"),
                item.get("average_session_duration"),
                item.get("engagement_rate"),
                item.get("conversions"),
                item.get("total_revenue"),
            ]
            for item in result.data
        ]
        self._populate_table(table, rows)

    def _populate_history(self, result: PaginatedGoogleAnalyticsResponse) -> None:
        rows = [
            [
                item.get("id"),
                item.get("property_id"),
                item.get("property_name"),
                item.get("google_property_id"),
                item.get("status"),
                item.get("imported_rows"),
                item.get("started_at"),
                item.get("finished_at"),
                item.get("duration_seconds"),
                item.get("error_message"),
            ]
            for item in result.items
        ]
        self._populate_table(self.history_table, rows)
        self._sync_pagination("History", result)

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

    def _metric_filters(self) -> dict[str, Any]:
        return {
            "website_id": self._optional_int(self.website_id_input),
            "property_id": self._selected_property_id(),
            "date_from": self._input_value(self.date_from_input),
            "date_to": self._input_value(self.date_to_input),
            "import_id": self._optional_int(self.import_id_input),
            "source": self._input_value(self.source_input),
            "medium": self._input_value(self.medium_input),
            "campaign": self._input_value(self.campaign_input),
            "device_category": self._input_value(self.device_input),
            "country": self._input_value(self.country_input),
        }

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        self.current_website = website
        website_id = website.get("id") if website is not None else None
        self.website_id_input.setText(str(website_id) if isinstance(website_id, int) else "")

    def open_bing(self) -> None:
        self.navigation_requested.emit("Bing Webmaster Tools", {"website": self.current_website})

    def _selected_property_id(self) -> int | None:
        value = self.property_filter.currentData()
        return value if isinstance(value, int) else None

    def _selected_status(self) -> str | None:
        value = self.status_filter.currentData()
        return value if isinstance(value, str) else None

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

    def _current_search(self) -> str | None:
        return self._input_value(self.search_input)

    def _current_tab_name(self) -> str:
        return self.tabs.tabText(self.tabs.currentIndex())

    def _page_for_tab(self, tab_name: str) -> int:
        return self.current_page if self._current_tab_name() == tab_name else GoogleAnalyticsService.DEFAULT_PAGE

    def _sync_pagination(self, tab_name: str, result: PaginatedGoogleAnalyticsResponse) -> None:
        if self._current_tab_name() != tab_name:
            return
        self.current_page = result.page
        self.page_size = result.page_size
        self.total_pages = result.pages

    def _set_busy(self, busy: bool) -> None:
        self.refresh_button.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.import_button.setEnabled(not busy)
        self.previous_button.setEnabled(not busy and self.current_page > 1)
        self.next_button.setEnabled(not busy and self.total_pages > 0 and self.current_page < self.total_pages)
        self.property_filter.setEnabled(not busy)
        self.website_id_input.setEnabled(not busy)
        self.date_from_input.setEnabled(not busy)
        self.date_to_input.setEnabled(not busy)
        self.import_id_input.setEnabled(not busy)
        self.status_filter.setEnabled(not busy)
        self.search_input.setEnabled(not busy)
        self.source_input.setEnabled(not busy)
        self.medium_input.setEnabled(not busy)
        self.campaign_input.setEnabled(not busy)
        self.device_input.setEnabled(not busy)
        self.country_input.setEnabled(not busy)

    def _update_pagination_actions(self) -> None:
        if self._current_tab_name() not in {"Proprietes", "Metrics", "History"}:
            self.total_pages = 0
            self.page_label.setText("Page -/-")
            self.previous_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
        pages_label = self.total_pages if self.total_pages else 0
        self.page_label.setText(f"Page {self.current_page}/{pages_label}")
        self.previous_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.total_pages > 0 and self.current_page < self.total_pages)

    def _error_message(self, exc: GoogleAnalyticsServiceError) -> str:
        if exc.code == "bad_request":
            return "Requete Google Analytics invalide. Verifiez les filtres."
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter Google Analytics 4."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter Google Analytics 4."
        if exc.code == "not_found":
            return "Ressource Google Analytics 4 introuvable."
        if exc.code == "conflict":
            return "Action Google Analytics 4 impossible dans l'etat actuel."
        if exc.code == "validation_error":
            return "Donnees Google Analytics 4 invalides. Verifiez les filtres et la periode."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement Google Analytics 4."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant Google Analytics 4 : {exc}"
