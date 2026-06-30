"""Tests des routes de sante publiques."""

from fastapi.testclient import TestClient


def test_public_health_route_returns_ok(client: TestClient) -> None:
    """Public health route returns the expected status payload."""

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_public_health_route_does_not_require_authentication(client: TestClient) -> None:
    """Desktop health check can be called without authentication."""

    response = client.get("/api/v1/health")

    assert response.status_code != 401
    assert response.status_code != 403


def test_admin_health_route_requires_authentication(client: TestClient) -> None:
    """Admin health route remains protected."""

    response = client.get("/api/v1/admin/health")

    assert response.status_code == 401
