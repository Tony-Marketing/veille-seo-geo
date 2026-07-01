"""Tests des routes REST Websites."""

from collections.abc import Callable

from fastapi.testclient import TestClient

AuthHeadersFactory = Callable[..., dict[str, str]]


def _create_website(
    client: TestClient,
    *,
    name: str = "Site Groupe",
    url: str = "https://example.com",
    cms: str | None = "WordPress",
    is_active: bool = True,
    headers: dict[str, str] | None = None,
) -> dict:
    response = client.post(
        "/api/v1/websites",
        headers=headers,
        json={"name": name, "url": url, "cms": cms, "is_active": is_active},
    )
    assert response.status_code == 201
    return response.json()


def test_create_website(client: TestClient, admin_headers: dict[str, str]) -> None:
    """A website can be created."""

    data = _create_website(client, headers=admin_headers)

    assert data["id"] is not None
    assert data["name"] == "Site Groupe"
    assert data["url"] == "https://example.com"
    assert data["cms"] == "WordPress"
    assert data["is_active"] is True


def test_read_website(client: TestClient, admin_headers: dict[str, str]) -> None:
    """A website can be read by id."""

    created = _create_website(client, headers=admin_headers)

    response = client.get(f"/api/v1/websites/{created['id']}", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["url"] == "https://example.com"


def test_list_websites_is_paginated(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Website list is paginated."""

    _create_website(client, name="Site A", url="https://a.example.com", headers=admin_headers)
    _create_website(client, name="Site B", url="https://b.example.com", headers=admin_headers)
    _create_website(client, name="Site C", url="https://c.example.com", headers=admin_headers)

    response = client.get("/api/v1/websites?page=1&page_size=2", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["pages"] == 2
    assert len(data["items"]) == 2


def test_search_websites(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Website list can be searched."""

    _create_website(client, name="Groupe APPartner", url="https://groupe.example.com", headers=admin_headers)
    _create_website(client, name="Autre site", url="https://other.example.com", headers=admin_headers)

    response = client.get("/api/v1/websites?search=APPartner", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Groupe APPartner"


def test_filter_active_websites(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Website list can be filtered on active websites."""

    _create_website(client, name="Site actif", url="https://active.example.com", is_active=True, headers=admin_headers)
    _create_website(
        client,
        name="Site inactif",
        url="https://inactive.example.com",
        is_active=False,
        headers=admin_headers,
    )

    response = client.get("/api/v1/websites?is_active=true", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["is_active"] is True


def test_filter_inactive_websites(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Website list can be filtered on inactive websites."""

    _create_website(client, name="Site actif", url="https://active.example.com", is_active=True, headers=admin_headers)
    _create_website(
        client,
        name="Site inactif",
        url="https://inactive.example.com",
        is_active=False,
        headers=admin_headers,
    )

    response = client.get("/api/v1/websites?is_active=false", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["is_active"] is False


def test_update_website(client: TestClient, admin_headers: dict[str, str]) -> None:
    """A website can be updated."""

    created = _create_website(client, headers=admin_headers)

    response = client.put(
        f"/api/v1/websites/{created['id']}",
        headers=admin_headers,
        json={"name": "Site modifie", "cms": "Drupal", "is_active": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Site modifie"
    assert data["cms"] == "Drupal"
    assert data["is_active"] is False


def test_delete_website(client: TestClient, admin_headers: dict[str, str]) -> None:
    """A website can be deleted."""

    created = _create_website(client, headers=admin_headers)

    delete_response = client.delete(f"/api/v1/websites/{created['id']}", headers=admin_headers)
    get_response = client.get(f"/api/v1/websites/{created['id']}", headers=admin_headers)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_duplicate_url_returns_409(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Duplicate website URLs are rejected."""

    _create_website(client, name="Site A", url="https://duplicate.example.com", headers=admin_headers)

    response = client.post(
        "/api/v1/websites",
        headers=admin_headers,
        json={"name": "Site B", "url": "https://duplicate.example.com"},
    )

    assert response.status_code == 409


def test_unknown_website_returns_404(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Unknown website ids return 404."""

    response = client.get("/api/v1/websites/999", headers=admin_headers)

    assert response.status_code == 404


def test_websites_reject_anonymous_user(client: TestClient) -> None:
    """Website routes require a JWT."""

    responses = [
        client.get("/api/v1/websites"),
        client.get("/api/v1/websites/999"),
        client.post("/api/v1/websites", json={"name": "Site", "url": "https://site.example.com"}),
        client.put("/api/v1/websites/999", json={"name": "Site modifie"}),
        client.delete("/api/v1/websites/999"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401]


def test_websites_reject_user_without_permission(
    client: TestClient,
    auth_headers_for: AuthHeadersFactory,
) -> None:
    """Website routes reject authenticated users without the required permission."""

    headers = auth_headers_for()
    responses = [
        client.get("/api/v1/websites", headers=headers),
        client.get("/api/v1/websites/999", headers=headers),
        client.post(
            "/api/v1/websites",
            headers=headers,
            json={"name": "Site", "url": "https://site.example.com"},
        ),
        client.put("/api/v1/websites/999", headers=headers, json={"name": "Site modifie"}),
        client.delete("/api/v1/websites/999", headers=headers),
    ]

    assert [response.status_code for response in responses] == [403, 403, 403, 403, 403]


def test_websites_enforce_operation_permissions(
    client: TestClient,
    auth_headers_for: AuthHeadersFactory,
) -> None:
    """Website routes require read, write and delete permissions per operation."""

    read_headers = auth_headers_for(permission_codes=["website.read"])
    write_headers = auth_headers_for(permission_codes=["website.write"])
    delete_headers = auth_headers_for(permission_codes=["website.delete"])

    assert client.get("/api/v1/websites", headers=write_headers).status_code == 403
    assert client.get("/api/v1/websites/999", headers=delete_headers).status_code == 403
    assert (
        client.post(
            "/api/v1/websites",
            headers=read_headers,
            json={"name": "Site", "url": "https://site.example.com"},
        ).status_code
        == 403
    )
    assert client.put("/api/v1/websites/999", headers=read_headers, json={"name": "Site modifie"}).status_code == 403
    assert client.delete("/api/v1/websites/999", headers=write_headers).status_code == 403


def test_websites_allow_user_with_permissions(
    client: TestClient,
    auth_headers_for: AuthHeadersFactory,
) -> None:
    """Website routes allow users with read, write and delete permissions."""

    headers = auth_headers_for(permission_codes=["website.read", "website.write", "website.delete"])

    create_response = client.post(
        "/api/v1/websites",
        headers=headers,
        json={"name": "Site permissions", "url": "https://permissions.example.com"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    list_response = client.get("/api/v1/websites", headers=headers)
    get_response = client.get(f"/api/v1/websites/{created['id']}", headers=headers)
    update_response = client.put(
        f"/api/v1/websites/{created['id']}",
        headers=headers,
        json={"name": "Site permissions modifie"},
    )
    delete_response = client.delete(f"/api/v1/websites/{created['id']}", headers=headers)
    missing_response = client.get(f"/api/v1/websites/{created['id']}", headers=headers)

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert delete_response.status_code == 204
    assert missing_response.status_code == 404
