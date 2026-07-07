"""Page Google Search Console du client Desktop."""

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
from services.gsc_service import GSCIndexationResponse, GSCService, GSCServiceError, PaginatedGSCResponse


class GSCPage(QWidget):
    """Display Google Search Console data returned by the REST API."""

    PROPERTY_COLUMNS = ["ID", "URL", "Type", "Actif", "Derniere synchro", "Nom", "Permission"]
    PERFORMANCE_COLUMNS = ["Date", "Page", "Query", "Pays", "Device", "Clics", "Impressions", "CTR", "Position"]
    INDEXATION_COLUMNS = [
        "URL",
        "Coverage",
        "Google state",
        "Indexing state",
        "Verdict",
        "Issue",
        "Sitemap",
        "Dernier crawl",
    ]
    SITEMAP_COLUMNS = [
        "URL",
        "Type",
        "Pending",
        "Index",
        "Soumis",
        "Derniere lecture",
        "Warnings",
        "Errors",
        "URL count",
    ]
    IMPORT_COLUMNS = [
        "ID",
        "Propriete",
        "Type",
        "Statut",
        "Debut",
        "Fin",
        "Lignes",
        "Erreur",
        "Lance",
        "Termine",
        "Duree",
    ]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the Google Search Console page and load initial data."""

        super().__init__()
        self.gsc_service = GSCService(api_client)
        self.properties: list[dict[str, Any]] = []

        title = QLabel("Google Search Console")
        title.setObjectName("PageTitle")

        self.property_filter = QComboBox()
        self.property_filter.setMinimumWidth(260)

        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("start_date YYYY-MM-DD")

        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("end_date YYYY-MM-DD")

        self.page_url_input = QLineEdit()
        self.page_url_input.setPlaceholderText("page URL")

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("query")

        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("country")
        self.country_input.setMaximumWidth(120)

        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("device")
        self.device_input.setMaximumWidth(140)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)

        self.import_button = QPushButton("Importer maintenant")
        self.import_button.clicked.connect(self.run_manual_import)

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.properties_table = self._table(self.PROPERTY_COLUMNS)
        self.performances_table = self._table(self.PERFORMANCE_COLUMNS)
        self.indexation_table = self._table(self.INDEXATION_COLUMNS)
        self.sitemaps_table = self._table(self.SITEMAP_COLUMNS)
        self.imports_table = self._table(self.IMPORT_COLUMNS)

        self.indexation_summary = QLabel("")
        self.indexation_summary.setObjectName("PageSubtitle")

        self.tabs = QTabWidget()
        self.tabs.addTab(self.properties_table, "Proprietes")
        self.tabs.addTab(self.performances_table, "Performances")
        self.tabs.addTab(self._indexation_tab(), "Indexation")
        self.tabs.addTab(self.sitemaps_table, "Sitemaps")
        self.tabs.addTab(self.imports_table, "Historique")

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.import_button)

        filters_first_row = QHBoxLayout()
        filters_first_row.addWidget(self.property_filter)
        filters_first_row.addWidget(self.start_date_input)
        filters_first_row.addWidget(self.end_date_input)

        filters_second_row = QHBoxLayout()
        filters_second_row.addWidget(self.page_url_input)
        filters_second_row.addWidget(self.query_input)
        filters_second_row.addWidget(self.country_input)
        filters_second_row.addWidget(self.device_input)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addLayout(filters_first_row)
        layout.addLayout(filters_second_row)
        layout.addWidget(self.message)
        layout.addWidget(self.tabs, stretch=1)

        self.load_data()

    def load_data(self) -> None:
        """Load every Google Search Console section from the service."""

        self._set_busy(True)
        self.message.setText("Chargement Google Search Console...")
        try:
            properties = self.gsc_service.list_properties()
            self._populate_properties(properties)
            self._populate_performances(self.gsc_service.list_performances(**self._performance_filters()))
            self._populate_indexation(self.gsc_service.list_indexation(property_id=self._selected_property_id()))
            self._populate_sitemaps(self.gsc_service.list_sitemaps(property_id=self._selected_property_id()))
            self._populate_imports(self.gsc_service.list_imports(property_id=self._selected_property_id()))
        except GSCServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.message.setText("Donnees Google Search Console chargees.")
        finally:
            self._set_busy(False)

    def run_manual_import(self) -> None:
        """Run a manual import for the selected property through the service."""

        property_id = self._selected_property_id()
        if property_id is None:
            self.message.setText("Selectionnez une propriete avant de lancer l'import.")
            return

        start_date = self.start_date_input.text().strip()
        end_date = self.end_date_input.text().strip()
        if not start_date or not end_date:
            self.message.setText("Saisissez start_date et end_date avant de lancer l'import.")
            return

        self._set_busy(True)
        self.message.setText("Import Google Search Console en cours...")
        try:
            self.gsc_service.run_manual_import(
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                dimensions=["query", "page"],
                search_type="web",
            )
        except GSCServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate_imports(self.gsc_service.list_imports(property_id=property_id))
            self.message.setText("Import manuel lance.")
        finally:
            self._set_busy(False)

    def _populate_properties(self, result: PaginatedGSCResponse) -> None:
        self.properties = result.items
        current_property_id = self._selected_property_id()
        self.property_filter.blockSignals(True)
        self.property_filter.clear()
        self.property_filter.addItem("Toutes les proprietes", None)
        for item in self.properties:
            label = str(item.get("display_name") or item.get("property_url") or item.get("id") or "")
            self.property_filter.addItem(label, item.get("id"))
        if current_property_id is not None:
            index = self.property_filter.findData(current_property_id)
            if index >= 0:
                self.property_filter.setCurrentIndex(index)
        self.property_filter.blockSignals(False)

        rows = [
            [
                item.get("id"),
                item.get("property_url"),
                item.get("property_type"),
                item.get("is_active"),
                item.get("last_sync_at"),
                item.get("display_name"),
                item.get("permission_level"),
            ]
            for item in result.items
        ]
        self._populate_table(self.properties_table, rows)

    def _populate_performances(self, result: PaginatedGSCResponse) -> None:
        rows = [
            [
                item.get("date"),
                item.get("page"),
                item.get("query"),
                item.get("country"),
                item.get("device"),
                item.get("clicks"),
                item.get("impressions"),
                item.get("ctr"),
                item.get("position"),
            ]
            for item in result.items
        ]
        self._populate_table(self.performances_table, rows)

    def _populate_indexation(self, result: GSCIndexationResponse) -> None:
        self.indexation_summary.setText(
            "valid_pages: "
            f"{result.valid_pages} | excluded_pages: {result.excluded_pages} | "
            f"errors: {result.errors} | warnings: {result.warnings}",
        )
        rows = [
            [
                item.get("url"),
                item.get("coverage_state"),
                item.get("google_state"),
                item.get("indexing_state"),
                item.get("verdict"),
                item.get("issue_type"),
                item.get("sitemap"),
                item.get("last_crawled_at"),
            ]
            for item in result.items
        ]
        self._populate_table(self.indexation_table, rows)

    def _populate_sitemaps(self, result: PaginatedGSCResponse) -> None:
        rows = [
            [
                item.get("sitemap_url"),
                item.get("sitemap_type"),
                item.get("is_pending"),
                item.get("is_sitemaps_index"),
                item.get("submitted_at"),
                item.get("last_downloaded_at"),
                item.get("warnings"),
                item.get("errors"),
                item.get("url_count"),
            ]
            for item in result.items
        ]
        self._populate_table(self.sitemaps_table, rows)

    def _populate_imports(self, result: PaginatedGSCResponse) -> None:
        rows = [
            [
                item.get("id"),
                item.get("property_id"),
                item.get("import_type"),
                item.get("status"),
                item.get("start_date"),
                item.get("end_date"),
                item.get("rows_imported"),
                item.get("error_message"),
                item.get("started_at"),
                item.get("completed_at"),
                item.get("duration_seconds"),
            ]
            for item in result.items
        ]
        self._populate_table(self.imports_table, rows)

    def _indexation_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.indexation_summary)
        layout.addWidget(self.indexation_table)
        return widget

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

    def _performance_filters(self) -> dict[str, Any]:
        return {
            "property_id": self._selected_property_id(),
            "start_date": self._input_value(self.start_date_input),
            "end_date": self._input_value(self.end_date_input),
            "page_url": self._input_value(self.page_url_input),
            "query": self._input_value(self.query_input),
            "country": self._input_value(self.country_input),
            "device": self._input_value(self.device_input),
        }

    def _selected_property_id(self) -> int | None:
        value = self.property_filter.currentData()
        return value if isinstance(value, int) else None

    def _input_value(self, input_widget: QLineEdit) -> str | None:
        value = input_widget.text().strip()
        return value or None

    def _set_busy(self, busy: bool) -> None:
        self.refresh_button.setEnabled(not busy)
        self.import_button.setEnabled(not busy)
        self.property_filter.setEnabled(not busy)
        self.start_date_input.setEnabled(not busy)
        self.end_date_input.setEnabled(not busy)
        self.page_url_input.setEnabled(not busy)
        self.query_input.setEnabled(not busy)
        self.country_input.setEnabled(not busy)
        self.device_input.setEnabled(not busy)

    def _error_message(self, exc: GSCServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter Google Search Console."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter Google Search Console."
        if exc.code == "not_found":
            return "Ressource Google Search Console introuvable."
        if exc.code == "conflict":
            return "Action impossible dans l'etat actuel."
        if exc.code == "validation_error":
            return "Donnees invalides. Verifiez les filtres et la periode."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement Google Search Console."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant Google Search Console : {exc}"
