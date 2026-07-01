"""Page Competitors du client Desktop."""

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
from services.competitors_service import CompetitorsService, CompetitorsServiceError
from ui.dialogs.competitor_dialog import CompetitorDialog


class CompetitorsPage(QWidget):
    """Affiche et gere les concurrents recuperes depuis l'API REST."""

    COLUMNS = ["Nom", "URL du site", "Entite", "Actif"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the competitors page and load the initial data."""

        super().__init__()
        self.competitors_service = CompetitorsService(api_client)
        self.competitors: list[dict[str, Any]] = []

        title = QLabel("Competitors")
        title.setObjectName("PageTitle")

        self.create_button = QPushButton("Ajouter")
        self.create_button.clicked.connect(self.create_competitor)

        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_competitor)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_competitor)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_competitors)

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
        self.table.itemDoubleClicked.connect(lambda _item: self.edit_competitor())

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

        self.load_competitors()

    def load_competitors(self) -> None:
        """Load the paginated competitors response and update the table."""

        self._set_busy(True)
        self.message.setText("Chargement des concurrents...")
        try:
            result = self.competitors_service.list_competitors()
            items = result.items
            total = result.total
            page = result.page
            page_size = result.page_size
            pages = result.pages
        except CompetitorsServiceError as exc:
            self.competitors = []
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        except (TypeError, ValueError) as exc:
            self.competitors = []
            self.table.setRowCount(0)
            self.message.setText(f"Reponse API inattendue : {exc}")
        else:
            self._populate_table(items)
            self.message.setText(f"{total} concurrent(s) trouve(s) - page {page}/{pages} - {page_size} par page")
            if not items:
                self.message.setText("Aucun concurrent a afficher.")
        finally:
            self._set_busy(False)

    def create_competitor(self) -> None:
        """Open the create dialog and create a competitor on confirmation."""

        dialog = CompetitorDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.competitors_service.create_competitor(dialog.payload())
        except CompetitorsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_competitors()
            self.message.setText("Concurrent ajoute.")
        finally:
            self._set_busy(False)

    def edit_competitor(self) -> None:
        """Open the edit dialog for the selected competitor."""

        competitor = self._selected_competitor()
        if competitor is None:
            self.message.setText("Selectionnez un concurrent a modifier.")
            return

        competitor_id = competitor.get("id")
        if not isinstance(competitor_id, int):
            self.message.setText("Impossible de modifier ce concurrent : identifiant manquant.")
            return

        dialog = CompetitorDialog(competitor, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.competitors_service.update_competitor(competitor_id, dialog.payload())
        except CompetitorsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_competitors()
            self.message.setText("Concurrent modifie.")
        finally:
            self._set_busy(False)

    def delete_competitor(self) -> None:
        """Delete the selected competitor after user confirmation."""

        competitor = self._selected_competitor()
        if competitor is None:
            self.message.setText("Selectionnez un concurrent a supprimer.")
            return

        competitor_id = competitor.get("id")
        if not isinstance(competitor_id, int):
            self.message.setText("Impossible de supprimer ce concurrent : identifiant manquant.")
            return

        name = str(competitor.get("name") or "ce concurrent")
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Supprimer le concurrent \"{name}\" ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        self._set_busy(True)
        try:
            self.competitors_service.delete_competitor(competitor_id)
        except CompetitorsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_competitors()
            self.message.setText("Concurrent supprime.")
        finally:
            self._set_busy(False)

    def _populate_table(self, competitors: list[dict[str, Any]]) -> None:
        """Render competitors in the table."""

        self.competitors = competitors
        self.table.setRowCount(len(competitors))
        for row, competitor in enumerate(competitors):
            values = [
                str(competitor.get("name") or ""),
                str(competitor.get("website_url") or ""),
                self._entity_label(competitor),
                "Oui" if competitor.get("is_active") else "Non",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setData(Qt.ItemDataRole.UserRole, competitor.get("id"))
                self.table.setItem(row, column, item)
        self._update_row_actions()

    def _selected_competitor(self) -> dict[str, Any] | None:
        """Return the selected competitor from the current table row."""

        row = self.table.currentRow()
        if row < 0 or row >= len(self.competitors):
            return None
        return self.competitors[row]

    def _set_busy(self, busy: bool) -> None:
        """Enable or disable actions while an API call is running."""

        self.create_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        has_selection = self._selected_competitor() is not None
        self.edit_button.setEnabled(not busy and has_selection)
        self.delete_button.setEnabled(not busy and has_selection)

    def _update_row_actions(self) -> None:
        """Enable row actions only when a competitor is selected."""

        has_selection = self._selected_competitor() is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _entity_label(self, competitor: dict[str, Any]) -> str:
        """Return a readable entity label from current or future API fields."""

        entity = competitor.get("entity")
        if isinstance(entity, dict):
            return str(entity.get("name") or entity.get("id") or "-")
        return str(competitor.get("entity_id") or "-")

    def _error_message(self, exc: CompetitorsServiceError) -> str:
        """Return a readable UI message for competitors loading errors."""

        if exc.code == "unauthorized":
            return "Connexion requise pour afficher les concurrents."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter les concurrents."
        if exc.code == "not_found":
            return "Concurrent introuvable. Rafraichissez la liste."
        if exc.code == "conflict":
            return "Un concurrent avec ces informations existe deja."
        if exc.code == "validation_error":
            details = self._validation_details(exc.details)
            if details:
                return f"Donnees invalides : {details}"
            return "Donnees invalides. Verifiez les champs du formulaire."
        if exc.code == "server_error":
            return "Erreur serveur pendant la gestion des concurrents."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion des concurrents : {exc}"

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
