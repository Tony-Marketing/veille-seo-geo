"""Page Project Tasks du client Desktop."""

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
from services.project_tasks_service import ProjectTasksService, ProjectTasksServiceError
from ui.dialogs.project_task_dialog import ProjectTaskDialog


class ProjectTasksPage(QWidget):
    """Affiche et gere les taches projet recuperees depuis l'API REST."""

    COLUMNS = ["Titre", "Statut", "Priorite", "Entite"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the project tasks page and load the initial data."""

        super().__init__()
        self.project_tasks_service = ProjectTasksService(api_client)
        self.project_tasks: list[dict[str, Any]] = []
        self.current_page = ProjectTasksService.DEFAULT_PAGE
        self.page_size = ProjectTasksService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("Project Tasks")
        title.setObjectName("PageTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une tache")
        self.search_input.returnPressed.connect(self.search_project_tasks)

        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search_project_tasks)

        self.create_button = QPushButton("Ajouter")
        self.create_button.clicked.connect(self.create_project_task)

        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_project_task)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_project_task)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_project_tasks)

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
        self.table.itemDoubleClicked.connect(lambda _item: self.edit_project_task())

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

        self.load_project_tasks()

    def load_project_tasks(self) -> None:
        """Load the paginated project tasks response and update the table."""

        self._set_busy(True)
        self.message.setText("Chargement des taches projet...")
        try:
            result = self.project_tasks_service.list_project_tasks(
                page=self.current_page,
                page_size=self.page_size,
                search=self._current_search(),
            )
            items = result.items
            total = result.total
            page = result.page
            page_size = result.page_size
            pages = result.pages
        except ProjectTasksServiceError as exc:
            self.project_tasks = []
            self.total_pages = 0
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        except (TypeError, ValueError) as exc:
            self.project_tasks = []
            self.total_pages = 0
            self.table.setRowCount(0)
            self.message.setText(f"Reponse API inattendue : {exc}")
        else:
            self.current_page = page
            self.page_size = page_size
            self.total_pages = pages
            self._populate_table(items)
            self.message.setText(f"{total} tache(s) trouvee(s) - page {page}/{pages} - {page_size} par page")
            if not items:
                self.message.setText("Aucune tache projet a afficher.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def search_project_tasks(self) -> None:
        """Restart listing from the first page with the current search term."""

        self.current_page = ProjectTasksService.DEFAULT_PAGE
        self.load_project_tasks()

    def previous_page(self) -> None:
        """Load the previous page when available."""

        if self.current_page <= 1:
            return
        self.current_page -= 1
        self.load_project_tasks()

    def next_page(self) -> None:
        """Load the next page when available."""

        if self.total_pages and self.current_page >= self.total_pages:
            return
        self.current_page += 1
        self.load_project_tasks()

    def create_project_task(self) -> None:
        """Open the create dialog and create a project task on confirmation."""

        dialog = ProjectTaskDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.project_tasks_service.create_project_task(dialog.payload())
        except ProjectTasksServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_project_tasks()
            self.message.setText("Tache projet ajoutee.")
        finally:
            self._set_busy(False)

    def edit_project_task(self) -> None:
        """Open the edit dialog for the selected project task."""

        project_task = self._selected_project_task()
        if project_task is None:
            self.message.setText("Selectionnez une tache projet a modifier.")
            return

        project_task_id = project_task.get("id")
        if not isinstance(project_task_id, int):
            self.message.setText("Impossible de modifier cette tache projet : identifiant manquant.")
            return

        dialog = ProjectTaskDialog(project_task, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.project_tasks_service.update_project_task(project_task_id, dialog.payload())
        except ProjectTasksServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_project_tasks()
            self.message.setText("Tache projet modifiee.")
        finally:
            self._set_busy(False)

    def delete_project_task(self) -> None:
        """Delete the selected project task after user confirmation."""

        project_task = self._selected_project_task()
        if project_task is None:
            self.message.setText("Selectionnez une tache projet a supprimer.")
            return

        project_task_id = project_task.get("id")
        if not isinstance(project_task_id, int):
            self.message.setText("Impossible de supprimer cette tache projet : identifiant manquant.")
            return

        title = str(project_task.get("title") or "cette tache projet")
        confirmation = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Supprimer la tache projet \"{title}\" ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        self._set_busy(True)
        try:
            self.project_tasks_service.delete_project_task(project_task_id)
        except ProjectTasksServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_project_tasks()
            self.message.setText("Tache projet supprimee.")
        finally:
            self._set_busy(False)

    def _populate_table(self, project_tasks: list[dict[str, Any]]) -> None:
        """Render project tasks in the table."""

        self.project_tasks = project_tasks
        self.table.setRowCount(len(project_tasks))
        for row, project_task in enumerate(project_tasks):
            values = [
                str(project_task.get("title") or ""),
                str(project_task.get("status") or ""),
                str(project_task.get("priority") or ""),
                self._entity_label(project_task),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                item.setData(Qt.ItemDataRole.UserRole, project_task.get("id"))
                self.table.setItem(row, column, item)
        self._update_row_actions()

    def _selected_project_task(self) -> dict[str, Any] | None:
        """Return the selected project task from the current table row."""

        row = self.table.currentRow()
        if row < 0 or row >= len(self.project_tasks):
            return None
        return self.project_tasks[row]

    def _set_busy(self, busy: bool) -> None:
        """Enable or disable actions while an API call is running."""

        self.create_button.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.search_input.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        has_selection = self._selected_project_task() is not None
        self.edit_button.setEnabled(not busy and has_selection)
        self.delete_button.setEnabled(not busy and has_selection)
        self.previous_button.setEnabled(not busy and self.current_page > 1)
        self.next_button.setEnabled(not busy and self.total_pages > 0 and self.current_page < self.total_pages)

    def _update_row_actions(self) -> None:
        """Enable row actions only when a project task is selected."""

        has_selection = self._selected_project_task() is not None
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

    def _entity_label(self, project_task: dict[str, Any]) -> str:
        """Return a readable entity label from current or future API fields."""

        entity = project_task.get("entity")
        if isinstance(entity, dict):
            return str(entity.get("name") or entity.get("id") or "-")
        return str(project_task.get("entity_id") or "-")

    def _error_message(self, exc: ProjectTasksServiceError) -> str:
        """Return a readable UI message for project tasks errors."""

        if exc.code == "unauthorized":
            return "Connexion requise pour afficher les taches projet."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter les taches projet."
        if exc.code == "not_found":
            return "Tache projet introuvable. Rafraichissez la liste."
        if exc.code == "conflict":
            return "Une tache projet avec ces informations existe deja."
        if exc.code == "validation_error":
            details = self._validation_details(exc.details)
            if details:
                return f"Donnees invalides : {details}"
            return "Donnees invalides. Verifiez les champs du formulaire."
        if exc.code == "server_error":
            return "Erreur serveur pendant la gestion des taches projet."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion des taches projet : {exc}"

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
