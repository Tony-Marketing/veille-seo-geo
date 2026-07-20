"""Page Keywords du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from services.keywords_service import KeywordsService, KeywordsServiceError
from ui.dialogs.keyword_dialog import KeywordDialog


class KeywordsPage(QWidget):
    """Affiche et gere les mots-cles recuperes depuis l'API REST."""

    navigation_requested = Signal(str, object)
    data_changed = Signal()

    COLUMNS = ["Mot-cle", "Intention", "Priorite", "Entite"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the keywords page and load the initial data."""

        super().__init__()
        self.keywords_service = KeywordsService(api_client)
        self.keywords: list[dict[str, Any]] = []
        self.current_website: dict[str, Any] | None = None
        self.current_entity_id: int | None = None

        title = QLabel("Keywords")
        title.setObjectName("PageTitle")

        self.create_button = QPushButton("Ajouter")
        self.create_button.clicked.connect(self.create_keyword)

        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_keyword)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_keyword)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_keywords)

        self.next_button = QPushButton("Ouvrir Crawls")
        self.next_button.clicked.connect(self.open_crawls)
        self.next_button.setEnabled(False)

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
        self.table.itemDoubleClicked.connect(lambda _item: self.edit_keyword())

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.create_button)
        header_layout.addWidget(self.edit_button)
        header_layout.addWidget(self.delete_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.table)

        self.load_keywords()

    def load_keywords(self) -> None:
        """Load the paginated keywords response and update the table."""

        self._set_busy(True)
        self.message.setText("Chargement des mots-cles...")
        try:
            result = self.keywords_service.list_keywords()
            items = result.items
            total = result.total
            page = result.page
            page_size = result.page_size
            pages = result.pages
        except KeywordsServiceError as exc:
            self.keywords = []
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        except (TypeError, ValueError) as exc:
            self.keywords = []
            self.table.setRowCount(0)
            self.message.setText(f"Reponse API inattendue : {exc}")
        else:
            self._populate_table(items)
            self.message.setText(f"{total} mot(s)-cle(s) trouve(s) - page {page}/{pages} - {page_size} par page")
            if not items:
                self.message.setText("Aucun mot-cle a afficher.")
        finally:
            self._set_busy(False)

    def create_keyword(self) -> None:
        """Open the create dialog and create a keyword on confirmation."""

        dialog = KeywordDialog(parent=self, default_entity_id=self.current_entity_id)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.keywords_service.create_keyword(dialog.payload())
        except KeywordsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_keywords()
            self.message.setText("Mot-cle ajoute.")
            self.data_changed.emit()
        finally:
            self._set_busy(False)

    def edit_keyword(self) -> None:
        """Open the edit dialog for the selected keyword."""

        keyword = self._selected_keyword()
        if keyword is None:
            self.message.setText("Selectionnez un mot-cle a modifier.")
            return

        keyword_id = keyword.get("id")
        if not isinstance(keyword_id, int):
            self.message.setText("Impossible de modifier ce mot-cle : identifiant manquant.")
            return

        dialog = KeywordDialog(keyword, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.keywords_service.update_keyword(keyword_id, dialog.payload())
        except KeywordsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_keywords()
            self.message.setText("Mot-cle modifie.")
            self.data_changed.emit()
        finally:
            self._set_busy(False)

    def delete_keyword(self) -> None:
        """Delete the selected keyword after user confirmation."""

        keyword = self._selected_keyword()
        if keyword is None:
            self.message.setText("Selectionnez un mot-cle a supprimer.")
            return

        keyword_id = keyword.get("id")
        if not isinstance(keyword_id, int):
            self.message.setText("Impossible de supprimer ce mot-cle : identifiant manquant.")
            return

        term = str(keyword.get("term") or "ce mot-cle")
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Supprimer le mot-cle \"{term}\" ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        self._set_busy(True)
        try:
            self.keywords_service.delete_keyword(keyword_id)
        except KeywordsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_keywords()
            self.message.setText("Mot-cle supprime.")
            self.data_changed.emit()
        finally:
            self._set_busy(False)

    def _populate_table(self, keywords: list[dict[str, Any]]) -> None:
        """Render keywords in the table."""

        self.keywords = keywords
        self.table.setRowCount(len(keywords))
        for row, keyword in enumerate(keywords):
            values = [
                str(keyword.get("term") or ""),
                str(keyword.get("intent") or ""),
                str(keyword.get("priority") or ""),
                self._entity_label(keyword),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setData(Qt.ItemDataRole.UserRole, keyword.get("id"))
                self.table.setItem(row, column, item)
        self._update_row_actions()

    def _selected_keyword(self) -> dict[str, Any] | None:
        """Return the selected keyword from the current table row."""

        row = self.table.currentRow()
        if row < 0 or row >= len(self.keywords):
            return None
        return self.keywords[row]

    def _set_busy(self, busy: bool) -> None:
        """Enable or disable actions while an API call is running."""

        self.create_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        self.next_button.setEnabled(not busy and self.current_website is not None)
        has_selection = self._selected_keyword() is not None
        self.edit_button.setEnabled(not busy and has_selection)
        self.delete_button.setEnabled(not busy and has_selection)

    def _update_row_actions(self) -> None:
        """Enable row actions only when a keyword is selected."""

        has_selection = self._selected_keyword() is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        """Apply the Entity associated with the current Website."""

        self.current_website = website
        entity_id = website.get("entity_id") if website is not None else None
        self.current_entity_id = entity_id if isinstance(entity_id, int) else None
        self.next_button.setEnabled(website is not None)

    def open_crawls(self) -> None:
        """Continue the transverse workflow with the current Website."""

        if self.current_website is None:
            self.message.setText("Selectionnez d'abord un Website.")
            return
        self.navigation_requested.emit("Crawls", {"website": self.current_website})

    def _entity_label(self, keyword: dict[str, Any]) -> str:
        """Return a readable entity label from current or future API fields."""

        entity = keyword.get("entity")
        if isinstance(entity, dict):
            return str(entity.get("name") or entity.get("id") or "-")
        return str(keyword.get("entity_id") or "-")

    def _error_message(self, exc: KeywordsServiceError) -> str:
        """Return a readable UI message for keywords loading errors."""

        if exc.code == "unauthorized":
            return "Connexion requise pour afficher les mots-cles."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter les mots-cles."
        if exc.code == "not_found":
            return "Mot-cle introuvable. Rafraichissez la liste."
        if exc.code == "conflict":
            return "Un mot-cle avec ces informations existe deja."
        if exc.code == "validation_error":
            details = self._validation_details(exc.details)
            if details:
                return f"Donnees invalides : {details}"
            return "Donnees invalides. Verifiez les champs du formulaire."
        if exc.code == "server_error":
            return "Erreur serveur pendant la gestion des mots-cles."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion des mots-cles : {exc}"

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
