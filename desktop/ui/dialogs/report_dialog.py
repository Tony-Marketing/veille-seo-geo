"""Dialog Desktop de creation et modification d'un rapport."""

from typing import Any

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout


class ReportDialog(QDialog):
    """Collect report fields before sending them to the REST API."""

    MIN_TITLE_LENGTH = 2
    MAX_TITLE_LENGTH = 200
    MAX_REPORT_TYPE_LENGTH = 80
    MAX_STATUS_LENGTH = 50

    def __init__(self, report: dict[str, Any] | None = None, parent: object | None = None) -> None:
        """Create the report dialog."""

        super().__init__(parent)
        self.report = report or {}
        self.setModal(True)
        self.setWindowTitle("Modifier un rapport" if report else "Ajouter un rapport")

        title = QLabel("Modifier un rapport" if report else "Ajouter un rapport")
        title.setObjectName("PageTitle")

        self.title_input = QLineEdit()
        self.title_input.setText(str(self.report.get("title") or ""))
        self.title_input.setPlaceholderText("Titre du rapport")
        self.title_input.setMaxLength(self.MAX_TITLE_LENGTH)

        self.report_type_input = QLineEdit()
        self.report_type_input.setText(str(self.report.get("report_type") or ""))
        self.report_type_input.setPlaceholderText("Optionnel")
        self.report_type_input.setMaxLength(self.MAX_REPORT_TYPE_LENGTH)

        self.status_input = QLineEdit()
        self.status_input.setText(str(self.report.get("status") or "draft"))
        self.status_input.setPlaceholderText("draft")
        self.status_input.setMaxLength(self.MAX_STATUS_LENGTH)

        self.entity_id_input = QLineEdit()
        entity_id = self.report.get("entity_id")
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
        form_layout.addRow("Type", self.report_type_input)
        form_layout.addRow("Statut", self.status_input)
        form_layout.addRow("Entite ID", self.entity_id_input)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.buttons)

    def payload(self) -> dict[str, Any]:
        """Return a payload compatible with the Reports REST API."""

        entity_id_text = self.entity_id_input.text().strip()
        report_type = self.report_type_input.text().strip()
        return {
            "entity_id": int(entity_id_text) if entity_id_text else None,
            "title": self.title_input.text().strip(),
            "report_type": report_type or None,
            "status": self.status_input.text().strip() or "draft",
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
        report_type = self.report_type_input.text().strip()
        status = self.status_input.text().strip()
        entity_id = self.entity_id_input.text().strip()
        if not title:
            return "Le titre est obligatoire."
        if len(title) < self.MIN_TITLE_LENGTH:
            return "Le titre doit contenir au moins 2 caracteres."
        if len(title) > self.MAX_TITLE_LENGTH:
            return "Le titre ne doit pas depasser 200 caracteres."
        if len(report_type) > self.MAX_REPORT_TYPE_LENGTH:
            return "Le type ne doit pas depasser 80 caracteres."
        if len(status) > self.MAX_STATUS_LENGTH:
            return "Le statut ne doit pas depasser 50 caracteres."
        if entity_id and not entity_id.isdigit():
            return "L'identifiant d'entite doit etre un nombre."
        return None
