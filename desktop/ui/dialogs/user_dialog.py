"""Dialog Desktop de creation et modification d'un utilisateur."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class UserDialog(QDialog):
    """Collect user fields before sending them to the REST API."""

    PASSWORD_MIN_LENGTH = 8

    def __init__(
        self,
        user: dict[str, Any] | None = None,
        *,
        roles: list[dict[str, Any]] | None = None,
        parent: object | None = None,
    ) -> None:
        """Create the user dialog."""

        super().__init__(parent)
        self.user = user or {}
        self.roles = roles or []
        self.setModal(True)
        self.setWindowTitle("Modifier un utilisateur" if user else "Ajouter un utilisateur")

        title = QLabel("Modifier un utilisateur" if user else "Ajouter un utilisateur")
        title.setObjectName("PageTitle")

        self.email_input = QLineEdit()
        self.email_input.setText(str(self.user.get("email") or ""))
        self.email_input.setPlaceholderText("utilisateur@example.com")

        self.first_name_input = QLineEdit()
        self.first_name_input.setText(str(self.user.get("first_name") or ""))
        self.first_name_input.setPlaceholderText("Prenom")

        self.last_name_input = QLineEdit()
        self.last_name_input.setText(str(self.user.get("last_name") or ""))
        self.last_name_input.setPlaceholderText("Nom")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText(
            "Mot de passe obligatoire" if not user else "Laisser vide pour ne pas modifier",
        )

        self.active_checkbox = QCheckBox("Utilisateur actif")
        self.active_checkbox.setChecked(bool(self.user.get("is_active", True)))

        self.superadmin_checkbox = QCheckBox("Super administrateur")
        self.superadmin_checkbox.setChecked(bool(self.user.get("is_superadmin", False)))

        self.roles_list = QListWidget()
        self.roles_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.roles_list.setMaximumHeight(140)
        self._populate_roles()

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Email", self.email_input)
        form_layout.addRow("Prenom", self.first_name_input)
        form_layout.addRow("Nom", self.last_name_input)
        form_layout.addRow("Mot de passe", self.password_input)
        form_layout.addRow("", self.active_checkbox)
        form_layout.addRow("", self.superadmin_checkbox)
        form_layout.addRow("Roles", self.roles_list)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.buttons)

    def payload(self) -> dict[str, Any]:
        """Return a payload compatible with the Users REST API."""

        payload: dict[str, Any] = {
            "email": self.email_input.text().strip(),
            "first_name": self.first_name_input.text().strip() or None,
            "last_name": self.last_name_input.text().strip() or None,
            "is_active": self.active_checkbox.isChecked(),
            "is_superadmin": self.superadmin_checkbox.isChecked(),
            "role_ids": self._selected_role_ids(),
        }
        password = self.password_input.text()
        if password:
            payload["password"] = password
        return payload

    def _populate_roles(self) -> None:
        selected_role_ids = self._current_role_ids()
        for role in self.roles:
            role_id = role.get("id")
            if not isinstance(role_id, int):
                continue
            label = str(role.get("name") or role_id)
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, role_id)
            self.roles_list.addItem(item)
            if role_id in selected_role_ids:
                item.setSelected(True)

    def _selected_role_ids(self) -> list[int]:
        role_ids: list[int] = []
        for item in self.roles_list.selectedItems():
            value = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(value, int):
                role_ids.append(value)
        return role_ids

    def _current_role_ids(self) -> set[int]:
        role_ids: set[int] = set()
        for role in self.user.get("roles") or []:
            if not isinstance(role, dict):
                continue
            role_id = role.get("id")
            if isinstance(role_id, int):
                role_ids.add(role_id)
        return role_ids

    def _accept_if_valid(self) -> None:
        error = self._validation_error()
        if error:
            self.message.setText(error)
            return
        self.accept()

    def _validation_error(self) -> str | None:
        email = self.email_input.text().strip()
        password = self.password_input.text()
        if not email:
            return "L'email est obligatoire."
        if "@" not in email or "." not in email.rsplit("@", maxsplit=1)[-1]:
            return "L'email doit etre valide."
        if not self.user and not password:
            return "Le mot de passe est obligatoire."
        if password and len(password) < self.PASSWORD_MIN_LENGTH:
            return "Le mot de passe doit contenir au moins 8 caracteres."
        return None
