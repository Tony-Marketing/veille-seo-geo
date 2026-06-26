"""Tests des routes REST d'administration."""

from fastapi.testclient import TestClient


def test_admin_dashboard_requires_authentication(client: TestClient) -> None:
    """Admin routes require authentication."""

    response = client.get("/api/v1/admin/dashboard")

    assert response.status_code == 401


def test_admin_dashboard_returns_counts(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Admin dashboard exposes backend indicators."""

    response = client.get("/api/v1/admin/dashboard", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["users_count"] == 1
    assert data["postgresql_status"] == "Healthy"


def test_api_key_route_masks_secret(client: TestClient, admin_headers: dict[str, str]) -> None:
    """API key responses never expose the clear secret."""

    response = client.post(
        "/api/v1/admin/api-keys",
        headers=admin_headers,
        json={"name": "OpenAI", "provider_name": "OpenAI", "value": "sk-secret"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "value" not in data
    assert data["masked_value"] != "sk-secret"
