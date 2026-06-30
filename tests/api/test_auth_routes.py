"""Tests des routes REST d'authentification."""

from fastapi.testclient import TestClient


def test_login_returns_access_token_for_valid_credentials(client: TestClient, admin_user: object) -> None:
    """A known active user can authenticate."""

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_rejects_wrong_password(client: TestClient, admin_user: object) -> None:
    """Invalid credentials are rejected."""

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Identifiants invalides."}


def test_login_rejects_unknown_user(client: TestClient) -> None:
    """Unknown users are rejected with the same generic error."""

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "Password123"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Identifiants invalides."}


def test_me_returns_current_user(client: TestClient, admin_headers: dict[str, str]) -> None:
    """The current user endpoint returns the authenticated user."""

    response = client.get("/api/v1/auth/me", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert data["is_active"] is True
    assert data["is_superadmin"] is True


def test_me_requires_token(client: TestClient) -> None:
    """The current user endpoint requires authentication."""

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentification requise."}


def test_me_rejects_invalid_token(client: TestClient) -> None:
    """Invalid bearer tokens are rejected."""

    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Jeton d'authentification invalide."}


def test_refresh_returns_new_access_token(client: TestClient, admin_headers: dict[str, str]) -> None:
    """The current access token can be used to request a new token."""

    response = client.post("/api/v1/auth/refresh", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_refresh_requires_token(client: TestClient) -> None:
    """Refresh requires an authenticated user."""

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentification requise."}
