"""Dialog Desktop de creation et modification d'un concurrent."""

from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class CompetitorDialog(QDialog):
    """Collect competitor fields before sending them to the REST API."""

    MAX_NAME_LENGTH = 150
    MAX_WEBSITE_URL_LENGTH = 255

    def __init__(self, competitor: dict[str, Any] | None = None, parent: object | None = None) -> None:
        """Create the competitor dialog."""

        super().__init__(parent)
        self.competitor = competitor or {}
        self.setModal(True)
        self.setWindowTitle("Modifier un concurrent" if competitor else "Ajouter un concurrent")

        title = QLabel("Modifier un concurrent" if competitor else "Ajouter un concurrent")
        title.setObjectName("PageTitle")

        self.name_input = QLineEdit()
        self.name_input.setText(str(self.competitor.get("name") or ""))
        self.name_input.setPlaceholderText("Nom du concurrent")
        self.name_input.setMaxLength(self.MAX_NAME_LENGTH)

        self.website_url_input = QLineEdit()
        self.website_url_input.setText(str(self.competitor.get("website_url") or ""))
        self.website_url_input.setPlaceholderText("https://example.com")
        self.website_url_input.setMaxLength(self.MAX_WEBSITE_URL_LENGTH)

        self.entity_id_input = QLineEdit()
        entity_id = self.competitor.get("entity_id")
        self.entity_id_input.setText("" if entity_id is None else str(entity_id))
        self.entity_id_input.setPlaceholderText("Optionnel")

        self.active_checkbox = QCheckBox("Concurrent actif")
        self.active_checkbox.setChecked(bool(self.competitor.get("is_active", True)))

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Nom", self.name_input)
        form_layout.addRow("URL du site", self.website_url_input)
        form_layout.addRow("Entite ID", self.entity_id_input)
        form_layout.addRow("", self.active_checkbox)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.buttons)

    def payload(self) -> dict[str, Any]:
        """Return a payload compatible with the Competitors REST API."""

        entity_id_text = self.entity_id_input.text().strip()
        website_url = self.website_url_input.text().strip()
        return {
            "entity_id": int(entity_id_text) if entity_id_text else None,
            "name": self.name_input.text().strip(),
            "website_url": website_url or None,
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
        website_url = self.website_url_input.text().strip()
        entity_id = self.entity_id_input.text().strip()
        if not name:
            return "Le nom est obligatoire."
        if len(name) < 2:
            return "Le nom doit contenir au moins 2 caracteres."
        if len(name) > self.MAX_NAME_LENGTH:
            return "Le nom ne doit pas depasser 150 caracteres."
        if len(website_url) > self.MAX_WEBSITE_URL_LENGTH:
            return "L'URL du site ne doit pas depasser 255 caracteres."
        if entity_id and not entity_id.isdigit():
            return "L'identifiant d'entite doit etre un nombre."
        return None
