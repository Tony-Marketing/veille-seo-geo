"""Tests des routes REST Websites."""

from fastapi.testclient import TestClient


def _create_website(
    client: TestClient,
    *,
    name: str = "Site Groupe",
    url: str = "https://example.com",
    cms: str | None = "WordPress",
    is_active: bool = True,
) -> dict:
    response = client.post(
        "/api/v1/websites",
        json={"name": name, "url": url, "cms": cms, "is_active": is_active},
    )
    assert response.status_code == 201
    return response.json()


def test_create_website(client: TestClient) -> None:
    """A website can be created."""

    data = _create_website(client)

    assert data["id"] is not None
    assert data["name"] == "Site Groupe"
    assert data["url"] == "https://example.com"
    assert data["cms"] == "WordPress"
    assert data["is_active"] is True


def test_read_website(client: TestClient) -> None:
    """A website can be read by id."""

    created = _create_website(client)

    response = client.get(f"/api/v1/websites/{created['id']}")

    assert response.status_code == 200
    assert response.json()["url"] == "https://example.com"


def test_list_websites_is_paginated(client: TestClient) -> None:
    """Website list is paginated."""

    _create_website(client, name="Site A", url="https://a.example.com")
    _create_website(client, name="Site B", url="https://b.example.com")
    _create_website(client, name="Site C", url="https://c.example.com")

    response = client.get("/api/v1/websites?page=1&page_size=2")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["pages"] == 2
    assert len(data["items"]) == 2


def test_search_websites(client: TestClient) -> None:
    """Website list can be searched."""

    _create_website(client, name="Groupe APPartner", url="https://groupe.example.com")
    _create_website(client, name="Autre site", url="https://other.example.com")

    response = client.get("/api/v1/websites?search=APPartner")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Groupe APPartner"


def test_filter_active_websites(client: TestClient) -> None:
    """Website list can be filtered on active websites."""

    _create_website(client, name="Site actif", url="https://active.example.com", is_active=True)
    _create_website(client, name="Site inactif", url="https://inactive.example.com", is_active=False)

    response = client.get("/api/v1/websites?is_active=true")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["is_active"] is True


def test_filter_inactive_websites(client: TestClient) -> None:
    """Website list can be filtered on inactive websites."""

    _create_website(client, name="Site actif", url="https://active.example.com", is_active=True)
    _create_website(client, name="Site inactif", url="https://inactive.example.com", is_active=False)

    response = client.get("/api/v1/websites?is_active=false")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["is_active"] is False


def test_update_website(client: TestClient) -> None:
    """A website can be updated."""

    created = _create_website(client)

    response = client.put(
        f"/api/v1/websites/{created['id']}",
        json={"name": "Site modifie", "cms": "Drupal", "is_active": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Site modifie"
    assert data["cms"] == "Drupal"
    assert data["is_active"] is False


def test_delete_website(client: TestClient) -> None:
    """A website can be deleted."""

    created = _create_website(client)

    delete_response = client.delete(f"/api/v1/websites/{created['id']}")
    get_response = client.get(f"/api/v1/websites/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_duplicate_url_returns_409(client: TestClient) -> None:
    """Duplicate website URLs are rejected."""

    _create_website(client, name="Site A", url="https://duplicate.example.com")

    response = client.post(
        "/api/v1/websites",
        json={"name": "Site B", "url": "https://duplicate.example.com"},
    )

    assert response.status_code == 409


def test_unknown_website_returns_404(client: TestClient) -> None:
    """Unknown website ids return 404."""

    response = client.get("/api/v1/websites/999")

    assert response.status_code == 404
