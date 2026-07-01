"""Page URLs du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from services.urls_service import URLsService, URLsServiceError
from ui.dialogs.url_dialog import URLDialog


class URLsPage(QWidget):
    """Affiche et gere les URLs recuperees depuis l'API REST."""

    COLUMNS = ["URL", "Website", "Code HTTP", "Indexable"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the URLs page and load the initial data."""

        super().__init__()
        self.urls_service = URLsService(api_client)
        self.urls: list[dict[str, Any]] = []
        self.current_page = URLsService.DEFAULT_PAGE
        self.page_size = URLsService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("URLs")
        title.setObjectName("PageTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une URL")
        self.search_input.returnPressed.connect(self.search_urls)

        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search_urls)

        self.create_button = QPushButton("Ajouter")
        self.create_button.clicked.connect(self.create_url)

        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_url)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_url)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_urls)

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
        self.table.itemSelectionChanged.connect(self._update_row_actions)
        self.table.itemDoubleClicked.connect(lambda _item: self.edit_url())

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.create_button)
        header_layout.addWidget(self.edit_button)
        header_layout.addWidget(self.delete_button)
        header_layout.addWidget(self.refresh_button)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.search_button)

        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.previous_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addLayout(search_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.table)
        layout.addLayout(pagination_layout)

        self.load_urls()

    def load_urls(self) -> None:
        """Load the paginated URLs response and update the table."""

        self._set_busy(True)
        self.message.setText("Chargement des URLs...")
        try:
            result = self.urls_service.list_urls(
                page=self.current_page,
                page_size=self.page_size,
                search=self._current_search(),
            )
            items = result.items
            total = result.total
            page = result.page
            page_size = result.page_size
            pages = result.pages
        except URLsServiceError as exc:
            self.urls = []
            self.total_pages = 0
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        except (TypeError, ValueError) as exc:
            self.urls = []
            self.total_pages = 0
            self.table.setRowCount(0)
            self.message.setText(f"Reponse API inattendue : {exc}")
        else:
            self.current_page = page
            self.page_size = page_size
            self.total_pages = pages
            self._populate_table(items)
            self.message.setText(f"{total} URL(s) trouvee(s) - page {page}/{pages} - {page_size} par page")
            if not items:
                self.message.setText("Aucune URL a afficher.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def search_urls(self) -> None:
        """Restart listing from the first page with the current search term."""

        self.current_page = URLsService.DEFAULT_PAGE
        self.load_urls()

    def previous_page(self) -> None:
        """Load the previous page when available."""

        if self.current_page <= 1:
            return
        self.current_page -= 1
        self.load_urls()

    def next_page(self) -> None:
        """Load the next page when available."""

        if self.total_pages and self.current_page >= self.total_pages:
            return
        self.current_page += 1
        self.load_urls()

    def create_url(self) -> None:
        """Open the create dialog and create an URL on confirmation."""

        dialog = URLDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.urls_service.create_url(dialog.payload())
        except URLsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_urls()
            self.message.setText("URL ajoutee.")
        finally:
            self._set_busy(False)

    def edit_url(self) -> None:
        """Open the edit dialog for the selected URL."""

        url_data = self._selected_url()
        if url_data is None:
            self.message.setText("Selectionnez une URL a modifier.")
            return

        url_id = url_data.get("id")
        if not isinstance(url_id, int):
            self.message.setText("Impossible de modifier cette URL : identifiant manquant.")
            return

        dialog = URLDialog(url_data, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.urls_service.update_url(url_id, dialog.payload())
        except URLsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_urls()
            self.message.setText("URL modifiee.")
        finally:
            self._set_busy(False)

    def delete_url(self) -> None:
        """Delete the selected URL after user confirmation."""

        url_data = self._selected_url()
        if url_data is None:
            self.message.setText("Selectionnez une URL a supprimer.")
            return

        url_id = url_data.get("id")
        if not isinstance(url_id, int):
            self.message.setText("Impossible de supprimer cette URL : identifiant manquant.")
            return

        url_value = str(url_data.get("url") or "cette URL")
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Supprimer l'URL \"{url_value}\" ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        self._set_busy(True)
        try:
            self.urls_service.delete_url(url_id)
        except URLsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_urls()
            self.message.setText("URL supprimee.")
        finally:
            self._set_busy(False)

    def _populate_table(self, urls: list[dict[str, Any]]) -> None:
        """Render URLs in the table."""

        self.urls = urls
        self.table.setRowCount(len(urls))
        for row, url_data in enumerate(urls):
            values = [
                str(url_data.get("url") or ""),
                self._website_label(url_data),
                self._status_code_label(url_data),
                "Oui" if url_data.get("is_indexable") else "Non",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setData(Qt.ItemDataRole.UserRole, url_data.get("id"))
                self.table.setItem(row, column, item)
        self._update_row_actions()

    def _selected_url(self) -> dict[str, Any] | None:
        """Return the selected URL from the current table row."""

        row = self.table.currentRow()
        if row < 0 or row >= len(self.urls):
            return None
        return self.urls[row]

    def _set_busy(self, busy: bool) -> None:
        """Enable or disable actions while an API call is running."""

        self.create_button.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.search_input.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        has_selection = self._selected_url() is not None
        self.edit_button.setEnabled(not busy and has_selection)
        self.delete_button.setEnabled(not busy and has_selection)
        self.previous_button.setEnabled(not busy and self.current_page > 1)
        self.next_button.setEnabled(not busy and self.total_pages > 0 and self.current_page < self.total_pages)

    def _update_row_actions(self) -> None:
        """Enable row actions only when an URL is selected."""

        has_selection = self._selected_url() is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _update_pagination_actions(self) -> None:
        """Refresh pagination labels and actions."""

        pages_label = self.total_pages if self.total_pages else 0
        self.page_label.setText(f"Page {self.current_page}/{pages_label}")
        self.previous_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.total_pages > 0 and self.current_page < self.total_pages)

    def _current_search(self) -> str | None:
        """Return the current search text."""

        search = self.search_input.text().strip()
        return search or None

    def _website_label(self, url_data: dict[str, Any]) -> str:
        """Return a readable website label from current or future API fields."""

        website = url_data.get("website")
        if isinstance(website, dict):
            return str(website.get("name") or website.get("id") or "-")
        return str(url_data.get("website_id") or "-")

    def _status_code_label(self, url_data: dict[str, Any]) -> str:
        """Return a readable HTTP status label."""

        status_code = url_data.get("status_code")
        return "-" if status_code is None else str(status_code)

    def _error_message(self, exc: URLsServiceError) -> str:
        """Return a readable UI message for URLs loading errors."""

        if exc.code == "unauthorized":
            return "Connexion requise pour afficher les URLs."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter les URLs."
        if exc.code == "not_found":
            return "URL introuvable. Rafraichissez la liste."
        if exc.code == "conflict":
            return "Une URL avec ces informations existe deja."
        if exc.code == "validation_error":
            details = self._validation_details(exc.details)
            if details:
                return f"Donnees invalides : {details}"
            return "Donnees invalides. Verifiez les champs du formulaire."
        if exc.code == "server_error":
            return "Erreur serveur pendant la gestion des URLs."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion des URLs : {exc}"

    def _validation_details(self, details: Any) -> str:
        """Return concise validation details from a FastAPI 422 response."""

        if not isinstance(details, dict):
            return ""
        detail = details.get("detail")
        if isinstance(detail, str):
            return detail
        if not isinstance(detail, list):
            return ""

        messages: list[str] = []
        for item in detail:
            if not isinstance(item, dict):
                continue
            field = item.get("loc")
            label = field[-1] if isinstance(field, list) and field else "champ"
            message = item.get("msg") or "valeur invalide"
            messages.append(f"{label}: {message}")
        return "; ".join(messages)
