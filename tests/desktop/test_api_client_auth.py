"""Tests de l'authentification dans le client API Desktop."""

import httpx
import pytest
from core.api_client import ApiClient, ApiClientError
from core.session import DesktopSession


def test_api_client_adds_authorization_header_when_token_exists() -> None:
    """Authenticated requests include the bearer token."""

    seen_headers: list[str | None] = []
    session = DesktopSession()
    session.set_token("token-123")

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.append(request.headers.get("Authorization"))
        return httpx.Response(200, json={"ok": True})

    client = ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler), session=session)

    assert client.get("/auth/me") == {"ok": True}
    assert seen_headers == ["Bearer token-123"]


def test_api_client_does_not_add_authorization_header_without_token() -> None:
    """Anonymous requests do not include an Authorization header."""

    seen_headers: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.append(request.headers.get("Authorization"))
        return httpx.Response(200, json={"status": "ok"})

    client = ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))

    assert client.get("/health") == {"status": "ok"}
    assert seen_headers == [None]


def test_check_health_stays_available_without_token() -> None:
    """The public health check still works without authentication."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "ok"})

    client = ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))

    assert client.check_health() is True


def test_api_client_preserves_401_status_code() -> None:
    """Unauthorized responses keep their status code."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Authentification requise."})

    client = ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))

    with pytest.raises(ApiClientError) as exc_info:
        client.get("/auth/me")

    assert exc_info.value.status_code == 401
    assert exc_info.value.details == {"detail": "Authentification requise."}


def test_api_client_preserves_403_status_code() -> None:
    """Forbidden responses keep their status code."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"detail": "Permission insuffisante."})

    client = ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))

    with pytest.raises(ApiClientError) as exc_info:
        client.get("/admin/dashboard")

    assert exc_info.value.status_code == 403
    assert exc_info.value.details == {"detail": "Permission insuffisante."}
