"""Page Bing Webmaster Tools du client Desktop."""

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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from services.bing_webmaster_tools_service import (
    BingWebmasterToolsService,
    BingWebmasterToolsServiceError,
    PaginatedBingWebmasterToolsResponse,
)


class BingWebmasterToolsPage(QWidget):
    """Display Bing Webmaster Tools data returned by the REST API."""

    CONNECTION_COLUMNS = [
        "ID",
        "Website",
        "Auth",
        "Client",
        "Actif",
        "Derniere synchro",
        "Erreur",
        "API key",
        "Token",
    ]
    SITE_COLUMNS = ["ID", "Connexion", "Website", "URL", "Verifie", "Actif", "Dernier import"]
    METRIC_COLUMNS = [
        "Date",
        "Site",
        "Import",
        "Query",
        "Page",
        "Pays",
        "Device",
        "Clics",
        "Impressions",
        "CTR",
        "Position",
    ]
    CRAWL_STAT_COLUMNS = [
        "Date",
        "Site",
        "Import",
        "URL",
        "HTTP",
        "Issue",
        "Categorie",
        "Severite",
        "Details",
    ]
    SITEMAP_COLUMNS = [
        "ID",
        "Site",
        "Import",
        "Sitemap",
        "Statut",
        "Soumis",
        "Dernier crawl",
        "URLs",
        "Erreurs",
        "Warnings",
    ]
    IMPORT_COLUMNS = [
        "ID",
        "Connexion",
        "Site",
        "Type",
        "Statut",
        "Debut",
        "Fin",
        "Items",
        "Duree",
        "Erreur",
    ]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the Bing Webmaster Tools page and load initial data."""

        super().__init__()
        self.bing_service = BingWebmasterToolsService(api_client)
        self.connections: list[dict[str, Any]] = []
        self.sites: list[dict[str, Any]] = []
        self.current_page = BingWebmasterToolsService.DEFAULT_PAGE
        self.page_size = BingWebmasterToolsService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("Bing Webmaster Tools")
        title.setObjectName("PageTitle")

        self.connection_filter = QComboBox()
        self.connection_filter.setMinimumWidth(220)

        self.site_filter = QComboBox()
        self.site_filter.setMinimumWidth(260)

        self.website_id_input = QLineEdit()
        self.website_id_input.setPlaceholderText("website_id")
        self.website_id_input.setMaximumWidth(110)

        self.date_from_input = QLineEdit()
        self.date_from_input.setPlaceholderText("date_from YYYY-MM-DD")

        self.date_to_input = QLineEdit()
        self.date_to_input.setPlaceholderText("date_to YYYY-MM-DD")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche")
        self.search_input.returnPressed.connect(self.search)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("query")

        self.page_url_input = QLineEdit()
        self.page_url_input.setPlaceholderText("page_url")

        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("country")
        self.country_input.setMaximumWidth(120)

        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("device")
        self.device_input.setMaximumWidth(140)

        self.http_status_input = QLineEdit()
        self.http_status_input.setPlaceholderText("HTTP status")
        self.http_status_input.setMaximumWidth(110)

        self.issue_type_input = QLineEdit()
        self.issue_type_input.setPlaceholderText("issue_type")

        self.severity_input = QLineEdit()
        self.severity_input.setPlaceholderText("severity")
        self.severity_input.setMaximumWidth(130)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous statuts", None)
        for status in ("PENDING", "RUNNING", "COMPLETED", "PARTIAL", "FAILED", "OK", "ERROR"):
            self.status_filter.addItem(status, status)

        self.import_type_input = QLineEdit()
        self.import_type_input.setPlaceholderText("import_type")
        self.import_type_input.setMaximumWidth(130)

        self.is_active_filter = QComboBox()
        self.is_active_filter.addItem("Tous sites", None)
        self.is_active_filter.addItem("Actifs", True)
        self.is_active_filter.addItem("Inactifs", False)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)

        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search)

        self.import_button = QPushButton("Importer maintenant")
        self.import_button.clicked.connect(self.run_manual_import)

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

        self.connections_table = self._table(self.CONNECTION_COLUMNS)
        self.sites_table = self._table(self.SITE_COLUMNS)
        self.metrics_table = self._table(self.METRIC_COLUMNS)
        self.crawl_stats_table = self._table(self.CRAWL_STAT_COLUMNS)
        self.sitemaps_table = self._table(self.SITEMAP_COLUMNS)
        self.imports_table = self._table(self.IMPORT_COLUMNS)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.connections_table, "Connexions")
        self.tabs.addTab(self.sites_table, "Sites")
        self.tabs.addTab(self.metrics_table, "Metriques")
        self.tabs.addTab(self.crawl_stats_table, "Crawl stats")
        self.tabs.addTab(self.sitemaps_table, "Sitemaps")
        self.tabs.addTab(self.imports_table, "Imports")
        self.tabs.currentChanged.connect(self.change_tab)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.import_button)

        filters_first_row = QHBoxLayout()
        filters_first_row.addWidget(self.connection_filter)
        filters_first_row.addWidget(self.site_filter)
        filters_first_row.addWidget(self.website_id_input)
        filters_first_row.addWidget(self.date_from_input)
        filters_first_row.addWidget(self.date_to_input)
        filters_first_row.addWidget(self.status_filter)
        filters_first_row.addWidget(self.is_active_filter)

        filters_second_row = QHBoxLayout()
        filters_second_row.addWidget(self.search_input)
        filters_second_row.addWidget(self.query_input)
        filters_second_row.addWidget(self.page_url_input)
        filters_second_row.addWidget(self.country_input)
        filters_second_row.addWidget(self.device_input)
        filters_second_row.addWidget(self.http_status_input)
        filters_second_row.addWidget(self.issue_type_input)
        filters_second_row.addWidget(self.severity_input)
        filters_second_row.addWidget(self.import_type_input)
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
        """Load every Bing Webmaster Tools section from the service."""

        self._set_busy(True)
        self.message.setText("Chargement Bing Webmaster Tools...")
        try:
            connections = self.bing_service.list_connections(
                page=self._page_for_tab("Connexions"),
                page_size=self.page_size,
                search=self._current_search(),
            )
            self._populate_connections(connections)
            self._populate_sites(
                self.bing_service.list_sites(
                    page=self._page_for_tab("Sites"),
                    page_size=self.page_size,
                    search=self._current_search(),
                    connection_id=self._selected_connection_id(),
                    website_id=self._optional_int(self.website_id_input),
                    is_active=self._selected_is_active(),
                ),
            )
            self._populate_metrics(
                self.bing_service.list_metrics(
                    page=self._page_for_tab("Metriques"),
                    page_size=self.page_size,
                    search=self._current_search(),
                    **self._data_filters(),
                ),
            )
            self._populate_crawl_stats(
                self.bing_service.list_crawl_stats(
                    page=self._page_for_tab("Crawl stats"),
                    page_size=self.page_size,
                    search=self._current_search(),
                    **self._crawl_stat_filters(),
                ),
            )
            self._populate_sitemaps(
                self.bing_service.list_sitemaps(
                    page=self._page_for_tab("Sitemaps"),
                    page_size=self.page_size,
                    search=self._current_search(),
                    website_id=self._optional_int(self.website_id_input),
                    bing_site_id=self._selected_site_id(),
                    status=self._selected_status(),
                ),
            )
            self._populate_imports(
                self.bing_service.list_import_runs(
                    page=self._page_for_tab("Imports"),
                    page_size=self.page_size,
                    search=self._current_search(),
                    connection_id=self._selected_connection_id(),
                    bing_site_id=self._selected_site_id(),
                    status=self._selected_status(),
                    import_type=self._input_value(self.import_type_input),
                ),
            )
        except BingWebmasterToolsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.message.setText("Donnees Bing Webmaster Tools chargees.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def search(self) -> None:
        """Restart listing from the first page with current filters."""

        self.current_page = BingWebmasterToolsService.DEFAULT_PAGE
        self.load_data()

    def change_tab(self, _index: int) -> None:
        """Reset pagination when the visible Bing tab changes."""

        self.current_page = BingWebmasterToolsService.DEFAULT_PAGE
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
        """Run a manual import for the selected connection through the service."""

        connection_id = self._selected_connection_id()
        if connection_id is None:
            self.message.setText("Selectionnez une connexion avant de lancer l'import.")
            return

        date_from = self.date_from_input.text().strip()
        date_to = self.date_to_input.text().strip()
        if not date_from or not date_to:
            self.message.setText("Saisissez date_from et date_to avant de lancer l'import.")
            return

        self._set_busy(True)
        self.message.setText("Import Bing Webmaster Tools en cours...")
        try:
            self.bing_service.run_manual_import(
                connection_id=connection_id,
                bing_site_id=self._selected_site_id(),
                date_from=date_from,
                date_to=date_to,
                import_type=self._input_value(self.import_type_input) or "MANUAL",
            )
        except BingWebmasterToolsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.current_page = BingWebmasterToolsService.DEFAULT_PAGE
            self._populate_imports(
                self.bing_service.list_import_runs(
                    page=self.current_page,
                    page_size=self.page_size,
                    connection_id=connection_id,
                    bing_site_id=self._selected_site_id(),
                    status=self._selected_status(),
                    import_type=self._input_value(self.import_type_input),
                    search=self._current_search(),
                ),
            )
            self.message.setText("Import manuel Bing Webmaster Tools lance.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def _populate_connections(self, result: PaginatedBingWebmasterToolsResponse) -> None:
        self.connections = result.items
        current_connection_id = self._selected_connection_id()
        self.connection_filter.blockSignals(True)
        self.connection_filter.clear()
        self.connection_filter.addItem("Toutes les connexions", None)
        for item in self.connections:
            label = str(item.get("client_id") or item.get("website_id") or item.get("id") or "")
            self.connection_filter.addItem(label, item.get("id"))
        if current_connection_id is not None:
            index = self.connection_filter.findData(current_connection_id)
            if index >= 0:
                self.connection_filter.setCurrentIndex(index)
        self.connection_filter.blockSignals(False)

        rows = [
            [
                item.get("id"),
                item.get("website_id"),
                item.get("auth_type"),
                item.get("client_id"),
                item.get("is_active"),
                item.get("last_sync_at"),
                item.get("last_error"),
                item.get("has_api_key"),
                item.get("has_access_token"),
            ]
            for item in result.items
        ]
        self._populate_table(self.connections_table, rows)
        self._sync_pagination("Connexions", result)

    def _populate_sites(self, result: PaginatedBingWebmasterToolsResponse) -> None:
        self.sites = result.items
        current_site_id = self._selected_site_id()
        self.site_filter.blockSignals(True)
        self.site_filter.clear()
        self.site_filter.addItem("Tous les sites Bing", None)
        for item in self.sites:
            label = str(item.get("site_url") or item.get("id") or "")
            self.site_filter.addItem(label, item.get("id"))
        if current_site_id is not None:
            index = self.site_filter.findData(current_site_id)
            if index >= 0:
                self.site_filter.setCurrentIndex(index)
        self.site_filter.blockSignals(False)

        rows = [
            [
                item.get("id"),
                item.get("connection_id"),
                item.get("website_id"),
                item.get("site_url"),
                item.get("is_verified"),
                item.get("is_active"),
                item.get("last_import_at"),
            ]
            for item in result.items
        ]
        self._populate_table(self.sites_table, rows)
        self._sync_pagination("Sites", result)

    def _populate_metrics(self, result: PaginatedBingWebmasterToolsResponse) -> None:
        rows = [
            [
                item.get("date"),
                item.get("bing_site_id"),
                item.get("import_id"),
                item.get("query"),
                item.get("page_url"),
                item.get("country"),
                item.get("device"),
                item.get("clicks"),
                item.get("impressions"),
                item.get("ctr"),
                item.get("average_position"),
            ]
            for item in result.items
        ]
        self._populate_table(self.metrics_table, rows)
        self._sync_pagination("Metriques", result)

    def _populate_crawl_stats(self, result: PaginatedBingWebmasterToolsResponse) -> None:
        rows = [
            [
                item.get("date"),
                item.get("bing_site_id"),
                item.get("import_id"),
                item.get("url"),
                item.get("http_status"),
                item.get("issue_type"),
                item.get("issue_category"),
                item.get("severity"),
                item.get("details"),
            ]
            for item in result.items
        ]
        self._populate_table(self.crawl_stats_table, rows)
        self._sync_pagination("Crawl stats", result)

    def _populate_sitemaps(self, result: PaginatedBingWebmasterToolsResponse) -> None:
        rows = [
            [
                item.get("id"),
                item.get("bing_site_id"),
                item.get("import_id"),
                item.get("sitemap_url"),
                item.get("status"),
                item.get("submitted_at"),
                item.get("last_crawled_at"),
                item.get("url_count"),
                item.get("error_count"),
                item.get("warning_count"),
            ]
            for item in result.items
        ]
        self._populate_table(self.sitemaps_table, rows)
        self._sync_pagination("Sitemaps", result)

    def _populate_imports(self, result: PaginatedBingWebmasterToolsResponse) -> None:
        rows = [
            [
                item.get("id"),
                item.get("connection_id"),
                item.get("bing_site_id"),
                item.get("import_type"),
                item.get("status"),
                item.get("started_at"),
                item.get("finished_at"),
                item.get("items_processed"),
                item.get("duration_seconds"),
                item.get("error_message"),
            ]
            for item in result.items
        ]
        self._populate_table(self.imports_table, rows)
        self._sync_pagination("Imports", result)

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

    def _data_filters(self) -> dict[str, Any]:
        return {
            "website_id": self._optional_int(self.website_id_input),
            "bing_site_id": self._selected_site_id(),
            "date_from": self._input_value(self.date_from_input),
            "date_to": self._input_value(self.date_to_input),
            "query": self._input_value(self.query_input),
            "page_url": self._input_value(self.page_url_input),
            "country": self._input_value(self.country_input),
            "device": self._input_value(self.device_input),
        }

    def _crawl_stat_filters(self) -> dict[str, Any]:
        filters = self._data_filters()
        filters.pop("query", None)
        filters.pop("page_url", None)
        filters.pop("country", None)
        filters.pop("device", None)
        filters.update(
            {
                "status": self._optional_int(self.http_status_input),
                "issue_type": self._input_value(self.issue_type_input),
                "severity": self._input_value(self.severity_input),
            },
        )
        return filters

    def _selected_connection_id(self) -> int | None:
        value = self.connection_filter.currentData()
        return value if isinstance(value, int) else None

    def _selected_site_id(self) -> int | None:
        value = self.site_filter.currentData()
        return value if isinstance(value, int) else None

    def _selected_status(self) -> str | None:
        value = self.status_filter.currentData()
        return value if isinstance(value, str) else None

    def _selected_is_active(self) -> bool | None:
        value = self.is_active_filter.currentData()
        return value if isinstance(value, bool) else None

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
        return self.current_page if self._current_tab_name() == tab_name else BingWebmasterToolsService.DEFAULT_PAGE

    def _sync_pagination(self, tab_name: str, result: PaginatedBingWebmasterToolsResponse) -> None:
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
        self.connection_filter.setEnabled(not busy)
        self.site_filter.setEnabled(not busy)
        self.website_id_input.setEnabled(not busy)
        self.date_from_input.setEnabled(not busy)
        self.date_to_input.setEnabled(not busy)
        self.search_input.setEnabled(not busy)
        self.query_input.setEnabled(not busy)
        self.page_url_input.setEnabled(not busy)
        self.country_input.setEnabled(not busy)
        self.device_input.setEnabled(not busy)
        self.http_status_input.setEnabled(not busy)
        self.issue_type_input.setEnabled(not busy)
        self.severity_input.setEnabled(not busy)
        self.status_filter.setEnabled(not busy)
        self.import_type_input.setEnabled(not busy)
        self.is_active_filter.setEnabled(not busy)

    def _update_pagination_actions(self) -> None:
        pages_label = self.total_pages if self.total_pages else 0
        self.page_label.setText(f"Page {self.current_page}/{pages_label}")
        self.previous_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.total_pages > 0 and self.current_page < self.total_pages)

    def _error_message(self, exc: BingWebmasterToolsServiceError) -> str:
        if exc.code == "bad_request":
            return "Requete Bing Webmaster Tools invalide. Verifiez les filtres."
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter Bing Webmaster Tools."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter Bing Webmaster Tools."
        if exc.code == "not_found":
            return "Ressource Bing Webmaster Tools introuvable."
        if exc.code == "conflict":
            return "Action Bing Webmaster Tools impossible dans l'etat actuel."
        if exc.code == "validation_error":
            return "Donnees Bing Webmaster Tools invalides. Verifiez les filtres et la periode."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement Bing Webmaster Tools."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant Bing Webmaster Tools : {exc}"
