"""Tests du service d'authentification Desktop."""

import json

import httpx
import pytest
from core.api_client import ApiClient, ApiClientError
from core.session import DesktopSession
from services.auth_service import AuthService


def test_empty_session_is_not_authenticated() -> None:
    """A new Desktop session has no authentication state."""

    session = DesktopSession()

    assert session.access_token is None
    assert session.user is None
    assert session.is_authenticated is False


def test_session_with_token_is_authenticated() -> None:
    """A session with a token is authenticated."""

    session = DesktopSession()
    session.set_token("token-123")

    assert session.is_authenticated is True


def test_session_stores_user_and_clear_purges_state() -> None:
    """Clearing a session removes token and user data."""

    session = DesktopSession()
    session.set_token("token-123")
    session.set_user({"email": "admin@example.com"})

    session.clear()

    assert session.access_token is None
    assert session.user is None
    assert session.is_authenticated is False


def test_login_stores_token_and_current_user() -> None:
    """Login stores the token then loads the current user."""

    seen_requests: list[tuple[str, str, str | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url.path, request.headers.get("Authorization")))
        if request.url.path == "/api/v1/auth/login":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload == {"email": "admin@example.com", "password": "Password123"}
            return httpx.Response(200, json={"access_token": "token-123", "token_type": "bearer"})
        if request.url.path == "/api/v1/auth/me":
            return httpx.Response(200, json={"email": "admin@example.com", "first_name": "Admin"})
        return httpx.Response(404, json={"detail": "missing"})

    session = DesktopSession()
    api_client = ApiClient(
        base_url="http://api.test/api/v1",
        transport=httpx.MockTransport(handler),
        session=session,
    )
    service = AuthService(api_client, session)

    user = service.login("admin@example.com", "Password123")

    assert user == {"email": "admin@example.com", "first_name": "Admin"}
    assert session.access_token == "token-123"
    assert session.user == user
    assert seen_requests == [
        ("POST", "/api/v1/auth/login", None),
        ("GET", "/api/v1/auth/me", "Bearer token-123"),
    ]


@pytest.mark.parametrize("status_code", [401, 403])
def test_login_refusal_preserves_status_code(status_code: int) -> None:
    """Authentication refusals keep their API status code."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "Erreur auth."})

    session = DesktopSession()
    api_client = ApiClient(
        base_url="http://api.test/api/v1",
        transport=httpx.MockTransport(handler),
        session=session,
    )
    service = AuthService(api_client, session)

    with pytest.raises(ApiClientError) as exc_info:
        service.login("admin@example.com", "Password123")

    assert exc_info.value.status_code == status_code
    assert session.is_authenticated is False


def test_login_network_error_keeps_session_empty() -> None:
    """Network errors leave the local session empty."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    session = DesktopSession()
    api_client = ApiClient(
        base_url="http://api.test/api/v1",
        transport=httpx.MockTransport(handler),
        session=session,
    )
    service = AuthService(api_client, session)

    with pytest.raises(ApiClientError) as exc_info:
        service.login("admin@example.com", "Password123")

    assert exc_info.value.status_code is None
    assert session.is_authenticated is False


def test_logout_clears_session() -> None:
    """Logout clears the in-memory session."""

    session = DesktopSession()
    session.set_token("token-123")
    session.set_user({"email": "admin@example.com"})
    api_client = ApiClient(base_url="http://api.test/api/v1", session=session)
    service = AuthService(api_client, session)

    service.logout()

    assert session.access_token is None
    assert session.user is None
    assert session.is_authenticated is False
