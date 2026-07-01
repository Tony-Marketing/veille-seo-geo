"""Page Websites du client Desktop."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt
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
from services.websites_service import WebsitesService, WebsitesServiceError
from ui.dialogs.website_dialog import WebsiteDialog


class WebsitesPage(QWidget):
    """Affiche et gere les sites recuperes depuis l'API REST."""

    COLUMNS = ["Nom", "URL", "Actif", "Entité"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the websites page and load the initial data."""

        super().__init__()
        self.websites_service = WebsitesService(api_client)
        self.websites: list[dict[str, Any]] = []

        title = QLabel("Websites")
        title.setObjectName("PageTitle")

        self.create_button = QPushButton("Ajouter")
        self.create_button.clicked.connect(self.create_website)

        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_website)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_website)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.clicked.connect(self.load_websites)

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
        self.table.itemDoubleClicked.connect(lambda _item: self.edit_website())

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.create_button)
        header_layout.addWidget(self.edit_button)
        header_layout.addWidget(self.delete_button)
        header_layout.addWidget(self.refresh_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.table)

        self.load_websites()

    def load_websites(self) -> None:
        """Load the paginated websites response and update the table."""

        self._set_busy(True)
        self.message.setText("Chargement des sites...")
        try:
            result = self.websites_service.list_websites()
            items = result.items
            total = result.total
            page = result.page
            page_size = result.page_size
            pages = result.pages
        except WebsitesServiceError as exc:
            self.websites = []
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        except (TypeError, ValueError) as exc:
            self.websites = []
            self.table.setRowCount(0)
            self.message.setText(f"Réponse API inattendue : {exc}")
        else:
            self._populate_table(items)
            self.message.setText(f"{total} site(s) trouvé(s) - page {page}/{pages} - {page_size} par page")
            if not items:
                self.message.setText("Aucun site web a afficher.")
        finally:
            self._set_busy(False)

    def create_website(self) -> None:
        """Open the create dialog and create a website on confirmation."""

        dialog = WebsiteDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.websites_service.create_website(dialog.payload())
        except WebsitesServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_websites()
            self.message.setText("Site ajoute.")
        finally:
            self._set_busy(False)

    def edit_website(self) -> None:
        """Open the edit dialog for the selected website."""

        website = self._selected_website()
        if website is None:
            self.message.setText("Selectionnez un site a modifier.")
            return

        website_id = website.get("id")
        if not isinstance(website_id, int):
            self.message.setText("Impossible de modifier ce site : identifiant manquant.")
            return

        dialog = WebsiteDialog(website, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.websites_service.update_website(website_id, dialog.payload())
        except WebsitesServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_websites()
            self.message.setText("Site modifie.")
        finally:
            self._set_busy(False)

    def delete_website(self) -> None:
        """Delete the selected website after user confirmation."""

        website = self._selected_website()
        if website is None:
            self.message.setText("Selectionnez un site a supprimer.")
            return

        website_id = website.get("id")
        if not isinstance(website_id, int):
            self.message.setText("Impossible de supprimer ce site : identifiant manquant.")
            return

        name = str(website.get("name") or "ce site")
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Supprimer le site \"{name}\" ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        self._set_busy(True)
        try:
            self.websites_service.delete_website(website_id)
        except WebsitesServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_websites()
            self.message.setText("Site supprime.")
        finally:
            self._set_busy(False)

    def _populate_table(self, websites: list[dict[str, Any]]) -> None:
        """Render websites in the table."""

        self.websites = websites
        self.table.setRowCount(len(websites))
        for row, website in enumerate(websites):
            values = [
                str(website.get("name") or ""),
                str(website.get("url") or ""),
                "Oui" if website.get("is_active") else "Non",
                self._entity_label(website),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setData(Qt.ItemDataRole.UserRole, website.get("id"))
                self.table.setItem(row, column, item)
        self._update_row_actions()

    def _selected_website(self) -> dict[str, Any] | None:
        """Return the selected website from the current table row."""

        row = self.table.currentRow()
        if row < 0 or row >= len(self.websites):
            return None
        return self.websites[row]

    def _set_busy(self, busy: bool) -> None:
        """Enable or disable actions while an API call is running."""

        self.create_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        has_selection = self._selected_website() is not None
        self.edit_button.setEnabled(not busy and has_selection)
        self.delete_button.setEnabled(not busy and has_selection)

    def _update_row_actions(self) -> None:
        """Enable row actions only when a website is selected."""

        has_selection = self._selected_website() is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _entity_label(self, website: dict[str, Any]) -> str:
        """Return a readable entity label from current or future API fields."""

        entity = website.get("entity")
        if isinstance(entity, dict):
            return str(entity.get("name") or entity.get("id") or "-")
        return str(website.get("entity_id") or "-")

    def _error_message(self, exc: WebsitesServiceError) -> str:
        """Return a readable UI message for websites loading errors."""

        if exc.code == "unauthorized":
            return "Connexion requise pour afficher les sites."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter les sites."
        if exc.code == "not_found":
            return "Site introuvable. Rafraichissez la liste."
        if exc.code == "conflict":
            return "Un site avec cette URL existe deja."
        if exc.code == "validation_error":
            details = self._validation_details(exc.details)
            if details:
                return f"Donnees invalides : {details}"
            return "Donnees invalides. Verifiez les champs du formulaire."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion des sites : {exc}"

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
