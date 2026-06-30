"""Service Desktop d'authentification via l'API REST."""

from typing import Any

from core.api_client import ApiClient, ApiClientError
from core.session import DesktopSession


class AuthService:
    """Authenticate Desktop users through the FastAPI auth endpoints."""

    def __init__(self, api_client: ApiClient, session: DesktopSession) -> None:
        self.api_client = api_client
        self.session = session

    def login(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate a user and load the current user profile."""

        payload = self.api_client.post("/auth/login", json={"email": email, "password": password})
        access_token = self._extract_access_token(payload)
        self.session.set_token(access_token)

        try:
            return self.load_current_user()
        except ApiClientError:
            self.session.clear()
            raise

    def load_current_user(self) -> dict[str, Any]:
        """Load and store the current authenticated user."""

        payload = self.api_client.get("/auth/me")
        if not isinstance(payload, dict):
            raise ApiClientError("Profil utilisateur invalide.")
        self.session.set_user(payload)
        return payload

    def logout(self) -> None:
        """Clear the local in-memory session."""

        self.session.clear()

    def _extract_access_token(self, payload: Any) -> str:
        """Extract the access token from the API login payload."""

        if not isinstance(payload, dict):
            raise ApiClientError("Reponse d'authentification invalide.")

        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise ApiClientError("Jeton d'authentification manquant.")

        return access_token
