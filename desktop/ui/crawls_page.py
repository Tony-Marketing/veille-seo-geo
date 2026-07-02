"""Page Crawls du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
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
from services.crawls_service import CrawlsService, CrawlsServiceError
from ui.dialogs.crawl_dialog import CrawlDialog


class CrawlsPage(QWidget):
    """Display and manage crawl sessions through the REST API."""

    SESSION_COLUMNS = ["URL", "Statut", "Progression", "Pages", "Profondeur"]
    PAGE_COLUMNS = ["URL", "Statut HTTP", "Profondeur", "Type", "Erreur"]

    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.crawls_service = CrawlsService(api_client)
        self.crawls: list[dict[str, Any]] = []
        self.pages: list[dict[str, Any]] = []
        self.current_page = CrawlsService.DEFAULT_PAGE
        self.page_size = CrawlsService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("Crawls")
        title.setObjectName("PageTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une session")
        self.search_input.returnPressed.connect(self.search_crawls)

        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search_crawls)

        self.create_button = QPushButton("Creer")
        self.create_button.clicked.connect(self.create_crawl)

        self.start_button = QPushButton("Lancer")
        self.start_button.clicked.connect(self.start_crawl)
        self.start_button.setEnabled(False)

        self.cancel_button = QPushButton("Arreter")
        self.cancel_button.clicked.connect(self.cancel_crawl)
        self.cancel_button.setEnabled(False)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_crawls)

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.sessions_table = QTableWidget(0, len(self.SESSION_COLUMNS))
        self.sessions_table.setObjectName("DataTable")
        self.sessions_table.setHorizontalHeaderLabels(self.SESSION_COLUMNS)
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sessions_table.verticalHeader().setVisible(False)
        self.sessions_table.setAlternatingRowColors(True)
        self.sessions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sessions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sessions_table.itemSelectionChanged.connect(self._on_session_selected)

        pages_label = QLabel("Pages decouvertes")
        pages_label.setObjectName("PageSubtitle")

        self.pages_table = QTableWidget(0, len(self.PAGE_COLUMNS))
        self.pages_table.setObjectName("DataTable")
        self.pages_table.setHorizontalHeaderLabels(self.PAGE_COLUMNS)
        self.pages_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pages_table.verticalHeader().setVisible(False)
        self.pages_table.setAlternatingRowColors(True)
        self.pages_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pages_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.create_button)
        header_layout.addWidget(self.start_button)
        header_layout.addWidget(self.cancel_button)
        header_layout.addWidget(self.refresh_button)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.search_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addLayout(search_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.sessions_table, stretch=2)
        layout.addWidget(pages_label)
        layout.addWidget(self.pages_table, stretch=1)

        self.load_crawls()

    def load_crawls(self) -> None:
        """Load crawl sessions and update the table."""

        self._set_busy(True)
        self.message.setText("Chargement des crawls...")
        try:
            result = self.crawls_service.list_crawls(
                page=self.current_page,
                page_size=self.page_size,
                search=self._current_search(),
            )
        except CrawlsServiceError as exc:
            self.crawls = []
            self.sessions_table.setRowCount(0)
            self.pages_table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        else:
            self.current_page = result.page
            self.page_size = result.page_size
            self.total_pages = result.pages
            self._populate_sessions(result.items)
            self.message.setText(f"{result.total} crawl(s) trouve(s).")
            if not result.items:
                self.message.setText("Aucun crawl a afficher.")
        finally:
            self._set_busy(False)

    def search_crawls(self) -> None:
        """Restart listing from the first page with the current search term."""

        self.current_page = CrawlsService.DEFAULT_PAGE
        self.load_crawls()

    def create_crawl(self) -> None:
        """Open the create dialog and create a crawl on confirmation."""

        dialog = CrawlDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._set_busy(True)
        try:
            self.crawls_service.create_crawl(dialog.payload())
        except CrawlsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_crawls()
            self.message.setText("Crawl cree.")
        finally:
            self._set_busy(False)

    def start_crawl(self) -> None:
        """Start the selected crawl session."""

        crawl = self._selected_crawl()
        if crawl is None:
            self.message.setText("Selectionnez un crawl a lancer.")
            return
        crawl_id = crawl.get("id")
        if not isinstance(crawl_id, int):
            self.message.setText("Identifiant de crawl manquant.")
            return
        self._set_busy(True)
        self.message.setText("Crawl en cours...")
        try:
            self.crawls_service.start_crawl(crawl_id)
        except CrawlsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_crawls()
            self.load_pages(crawl_id)
            self.message.setText("Crawl termine ou arrete.")
        finally:
            self._set_busy(False)

    def cancel_crawl(self) -> None:
        """Request cancellation for the selected crawl."""

        crawl = self._selected_crawl()
        if crawl is None:
            self.message.setText("Selectionnez un crawl a arreter.")
            return
        crawl_id = crawl.get("id")
        if not isinstance(crawl_id, int):
            self.message.setText("Identifiant de crawl manquant.")
            return
        self._set_busy(True)
        try:
            self.crawls_service.cancel_crawl(crawl_id)
        except CrawlsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_crawls()
            self.message.setText("Demande d'arret envoyee.")
        finally:
            self._set_busy(False)

    def load_pages(self, crawl_id: int) -> None:
        """Load pages for one crawl session."""

        try:
            result = self.crawls_service.list_crawl_pages(crawl_id)
        except CrawlsServiceError as exc:
            self.pages = []
            self.pages_table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        else:
            self._populate_pages(result.items)

    def _populate_sessions(self, crawls: list[dict[str, Any]]) -> None:
        self.crawls = crawls
        self.sessions_table.setRowCount(len(crawls))
        for row, crawl in enumerate(crawls):
            values = [
                str(crawl.get("start_url") or ""),
                str(crawl.get("status") or ""),
                self._progress_label(crawl),
                str(crawl.get("pages_found") or 0),
                f"{crawl.get('max_depth_reached') or 0}/{crawl.get('max_depth') or 0}",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setData(Qt.ItemDataRole.UserRole, crawl.get("id"))
                self.sessions_table.setItem(row, column, item)
        self._update_actions()

    def _populate_pages(self, pages: list[dict[str, Any]]) -> None:
        self.pages = pages
        self.pages_table.setRowCount(len(pages))
        for row, page in enumerate(pages):
            values = [
                str(page.get("url") or ""),
                str(page.get("status_code") or "-"),
                str(page.get("depth") or 0),
                str(page.get("content_type") or ""),
                str(page.get("error_message") or ""),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.pages_table.setItem(row, column, item)

    def _on_session_selected(self) -> None:
        self._update_actions()
        crawl = self._selected_crawl()
        if crawl is None:
            return
        crawl_id = crawl.get("id")
        if isinstance(crawl_id, int):
            self.load_pages(crawl_id)

    def _selected_crawl(self) -> dict[str, Any] | None:
        row = self.sessions_table.currentRow()
        if row < 0 or row >= len(self.crawls):
            return None
        return self.crawls[row]

    def _set_busy(self, busy: bool) -> None:
        self.create_button.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.search_input.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        self._update_actions(disabled=busy)

    def _update_actions(self, *, disabled: bool = False) -> None:
        crawl = self._selected_crawl()
        if disabled or crawl is None:
            self.start_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            return
        status = str(crawl.get("status") or "")
        self.start_button.setEnabled(status in {"PENDING", "FAILED", "CANCELLED"})
        self.cancel_button.setEnabled(status in {"PENDING", "RUNNING"})

    def _current_search(self) -> str | None:
        search = self.search_input.text().strip()
        return search or None

    def _progress_label(self, crawl: dict[str, Any]) -> str:
        crawled = int(crawl.get("pages_crawled") or 0)
        found = int(crawl.get("pages_found") or 0)
        failed = int(crawl.get("pages_failed") or 0)
        return f"{crawled}/{found} traitees, {failed} erreur(s)"

    def _error_message(self, exc: CrawlsServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour gerer les crawls."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de gerer les crawls."
        if exc.code == "not_found":
            return "Crawl introuvable. Rafraichissez la liste."
        if exc.code == "conflict":
            return "Action impossible dans l'etat actuel du crawl."
        if exc.code == "validation_error":
            return "Donnees invalides. Verifiez l'URL, le site, la profondeur et le nombre de pages."
        if exc.code == "server_error":
            return "Erreur serveur pendant la gestion des crawls."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion des crawls : {exc}"

