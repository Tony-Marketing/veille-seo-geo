"""Desktop page backed by existing Bing Webmaster Tools REST endpoints."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
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
from services.bing_webmaster_tools_service import BingWebmasterToolsService, BingWebmasterToolsServiceError


class BingWebmasterToolsPage(QWidget):
    """Display backend-persisted Bing data without direct external calls."""

    navigation_requested = Signal(str, object)
    data_changed = Signal()

    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.bing_service = BingWebmasterToolsService(api_client)
        self.current_website: dict[str, Any] | None = None
        self.connections: list[dict[str, Any]] = []
        self.sites: list[dict[str, Any]] = []

        title = QLabel("Bing Webmaster Tools")
        title.setObjectName("PageTitle")
        self.connection_input = QLineEdit()
        self.connection_input.setPlaceholderText("ID connexion")
        self.site_input = QLineEdit()
        self.site_input.setPlaceholderText("ID site Bing optionnel")
        self.date_from_input = QLineEdit()
        self.date_from_input.setPlaceholderText("date_from YYYY-MM-DD")
        self.date_to_input = QLineEdit()
        self.date_to_input.setPlaceholderText("date_to YYYY-MM-DD")
        self.import_button = QPushButton("Importer maintenant")
        self.import_button.clicked.connect(self.run_manual_import)
        self.reports_button = QPushButton("Ouvrir Reports")
        self.reports_button.clicked.connect(self.open_reports)
        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)
        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.connections_table = self._table(["ID", "Website", "Auth", "Actif", "Derniere synchro", "Erreur"])
        self.sites_table = self._table(["ID", "Connexion", "Website", "URL", "Verifie", "Actif"])
        self.metrics_table = self._table(["Date", "Query", "Page", "Clics", "Impressions", "CTR", "Position"])
        self.crawl_table = self._table(["Date", "URL", "HTTP", "Type", "Severite", "Details"])
        self.sitemaps_table = self._table(["URL", "Statut", "URLs", "Erreurs", "Warnings"])
        self.imports_table = self._table(["ID", "Connexion", "Site", "Type", "Statut", "Items", "Erreur"])

        tabs = QTabWidget()
        tabs.addTab(self.connections_table, "Connexions")
        tabs.addTab(self.sites_table, "Sites")
        tabs.addTab(self.metrics_table, "Metriques")
        tabs.addTab(self.crawl_table, "Crawl")
        tabs.addTab(self.sitemaps_table, "Sitemaps")
        tabs.addTab(self.imports_table, "Imports")

        header = QHBoxLayout()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.reports_button)
        header.addWidget(self.refresh_button)
        filters = QHBoxLayout()
        for widget in (
            self.connection_input,
            self.site_input,
            self.date_from_input,
            self.date_to_input,
            self.import_button,
        ):
            filters.addWidget(widget)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addLayout(filters)
        layout.addWidget(self.message)
        layout.addWidget(tabs)
        self.load_data()

    def load_data(self) -> None:
        """Load all persisted Bing sections using the current Website filter."""

        self._set_busy(True)
        self.message.setText("Chargement Bing Webmaster Tools...")
        website_id = self._website_id()
        try:
            connections = self.bing_service.list_connections()
            sites = self.bing_service.list_sites(website_id=website_id)
            metrics = self.bing_service.list_metrics(website_id=website_id)
            crawls = self.bing_service.list_crawl_stats(website_id=website_id)
            sitemaps = self.bing_service.list_sitemaps(website_id=website_id)
            imports = self.bing_service.list_import_runs(connection_id=self._optional_int(self.connection_input))
        except BingWebmasterToolsServiceError as exc:
            self._clear_tables()
            self.message.setText(self._error_message(exc))
        else:
            self.connections = connections.items
            self.sites = sites.items
            self._populate_connections(connections.items)
            self._populate_sites(sites.items)
            self._populate_metrics(metrics.items)
            self._populate_crawls(crawls.items)
            self._populate_sitemaps(sitemaps.items)
            self._populate_imports(imports.items)
            total = sites.total + metrics.total + crawls.total + sitemaps.total
            self.message.setText("Aucune donnee Bing pour ce Website." if total == 0 else "Donnees Bing chargees.")
            self._prefill_connection()
        finally:
            self._set_busy(False)

    def run_manual_import(self) -> None:
        connection_id = self._optional_int(self.connection_input)
        date_from = self.date_from_input.text().strip()
        date_to = self.date_to_input.text().strip()
        if connection_id is None or not date_from or not date_to:
            self.message.setText("Renseignez une connexion, date_from et date_to.")
            return
        self._set_busy(True)
        try:
            self.bing_service.run_manual_import(
                connection_id=connection_id,
                bing_site_id=self._optional_int(self.site_input),
                date_from=date_from,
                date_to=date_to,
            )
        except BingWebmasterToolsServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self.load_data()
        self.message.setText("Import Bing Webmaster Tools termine.")
        self.data_changed.emit()

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        self.current_website = website

    def open_reports(self) -> None:
        entity_id = self.current_website.get("entity_id") if self.current_website is not None else None
        self.navigation_requested.emit(
            "Reports",
            {"website": self.current_website, "entity_id": entity_id},
        )

    def _prefill_connection(self) -> None:
        website_id = self._website_id()
        match = next((item for item in self.connections if item.get("website_id") == website_id), None)
        if match is not None and isinstance(match.get("id"), int):
            self.connection_input.setText(str(match["id"]))
        if self.sites and isinstance(self.sites[0].get("id"), int):
            self.site_input.setText(str(self.sites[0]["id"]))

    def _populate_connections(self, items: list[dict[str, Any]]) -> None:
        self._populate(
            self.connections_table,
            [
                [
                    item.get("id"),
                    item.get("website_id"),
                    item.get("auth_type"),
                    item.get("is_active"),
                    item.get("last_sync_at"),
                    item.get("last_error"),
                ]
                for item in items
            ],
        )

    def _populate_sites(self, items: list[dict[str, Any]]) -> None:
        self._populate(
            self.sites_table,
            [
                [
                    item.get("id"),
                    item.get("connection_id"),
                    item.get("website_id"),
                    item.get("site_url"),
                    item.get("is_verified"),
                    item.get("is_active"),
                ]
                for item in items
            ],
        )

    def _populate_metrics(self, items: list[dict[str, Any]]) -> None:
        columns = ("date", "query", "page_url", "clicks", "impressions", "ctr", "average_position")
        self._populate(self.metrics_table, [[item.get(key) for key in columns] for item in items])

    def _populate_crawls(self, items: list[dict[str, Any]]) -> None:
        columns = ("date", "url", "http_status", "issue_type", "severity", "details")
        self._populate(self.crawl_table, [[item.get(key) for key in columns] for item in items])

    def _populate_sitemaps(self, items: list[dict[str, Any]]) -> None:
        columns = ("sitemap_url", "status", "url_count", "error_count", "warning_count")
        self._populate(self.sitemaps_table, [[item.get(key) for key in columns] for item in items])

    def _populate_imports(self, items: list[dict[str, Any]]) -> None:
        columns = (
            "id",
            "connection_id",
            "bing_site_id",
            "import_type",
            "status",
            "items_processed",
            "error_message",
        )
        self._populate(self.imports_table, [[item.get(key) for key in columns] for item in items])

    def _table(self, columns: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(columns))
        table.setObjectName("DataTable")
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def _populate(self, table: QTableWidget, rows: list[list[Any]]) -> None:
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                cell = QTableWidgetItem("" if value is None else str(value))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                table.setItem(row_index, column_index, cell)

    def _clear_tables(self) -> None:
        for table in (
            self.connections_table,
            self.sites_table,
            self.metrics_table,
            self.crawl_table,
            self.sitemaps_table,
            self.imports_table,
        ):
            table.setRowCount(0)

    def _website_id(self) -> int | None:
        value = self.current_website.get("id") if self.current_website is not None else None
        return value if isinstance(value, int) else None

    def _optional_int(self, widget: QLineEdit) -> int | None:
        value = widget.text().strip()
        return int(value) if value.isdigit() and int(value) > 0 else None

    def _set_busy(self, busy: bool) -> None:
        for widget in (
            self.connection_input,
            self.site_input,
            self.date_from_input,
            self.date_to_input,
            self.import_button,
            self.refresh_button,
        ):
            widget.setEnabled(not busy)

    def _error_message(self, exc: BingWebmasterToolsServiceError) -> str:
        messages = {
            "unauthorized": "Connexion requise pour Bing Webmaster Tools.",
            "forbidden": "Acces refuse a Bing Webmaster Tools.",
            "not_found": "Ressource Bing introuvable.",
            "conflict": "Action Bing impossible dans l'etat actuel.",
            "validation_error": "Parametres Bing invalides.",
            "server_error": "Erreur serveur Bing Webmaster Tools.",
            "backend_unavailable": "Backend indisponible.",
            "network_error": "Erreur reseau Bing Webmaster Tools.",
        }
        return messages.get(exc.code, f"Erreur inattendue Bing Webmaster Tools : {exc}")
