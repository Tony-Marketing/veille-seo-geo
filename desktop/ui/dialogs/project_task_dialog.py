"""Dialog Desktop de creation et modification d'une tache projet."""

from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
)


class ProjectTaskDialog(QDialog):
    """Collect project task fields before sending them to the REST API."""

    MIN_TITLE_LENGTH = 2
    MAX_TITLE_LENGTH = 200
    MAX_STATUS_LENGTH = 50
    MAX_PRIORITY_LENGTH = 50

    def __init__(self, project_task: dict[str, Any] | None = None, parent: object | None = None) -> None:
        """Create the project task dialog."""

        super().__init__(parent)
        self.project_task = project_task or {}
        self.setModal(True)
        self.setWindowTitle("Modifier une tache projet" if project_task else "Ajouter une tache projet")

        title = QLabel("Modifier une tache projet" if project_task else "Ajouter une tache projet")
        title.setObjectName("PageTitle")

        self.title_input = QLineEdit()
        self.title_input.setText(str(self.project_task.get("title") or ""))
        self.title_input.setPlaceholderText("Titre de la tache")
        self.title_input.setMaxLength(self.MAX_TITLE_LENGTH)

        self.description_input = QPlainTextEdit()
        self.description_input.setPlainText(str(self.project_task.get("description") or ""))
        self.description_input.setPlaceholderText("Description optionnelle")
        self.description_input.setFixedHeight(90)

        self.status_input = QLineEdit()
        self.status_input.setText(str(self.project_task.get("status") or "todo"))
        self.status_input.setPlaceholderText("todo")
        self.status_input.setMaxLength(self.MAX_STATUS_LENGTH)

        self.priority_input = QLineEdit()
        self.priority_input.setText(str(self.project_task.get("priority") or ""))
        self.priority_input.setPlaceholderText("Optionnel")
        self.priority_input.setMaxLength(self.MAX_PRIORITY_LENGTH)

        self.entity_id_input = QLineEdit()
        entity_id = self.project_task.get("entity_id")
        self.entity_id_input.setText("" if entity_id is None else str(entity_id))
        self.entity_id_input.setPlaceholderText("Optionnel")

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Titre", self.title_input)
        form_layout.addRow("Description", self.description_input)
        form_layout.addRow("Statut", self.status_input)
        form_layout.addRow("Priorite", self.priority_input)
        form_layout.addRow("Entite ID", self.entity_id_input)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.buttons)

    def payload(self) -> dict[str, Any]:
        """Return a payload compatible with the Project Tasks REST API."""

        entity_id_text = self.entity_id_input.text().strip()
        description = self.description_input.toPlainText().strip()
        priority = self.priority_input.text().strip()
        return {
            "entity_id": int(entity_id_text) if entity_id_text else None,
            "title": self.title_input.text().strip(),
            "description": description or None,
            "status": self.status_input.text().strip() or "todo",
            "priority": priority or None,
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

        title = self.title_input.text().strip()
        status = self.status_input.text().strip()
        priority = self.priority_input.text().strip()
        entity_id = self.entity_id_input.text().strip()
        if not title:
            return "Le titre est obligatoire."
        if len(title) < self.MIN_TITLE_LENGTH:
            return "Le titre doit contenir au moins 2 caracteres."
        if len(title) > self.MAX_TITLE_LENGTH:
            return "Le titre ne doit pas depasser 200 caracteres."
        if len(status) > self.MAX_STATUS_LENGTH:
            return "Le statut ne doit pas depasser 50 caracteres."
        if len(priority) > self.MAX_PRIORITY_LENGTH:
            return "La priorite ne doit pas depasser 50 caracteres."
        if entity_id and not entity_id.isdigit():
            return "L'identifiant d'entite doit etre un nombre."
        return None
