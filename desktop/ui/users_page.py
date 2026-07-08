"""Page de gestion des utilisateurs du client Desktop."""

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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from services.users_service import PaginatedUsersResponse, UsersService, UsersServiceError
from ui.dialogs.user_dialog import UserDialog


class UsersPage(QWidget):
    """Display and manage users, roles and permissions returned by the REST API."""

    USER_COLUMNS = ["ID", "Email", "Nom", "Actif", "Super admin", "Roles"]
    ROLE_COLUMNS = ["ID", "Nom", "Systeme", "Permissions", "Description"]
    PERMISSION_COLUMNS = ["ID", "Code", "Module", "Libelle", "Description"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the users page and load initial data."""

        super().__init__()
        self.users_service = UsersService(api_client)
        self.users: list[dict[str, Any]] = []
        self.roles: list[dict[str, Any]] = []
        self.permissions: list[dict[str, Any]] = []
        self.current_page = UsersService.DEFAULT_PAGE
        self.page_size = UsersService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("Gestion utilisateurs")
        title.setObjectName("PageTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un utilisateur")
        self.search_input.returnPressed.connect(self.search_users)

        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search_users)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)

        self.create_button = QPushButton("Ajouter")
        self.create_button.clicked.connect(self.create_user)

        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_user)
        self.edit_button.setEnabled(False)

        self.toggle_active_button = QPushButton("Activer / desactiver")
        self.toggle_active_button.clicked.connect(self.toggle_user_active)
        self.toggle_active_button.setEnabled(False)

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

        self.users_table = self._table(self.USER_COLUMNS)
        self.users_table.itemSelectionChanged.connect(self._update_row_actions)
        self.users_table.itemDoubleClicked.connect(lambda _item: self.edit_user())
        self.roles_table = self._table(self.ROLE_COLUMNS)
        self.permissions_table = self._table(self.PERMISSION_COLUMNS)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.users_table, "Utilisateurs")
        self.tabs.addTab(self.roles_table, "Roles")
        self.tabs.addTab(self.permissions_table, "Permissions")
        self.tabs.currentChanged.connect(lambda _index: self._update_pagination_actions())

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.create_button)
        header_layout.addWidget(self.edit_button)
        header_layout.addWidget(self.toggle_active_button)
        header_layout.addWidget(self.refresh_button)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
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
        layout.addWidget(self.tabs, stretch=1)
        layout.addLayout(pagination_layout)

        self.load_data()

    def load_data(self) -> None:
        """Load users, roles and permissions from the Desktop service."""

        self._set_busy(True)
        self.message.setText("Chargement des utilisateurs...")
        try:
            roles = self.users_service.list_roles()
            permissions = self.users_service.list_permissions()
            users = self.users_service.list_users(
                page=self.current_page,
                page_size=self.page_size,
                search=self._current_search(),
                sort="email",
                order="asc",
            )
        except UsersServiceError as exc:
            self.users = []
            self.roles = []
            self.permissions = []
            self.users_table.setRowCount(0)
            self.roles_table.setRowCount(0)
            self.permissions_table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        else:
            self._populate_roles(roles.items)
            self._populate_permissions(permissions.items)
            self._populate_users(users)
            self.message.setText(
                f"{users.total} utilisateur(s) trouve(s) - page {users.page}/{users.pages} - "
                f"{users.page_size} par page",
            )
            if not users.items:
                self.message.setText("Aucun utilisateur a afficher.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def search_users(self) -> None:
        """Restart users listing from the first page with the current search."""

        self.current_page = UsersService.DEFAULT_PAGE
        self.load_data()

    def previous_page(self) -> None:
        """Load the previous users page when available."""

        if self.current_page <= 1:
            return
        self.current_page -= 1
        self.load_data()

    def next_page(self) -> None:
        """Load the next users page when available."""

        if self.total_pages and self.current_page >= self.total_pages:
            return
        self.current_page += 1
        self.load_data()

    def create_user(self) -> None:
        """Open the create dialog and create a user on confirmation."""

        dialog = UserDialog(roles=self.roles, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.users_service.create_user(dialog.payload())
        except UsersServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.current_page = UsersService.DEFAULT_PAGE
            self.load_data()
            self.message.setText("Utilisateur cree.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def edit_user(self) -> None:
        """Open the edit dialog for the selected user."""

        user = self._selected_user()
        if user is None:
            self.message.setText("Selectionnez un utilisateur a modifier.")
            return

        user_id = user.get("id")
        if not isinstance(user_id, int):
            self.message.setText("Impossible de modifier cet utilisateur : identifiant manquant.")
            return

        dialog = UserDialog(user, roles=self.roles, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._set_busy(True)
        try:
            self.users_service.update_user(user_id, dialog.payload())
        except UsersServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_data()
            self.message.setText("Utilisateur modifie.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def toggle_user_active(self) -> None:
        """Activate or deactivate the selected user through the service."""

        user = self._selected_user()
        if user is None:
            self.message.setText("Selectionnez un utilisateur.")
            return

        user_id = user.get("id")
        if not isinstance(user_id, int):
            self.message.setText("Impossible de modifier cet utilisateur : identifiant manquant.")
            return

        next_state = not bool(user.get("is_active"))
        self._set_busy(True)
        try:
            self.users_service.set_user_active(user_id, next_state)
        except UsersServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_data()
            self.message.setText("Utilisateur active." if next_state else "Utilisateur desactive.")
        finally:
            self._set_busy(False)
            self._update_pagination_actions()

    def _populate_users(self, result: PaginatedUsersResponse) -> None:
        self.users = result.items
        self.current_page = result.page
        self.page_size = result.page_size
        self.total_pages = result.pages

        rows = [
            [
                user.get("id"),
                user.get("email"),
                self._full_name(user),
                "Oui" if user.get("is_active") else "Non",
                "Oui" if user.get("is_superadmin") else "Non",
                self._roles_label(user),
            ]
            for user in self.users
        ]
        self._populate_table(self.users_table, rows)
        self._update_row_actions()

    def _populate_roles(self, roles: list[dict[str, Any]]) -> None:
        self.roles = roles
        rows = [
            [
                role.get("id"),
                role.get("name"),
                "Oui" if role.get("is_system") else "Non",
                self._permissions_count(role),
                role.get("description"),
            ]
            for role in roles
        ]
        self._populate_table(self.roles_table, rows)

    def _populate_permissions(self, permissions: list[dict[str, Any]]) -> None:
        self.permissions = permissions
        rows = [
            [
                permission.get("id"),
                permission.get("code"),
                permission.get("module"),
                permission.get("label"),
                permission.get("description"),
            ]
            for permission in permissions
        ]
        self._populate_table(self.permissions_table, rows)

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

    def _selected_user(self) -> dict[str, Any] | None:
        row = self.users_table.currentRow()
        if row < 0 or row >= len(self.users):
            return None
        return self.users[row]

    def _current_search(self) -> str | None:
        value = self.search_input.text().strip()
        return value or None

    def _full_name(self, user: dict[str, Any]) -> str:
        first_name = str(user.get("first_name") or "").strip()
        last_name = str(user.get("last_name") or "").strip()
        full_name = " ".join(part for part in (first_name, last_name) if part)
        return full_name or "-"

    def _roles_label(self, user: dict[str, Any]) -> str:
        roles = user.get("roles")
        if not isinstance(roles, list):
            return "-"
        labels = [str(role.get("name")) for role in roles if isinstance(role, dict) and role.get("name")]
        return ", ".join(labels) if labels else "-"

    def _permissions_count(self, role: dict[str, Any]) -> int:
        permissions = role.get("permissions")
        return len(permissions) if isinstance(permissions, list) else 0

    def _set_busy(self, busy: bool) -> None:
        self.refresh_button.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.search_input.setEnabled(not busy)
        self.create_button.setEnabled(not busy)
        has_selection = self._selected_user() is not None
        self.edit_button.setEnabled(not busy and has_selection)
        self.toggle_active_button.setEnabled(not busy and has_selection)
        self.previous_button.setEnabled(not busy and self.current_page > 1)
        self.next_button.setEnabled(not busy and self.total_pages > 0 and self.current_page < self.total_pages)

    def _update_row_actions(self) -> None:
        has_selection = self._selected_user() is not None
        self.edit_button.setEnabled(has_selection)
        self.toggle_active_button.setEnabled(has_selection)

    def _update_pagination_actions(self) -> None:
        if self.tabs.tabText(self.tabs.currentIndex()) != "Utilisateurs":
            self.page_label.setText("Page -/-")
            self.previous_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
        pages_label = self.total_pages if self.total_pages else 0
        self.page_label.setText(f"Page {self.current_page}/{pages_label}")
        self.previous_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.total_pages > 0 and self.current_page < self.total_pages)

    def _error_message(self, exc: UsersServiceError) -> str:
        if exc.code == "bad_request":
            return "Requete utilisateurs invalide."
        if exc.code == "unauthorized":
            return "Connexion requise pour gerer les utilisateurs."
        if exc.code == "forbidden":
            return "Acces refuse : droits administrateur requis."
        if exc.code == "not_found":
            return "Utilisateur, role ou permission introuvable."
        if exc.code == "conflict":
            return "Un utilisateur, role ou permission avec cette valeur existe deja."
        if exc.code == "validation_error":
            details = self._validation_details(exc.details)
            if details:
                return f"Donnees invalides : {details}"
            return "Donnees invalides. Verifiez les champs du formulaire."
        if exc.code == "server_error":
            return "Erreur serveur pendant la gestion utilisateurs."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion utilisateurs : {exc}"

    def _validation_details(self, details: Any) -> str:
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
