"""Dialog Desktop de creation et modification d'une entite."""

from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
)


class EntityDialog(QDialog):
    """Collect entity fields before sending them to the REST API."""

    MAX_NAME_LENGTH = 150

    def __init__(self, entity: dict[str, Any] | None = None, parent: object | None = None) -> None:
        """Create the entity dialog."""

        super().__init__(parent)
        self.entity = entity or {}
        self.setModal(True)
        self.setWindowTitle("Modifier une entite" if entity else "Ajouter une entite")

        title = QLabel("Modifier une entite" if entity else "Ajouter une entite")
        title.setObjectName("PageTitle")

        self.name_input = QLineEdit()
        self.name_input.setText(str(self.entity.get("name") or ""))
        self.name_input.setPlaceholderText("Nom de l'entite")
        self.name_input.setMaxLength(self.MAX_NAME_LENGTH)

        self.description_input = QPlainTextEdit()
        self.description_input.setPlainText(str(self.entity.get("description") or ""))
        self.description_input.setPlaceholderText("Description optionnelle")
        self.description_input.setFixedHeight(90)

        self.active_checkbox = QCheckBox("Entite active")
        self.active_checkbox.setChecked(bool(self.entity.get("is_active", True)))

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Nom", self.name_input)
        form_layout.addRow("Description", self.description_input)
        form_layout.addRow("", self.active_checkbox)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.buttons)

    def payload(self) -> dict[str, Any]:
        """Return a payload compatible with the Entities REST API."""

        description = self.description_input.toPlainText().strip()
        return {
            "name": self.name_input.text().strip(),
            "description": description or None,
            "is_active": self.active_checkbox.isChecked(),
        }

    def _accept_if_valid(self) -> None:
        """Accept the dialog only when simple Desktop validation passes."""

        error = self._validation_error()
        if error:
            self.message.setText(error)
            return
        self.accept()

    def _validation_error(self) -> str | None:
        """Return the first validation error, if any."""

        name = self.name_input.text().strip()
        if not name:
            return "Le nom est obligatoire."
        if len(name) < 2:
            return "Le nom doit contenir au moins 2 caracteres."
        if len(name) > self.MAX_NAME_LENGTH:
            return "Le nom ne doit pas depasser 150 caracteres."
        return None
