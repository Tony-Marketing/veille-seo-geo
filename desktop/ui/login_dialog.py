"""Boite de dialogue de connexion Desktop."""

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from core.api_client import ApiClientError
from services.auth_service import AuthService


class LoginDialog(QDialog):
    """Dialog used to authenticate a Desktop user."""

    def __init__(self, auth_service: AuthService, parent: object | None = None) -> None:
        """Create the login dialog."""

        super().__init__(parent)
        self.auth_service = auth_service
        self.setWindowTitle("Connexion")
        self.setModal(True)

        title = QLabel("Connexion")
        title.setObjectName("PageTitle")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.login_button = QPushButton("Connexion")
        self.login_button.clicked.connect(self._on_login_clicked)

        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Email", self.email_input)
        form_layout.addRow("Mot de passe", self.password_input)

        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        actions_layout.addWidget(cancel_button)
        actions_layout.addWidget(self.login_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.message)
        layout.addLayout(actions_layout)

    def _on_login_clicked(self) -> None:
        """Try to authenticate and close the dialog on success."""

        email = self.email_input.text().strip()
        password = self.password_input.text()
        if not email or not password:
            self.message.setText("Email et mot de passe sont obligatoires.")
            return

        self.login_button.setEnabled(False)
        try:
            self.auth_service.login(email, password)
        except ApiClientError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.accept()
        finally:
            self.login_button.setEnabled(True)

    def _error_message(self, exc: ApiClientError) -> str:
        """Return a readable authentication error message."""

        if exc.status_code == 401:
            return "Identifiants invalides."
        if exc.status_code == 403:
            return "Acces refuse ou compte desactive."
        if exc.status_code is None:
            return "API indisponible. Verifiez que le backend est lance."
        return "Connexion impossible."
