"""Page Entities du client Desktop."""

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
from services.entities_service import EntitiesService, EntitiesServiceError
from ui.dialogs.entity_dialog import EntityDialog


class EntitiesPage(QWidget):
    """Affiche et gere les entites recuperees depuis l'API REST."""

    COLUMNS = ["Nom", "Description", "Actif"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the entities page and load the initial data."""

        super().__init__()
        self.entities_service = EntitiesService(api_client)
        self.entities: list[dict[str, Any]] = []

        title = QLabel("Entities")
        title.setObjectName("PageTitle")

        self.create_button = QPushButton("Ajouter")
        self.create_button.clicked.connect(self.create_entity)

        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_entity)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_entity)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_entities)

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
        self.table.itemDoubleClicked.connect(lambda _item: self.edit_entity())

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

        self.load_entities()

    def load_entities(self) -> None:
        """Load the paginated entities response and update the table."""

        self._set_busy(True)
        self.message.setText("Chargement des entites...")
        try:
            result = self.entities_service.list_entities()
            items = result.items
            total = result.total
            page = result.page
            page_size = result.page_size
            pages = result.pages
        except EntitiesServiceError as exc:
            self.entities = []
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        except (TypeError, ValueError) as exc:
            self.entities = []
            self.table.setRowCount(0)
            self.message.setText(f"Reponse API inattendue : {exc}")
        else:
            self._populate_table(items)
            self.message.setText(f"{total} entite(s) trouvee(s) - page {page}/{pages} - {page_size} par page")
            if not items:
                self.message.setText("Aucune entite a afficher.")
        finally:
            self._set_busy(False)

    def create_entity(self) -> None:
        """Open the create dialog and create an entity on confirmation."""

        dialog = EntityDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.entities_service.create_entity(dialog.payload())
        except EntitiesServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_entities()
            self.message.setText("Entite ajoutee.")
        finally:
            self._set_busy(False)

    def edit_entity(self) -> None:
        """Open the edit dialog for the selected entity."""

        entity = self._selected_entity()
        if entity is None:
            self.message.setText("Selectionnez une entite a modifier.")
            return

        entity_id = entity.get("id")
        if not isinstance(entity_id, int):
            self.message.setText("Impossible de modifier cette entite : identifiant manquant.")
            return

        dialog = EntityDialog(entity, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.entities_service.update_entity(entity_id, dialog.payload())
        except EntitiesServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_entities()
            self.message.setText("Entite modifiee.")
        finally:
            self._set_busy(False)

    def delete_entity(self) -> None:
        """Delete the selected entity after user confirmation."""

        entity = self._selected_entity()
        if entity is None:
            self.message.setText("Selectionnez une entite a supprimer.")
            return

        entity_id = entity.get("id")
        if not isinstance(entity_id, int):
            self.message.setText("Impossible de supprimer cette entite : identifiant manquant.")
            return

        name = str(entity.get("name") or "cette entite")
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Supprimer l'entite \"{name}\" ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        self._set_busy(True)
        try:
            self.entities_service.delete_entity(entity_id)
        except EntitiesServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_entities()
            self.message.setText("Entite supprimee.")
        finally:
            self._set_busy(False)

    def _populate_table(self, entities: list[dict[str, Any]]) -> None:
        """Render entities in the table."""

        self.entities = entities
        self.table.setRowCount(len(entities))
        for row, entity in enumerate(entities):
            values = [
                str(entity.get("name") or ""),
                str(entity.get("description") or ""),
                "Oui" if entity.get("is_active") else "Non",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setData(Qt.ItemDataRole.UserRole, entity.get("id"))
                self.table.setItem(row, column, item)
        self._update_row_actions()

    def _selected_entity(self) -> dict[str, Any] | None:
        """Return the selected entity from the current table row."""

        row = self.table.currentRow()
        if row < 0 or row >= len(self.entities):
            return None
        return self.entities[row]

    def _set_busy(self, busy: bool) -> None:
        """Enable or disable actions while an API call is running."""

        self.create_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        has_selection = self._selected_entity() is not None
        self.edit_button.setEnabled(not busy and has_selection)
        self.delete_button.setEnabled(not busy and has_selection)

    def _update_row_actions(self) -> None:
        """Enable row actions only when an entity is selected."""

        has_selection = self._selected_entity() is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _error_message(self, exc: EntitiesServiceError) -> str:
        """Return a readable UI message for entities loading errors."""

        if exc.code == "unauthorized":
            return "Connexion requise pour afficher les entites."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter les entites."
        if exc.code == "not_found":
            return "Entite introuvable. Rafraichissez la liste."
        if exc.code == "conflict":
            return "Une entite avec ce nom existe deja."
        if exc.code == "validation_error":
            details = self._validation_details(exc.details)
            if details:
                return f"Donnees invalides : {details}"
            return "Donnees invalides. Verifiez les champs du formulaire."
        if exc.code == "server_error":
            return "Erreur serveur pendant la gestion des entites."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion des entites : {exc}"

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
