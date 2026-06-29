"""Client HTTP REST utilise par l'application Desktop."""

from typing import Any

import httpx
from core.config import API_BASE_URL, HTTP_TIMEOUT_SECONDS


class ApiClientError(RuntimeError):
    """Erreur lisible pour les problemes de communication API."""


class ApiClient:
    """Client REST centralise pour communiquer avec l'API FastAPI."""

    def __init__(self, base_url: str = API_BASE_URL, timeout: float = HTTP_TIMEOUT_SECONDS) -> None:
        """Initialise le client HTTP.

        Args:
            base_url: URL racine de l'API REST.
            timeout: Delai maximum des requetes HTTP en secondes.
        """

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Execute une requete GET vers l'API."""

        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Execute une requete POST vers l'API."""

        return self._request("POST", path, json=json)

    def put(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Execute une requete PUT vers l'API."""

        return self._request("PUT", path, json=json)

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
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, params=params, json=json)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ApiClientError(f"Erreur API {exc.response.status_code} pour {url}") from exc
        except httpx.RequestError as exc:
            raise ApiClientError(f"API indisponible pour {url}") from exc

        if response.status_code == httpx.codes.NO_CONTENT:
            return None
        return response.json()
