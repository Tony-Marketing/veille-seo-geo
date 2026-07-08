"""Service d'envoi email backend."""

import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode

from backend.app.core.config import settings


class EmailDeliveryError(RuntimeError):
    """Raised when an email cannot be delivered."""


class EmailService:
    """Send transactional emails through SMTP."""

    def build_activation_link(self, token: str) -> str:
        """Return an activation link containing the raw token."""

        separator = "&" if "?" in settings.activation_base_url else "?"
        return f"{settings.activation_base_url}{separator}{urlencode({'token': token})}"

    def send_activation_email(self, *, email: str, token: str) -> None:
        """Send a 24-hour account activation email."""

        if not settings.smtp_host:
            raise EmailDeliveryError("Configuration SMTP absente.")

        activation_link = self.build_activation_link(token)
        message = EmailMessage()
        message["From"] = settings.smtp_from_email
        message["To"] = email
        message["Subject"] = "Activation de votre compte Veille SEO-GEO"
        message.set_content(
            "Bonjour,\n\n"
            "Un compte vient d'etre cree pour vous sur la plateforme Veille SEO-GEO Groupe A.P&Partner.\n"
            "Pour l'activer, ouvrez le lien suivant dans les 24 heures et definissez votre mot de passe :\n\n"
            f"{activation_link}\n\n"
            "Si vous n'etes pas a l'origine de cette demande, ignorez cet email.\n",
        )

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if settings.smtp_username and settings.smtp_password:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
        except OSError as exc:
            raise EmailDeliveryError("Email d'activation non envoye.") from exc
