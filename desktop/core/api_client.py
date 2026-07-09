"""Client HTTP REST utilise par l'application Desktop."""

from typing import Any

import httpx
from core.config import API_BASE_URL, HTTP_TIMEOUT_SECONDS
from core.session import DesktopSession


class ApiClientError(RuntimeError):
    """Erreur lisible pour les problemes de communication API."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class ApiClient:
    """Client REST centralise pour communiquer avec l'API FastAPI."""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout: float = HTTP_TIMEOUT_SECONDS,
        transport: httpx.BaseTransport | None = None,
        session: DesktopSession | None = None,
        access_token: str | None = None,
    ) -> None:
        """Initialise le client HTTP.

        Args:
            base_url: URL racine de l'API REST.
            timeout: Delai maximum des requetes HTTP en secondes.
            transport: Transport HTTP optionnel, utile pour les tests sans reseau.
            session: Session Desktop optionnelle contenant le token courant.
            access_token: Token optionnel pour les usages simples ou les tests.
        """

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport
        self.session = session
        self.access_token = access_token

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Execute une requete GET vers l'API."""

        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Execute une requete POST vers l'API."""

        return self._request("POST", path, json=json)

    def put(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Execute une requete PUT vers l'API."""

        return self._request("PUT", path, json=json)

    def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Execute une requete PATCH vers l'API."""

        return self._request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:
        """Execute une requete DELETE vers l'API."""

        return self._request("DELETE", path)

    def check_health(self) -> bool:
        """Return True when the backend health endpoint responds successfully."""

        try:
            payload = self.get("/health")
        except ApiClientError:
            return False

        return isinstance(payload, dict) and payload.get("status") == "ok"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Execute une requete HTTP et normalise les erreurs reseau."""

        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
                response = client.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=self._auth_headers(),
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            details = self._safe_error_details(exc.response)
            raise ApiClientError(
                f"Erreur API {exc.response.status_code} pour {url}",
                status_code=exc.response.status_code,
                details=details,
            ) from exc
        except httpx.RequestError as exc:
            raise ApiClientError(f"API indisponible pour {url}") from exc

        if response.status_code == httpx.codes.NO_CONTENT:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise ApiClientError(f"Reponse API invalide pour {url}", status_code=response.status_code) from exc

    def _safe_error_details(self, response: httpx.Response) -> Any | None:
        """Return JSON error details when the API response contains valid JSON."""

        try:
            return response.json()
        except ValueError:
            return None

    def _auth_headers(self) -> dict[str, str] | None:
        """Return Authorization headers when a token is available."""

        token = self.access_token
        if token is None and self.session is not None:
            token = self.session.access_token
        if not token:
            return None
        return {"Authorization": f"Bearer {token}"}
