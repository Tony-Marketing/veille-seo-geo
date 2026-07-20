"""Dialog Desktop for crawl creation."""

from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)


class CrawlDialog(QDialog):
    """Collect crawl creation parameters."""

    def __init__(self, parent: Any | None = None, *, default_website_id: int | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nouveau crawl")
        self.resize(420, 220)

        self.website_id_input = QLineEdit()
        self.website_id_input.setPlaceholderText("Optionnel")
        if default_website_id is not None:
            self.website_id_input.setText(str(default_website_id))

        self.start_url_input = QLineEdit()
        self.start_url_input.setPlaceholderText("https://www.example.com")

        self.max_depth_input = QSpinBox()
        self.max_depth_input.setRange(0, 10)
        self.max_depth_input.setValue(2)

        self.max_pages_input = QSpinBox()
        self.max_pages_input.setRange(1, 1000)
        self.max_pages_input.setValue(100)

        form_layout = QFormLayout()
        form_layout.addRow("ID site", self.website_id_input)
        form_layout.addRow("URL de depart", self.start_url_input)
        form_layout.addRow("Profondeur max", self.max_depth_input)
        form_layout.addRow("Pages max", self.max_pages_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.buttons)

    def payload(self) -> dict[str, Any]:
        """Return API payload for crawl creation."""

        payload: dict[str, Any] = {
            "max_depth": self.max_depth_input.value(),
            "max_pages": self.max_pages_input.value(),
        }
        website_id = self.website_id_input.text().strip()
        start_url = self.start_url_input.text().strip()
        if website_id:
            payload["website_id"] = int(website_id)
        if start_url:
            payload["start_url"] = start_url
        return payload

    def _accept_if_valid(self) -> None:
        website_id = self.website_id_input.text().strip()
        start_url = self.start_url_input.text().strip()
        if not website_id and not start_url:
            QMessageBox.warning(self, "Crawl incomplet", "Renseignez un ID site ou une URL de depart.")
            return
        if website_id and not website_id.isdigit():
            QMessageBox.warning(self, "ID site invalide", "L'ID site doit etre un nombre entier.")
            return
        self.accept()

