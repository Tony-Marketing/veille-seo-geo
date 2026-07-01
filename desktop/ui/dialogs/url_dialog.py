"""Dialog Desktop de creation et modification d'une URL."""

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


class URLDialog(QDialog):
    """Collect URL fields before sending them to the REST API."""

    MIN_URL_LENGTH = 8
    MAX_URL_LENGTH = 500
    MIN_STATUS_CODE = 100
    MAX_STATUS_CODE = 599

    def __init__(self, url_data: dict[str, Any] | None = None, parent: object | None = None) -> None:
        """Create the URL dialog."""

        super().__init__(parent)
        self.url_data = url_data or {}
        self.setModal(True)
        self.setWindowTitle("Modifier une URL" if url_data else "Ajouter une URL")

        title = QLabel("Modifier une URL" if url_data else "Ajouter une URL")
        title.setObjectName("PageTitle")

        self.url_input = QLineEdit()
        self.url_input.setText(str(self.url_data.get("url") or ""))
        self.url_input.setPlaceholderText("https://example.com/page")
        self.url_input.setMaxLength(self.MAX_URL_LENGTH)

        self.website_id_input = QLineEdit()
        website_id = self.url_data.get("website_id")
        self.website_id_input.setText("" if website_id is None else str(website_id))
        self.website_id_input.setPlaceholderText("Optionnel")

        self.status_code_input = QLineEdit()
        status_code = self.url_data.get("status_code")
        self.status_code_input.setText("" if status_code is None else str(status_code))
        self.status_code_input.setPlaceholderText("Optionnel")

        self.indexable_checkbox = QCheckBox("URL indexable")
        self.indexable_checkbox.setChecked(bool(self.url_data.get("is_indexable", True)))

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("URL", self.url_input)
        form_layout.addRow("Website ID", self.website_id_input)
        form_layout.addRow("Code HTTP", self.status_code_input)
        form_layout.addRow("", self.indexable_checkbox)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.buttons)

    def payload(self) -> dict[str, Any]:
        """Return a payload compatible with the URLs REST API."""

        website_id_text = self.website_id_input.text().strip()
        status_code_text = self.status_code_input.text().strip()
        return {
            "website_id": int(website_id_text) if website_id_text else None,
            "url": self.url_input.text().strip(),
            "status_code": int(status_code_text) if status_code_text else None,
            "is_indexable": self.indexable_checkbox.isChecked(),
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

        url = self.url_input.text().strip()
        website_id = self.website_id_input.text().strip()
        status_code = self.status_code_input.text().strip()
        if not url:
            return "L'URL est obligatoire."
        if len(url) < self.MIN_URL_LENGTH:
            return "L'URL doit contenir au moins 8 caracteres."
        if len(url) > self.MAX_URL_LENGTH:
            return "L'URL ne doit pas depasser 500 caracteres."
        if website_id and not website_id.isdigit():
            return "L'identifiant de site doit etre un nombre."
        if status_code and not status_code.isdigit():
            return "Le code HTTP doit etre un nombre."
        if status_code:
            numeric_status = int(status_code)
            if numeric_status < self.MIN_STATUS_CODE or numeric_status > self.MAX_STATUS_CODE:
                return "Le code HTTP doit etre compris entre 100 et 599."
        return None
