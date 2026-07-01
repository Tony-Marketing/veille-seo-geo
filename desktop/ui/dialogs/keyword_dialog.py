"""Dialog Desktop de creation et modification d'un mot-cle."""

from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class KeywordDialog(QDialog):
    """Collect keyword fields before sending them to the REST API."""

    MAX_TERM_LENGTH = 255
    MAX_INTENT_LENGTH = 100
    MAX_PRIORITY_LENGTH = 50

    def __init__(self, keyword: dict[str, Any] | None = None, parent: object | None = None) -> None:
        """Create the keyword dialog."""

        super().__init__(parent)
        self.keyword = keyword or {}
        self.setModal(True)
        self.setWindowTitle("Modifier un mot-cle" if keyword else "Ajouter un mot-cle")

        title = QLabel("Modifier un mot-cle" if keyword else "Ajouter un mot-cle")
        title.setObjectName("PageTitle")

        self.term_input = QLineEdit()
        self.term_input.setText(str(self.keyword.get("term") or ""))
        self.term_input.setPlaceholderText("Mot-cle")
        self.term_input.setMaxLength(self.MAX_TERM_LENGTH)

        self.intent_input = QLineEdit()
        self.intent_input.setText(str(self.keyword.get("intent") or ""))
        self.intent_input.setPlaceholderText("Informationnel, commercial...")
        self.intent_input.setMaxLength(self.MAX_INTENT_LENGTH)

        self.priority_input = QLineEdit()
        self.priority_input.setText(str(self.keyword.get("priority") or ""))
        self.priority_input.setPlaceholderText("Haute, moyenne, basse...")
        self.priority_input.setMaxLength(self.MAX_PRIORITY_LENGTH)

        self.entity_id_input = QLineEdit()
        entity_id = self.keyword.get("entity_id")
        self.entity_id_input.setText("" if entity_id is None else str(entity_id))
        self.entity_id_input.setPlaceholderText("Optionnel")

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self._accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Mot-cle", self.term_input)
        form_layout.addRow("Intention", self.intent_input)
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
        """Return a payload compatible with the Keywords REST API."""

        entity_id_text = self.entity_id_input.text().strip()
        intent = self.intent_input.text().strip()
        priority = self.priority_input.text().strip()
        return {
            "entity_id": int(entity_id_text) if entity_id_text else None,
            "term": self.term_input.text().strip(),
            "intent": intent or None,
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

        term = self.term_input.text().strip()
        intent = self.intent_input.text().strip()
        priority = self.priority_input.text().strip()
        entity_id = self.entity_id_input.text().strip()
        if not term:
            return "Le mot-cle est obligatoire."
        if len(term) > self.MAX_TERM_LENGTH:
            return "Le mot-cle ne doit pas depasser 255 caracteres."
        if len(intent) > self.MAX_INTENT_LENGTH:
            return "L'intention ne doit pas depasser 100 caracteres."
        if len(priority) > self.MAX_PRIORITY_LENGTH:
            return "La priorite ne doit pas depasser 50 caracteres."
        if entity_id and not entity_id.isdigit():
            return "L'identifiant d'entite doit etre un nombre."
        return None
