"""Dialog Desktop de creation et modification d'un site Web."""

from typing import Any
from urllib.parse import urlparse

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class WebsiteDialog(QDialog):
    """Collect website fields before sending them to the REST API."""

    def __init__(self, website: dict[str, Any] | None = None, parent: object | None = None) -> None:
        """Create the website dialog."""

        super().__init__(parent)
        self.website = website or {}
        self.setModal(True)
        self.setWindowTitle("Modifier un site" if website else "Ajouter un site")

        title = QLabel("Modifier un site" if website else "Ajouter un site")
        title.setObjectName("PageTitle")

        self.name_input = QLineEdit()
        self.name_input.setText(str(self.website.get("name") or ""))
        self.name_input.setPlaceholderText("Nom du site")

        self.url_input = QLineEdit()
        self.url_input.setText(str(self.website.get("url") or ""))
        self.url_input.setPlaceholderText("https://example.com")

        self.cms_input = QLineEdit()
        self.cms_input.setText(str(self.website.get("cms") or ""))
        self.cms_input.setPlaceholderText("WordPress, Drupal...")

        self.entity_id_input = QLineEdit()
        entity_id = self.website.get("entity_id")
        self.entity_id_input.setText("" if entity_id is None else str(entity_id))
        self.entity_id_input.setPlaceholderText("Optionnel")

        self.active_checkbox = QCheckBox("Site actif")
        self.active_checkbox.setChecked(bool(self.website.get("is_active", True)))

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Nom", self.name_input)
        form_layout.addRow("URL", self.url_input)
        form_layout.addRow("CMS", self.cms_input)
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
        """Return a payload compatible with the Websites REST API."""

        entity_id_text = self.entity_id_input.text().strip()
        return {
            "entity_id": int(entity_id_text) if entity_id_text else None,
            "name": self.name_input.text().strip(),
            "url": self.url_input.text().strip(),
            "cms": self.cms_input.text().strip() or None,
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
        url = self.url_input.text().strip()
        entity_id = self.entity_id_input.text().strip()
        if not name:
            return "Le nom est obligatoire."
        if len(name) < 2:
            return "Le nom doit contenir au moins 2 caracteres."
        if not url:
            return "L'URL est obligatoire."
        if not self._is_valid_url(url):
            return "L'URL doit commencer par http:// ou https:// et contenir un domaine."
        if entity_id and not entity_id.isdigit():
            return "L'identifiant d'entite doit etre un nombre."
        return None

    def _is_valid_url(self, value: str) -> bool:
        """Return True when the URL has a minimal valid HTTP(S) shape."""

        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
