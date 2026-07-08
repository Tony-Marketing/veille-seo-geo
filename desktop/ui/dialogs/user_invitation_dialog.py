"""Dialog Desktop d'invitation utilisateur."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class UserInvitationDialog(QDialog):
    """Collect user invitation fields before sending them to the REST API."""

    def __init__(self, *, roles: list[dict[str, Any]] | None = None, parent: object | None = None) -> None:
        """Create the invitation dialog."""

        super().__init__(parent)
        self.roles = roles or []
        self.setModal(True)
        self.setWindowTitle("Inviter un utilisateur")

        title = QLabel("Inviter un utilisateur")
        title.setObjectName("PageTitle")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("utilisateur@example.com")

        self.roles_list = QListWidget()
        self.roles_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.roles_list.setMaximumHeight(140)
        self._populate_roles()

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        ok_button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button is not None:
            ok_button.setText("Creer et envoyer l'invitation")
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Email", self.email_input)
        form_layout.addRow("Roles", self.roles_list)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.buttons)

    def payload(self) -> dict[str, Any]:
        """Return a payload compatible with the invitation REST API."""

        return {
            "email": self.email_input.text().strip(),
            "role_ids": self._selected_role_ids(),
        }

    def _populate_roles(self) -> None:
        for role in self.roles:
            role_id = role.get("id")
            if not isinstance(role_id, int):
                continue
            label = str(role.get("name") or role_id)
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, role_id)
            self.roles_list.addItem(item)

    def _selected_role_ids(self) -> list[int]:
        role_ids: list[int] = []
        for item in self.roles_list.selectedItems():
            value = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(value, int):
                role_ids.append(value)
        return role_ids

    def _accept_if_valid(self) -> None:
        error = self._validation_error()
        if error:
            self.message.setText(error)
            return
        self.accept()

    def _validation_error(self) -> str | None:
        email = self.email_input.text().strip()
        if not email:
            return "L'email est obligatoire."
        if "@" not in email or "." not in email.rsplit("@", maxsplit=1)[-1]:
            return "L'email doit etre valide."
        return None
