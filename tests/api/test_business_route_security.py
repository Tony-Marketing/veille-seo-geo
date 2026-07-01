"""Tests de securisation des routes metier CRUD."""

from collections.abc import Callable
from copy import deepcopy
from typing import Any

import pytest
from fastapi.testclient import TestClient

AuthHeadersFactory = Callable[..., dict[str, str]]
CRUD_PARAM_NAMES = ("path", "read_permission", "write_permission", "delete_permission", "payload", "update")

CRUD_CASES: list[tuple[str, str, str, str, dict[str, Any], dict[str, Any]]] = [
    (
        "/api/v1/entities",
        "entity.read",
        "entity.write",
        "entity.delete",
        {"name": "Entite test"},
        {"name": "Entite test modifiee"},
    ),
    (
        "/api/v1/keywords",
        "keyword.read",
        "keyword.write",
        "keyword.delete",
        {"term": "audit seo"},
        {"term": "audit geo"},
    ),
    (
        "/api/v1/competitors",
        "competitor.read",
        "competitor.write",
        "competitor.delete",
        {"name": "Concurrent test"},
        {"name": "Concurrent test modifie"},
    ),
    (
        "/api/v1/urls",
        "url.read",
        "url.write",
        "url.delete",
        {"url": "https://example.com/page"},
        {"url": "https://example.com/page-modifiee"},
    ),
    (
        "/api/v1/reports",
        "report.read",
        "report.write",
        "report.delete",
        {"title": "Rapport test"},
        {"title": "Rapport test modifie"},
    ),
    (
        "/api/v1/project-tasks",
        "project_task.read",
        "project_task.write",
        "project_task.delete",
        {"title": "Tache test"},
        {"title": "Tache test modifiee"},
    ),
]


@pytest.mark.parametrize(CRUD_PARAM_NAMES, CRUD_CASES)
def test_business_routes_reject_anonymous_user(
    client: TestClient,
    path: str,
    read_permission: str,
    write_permission: str,
    delete_permission: str,
    payload: dict[str, Any],
    update: dict[str, Any],
) -> None:
    """Business CRUD routes require a JWT."""

    responses = [
        client.get(path),
        client.get(f"{path}/999"),
        client.post(path, json=payload),
        client.put(f"{path}/999", json=update),
        client.delete(f"{path}/999"),
    ]

    assert read_permission
    assert write_permission
    assert delete_permission
    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401]


@pytest.mark.parametrize(CRUD_PARAM_NAMES, CRUD_CASES)
def test_business_routes_reject_user_without_permission(
    client: TestClient,
    auth_headers_for: AuthHeadersFactory,
    path: str,
    read_permission: str,
    write_permission: str,
    delete_permission: str,
    payload: dict[str, Any],
    update: dict[str, Any],
) -> None:
    """Business CRUD routes reject authenticated users without permissions."""

    headers = auth_headers_for()
    responses = [
        client.get(path, headers=headers),
        client.get(f"{path}/999", headers=headers),
        client.post(path, headers=headers, json=payload),
        client.put(f"{path}/999", headers=headers, json=update),
        client.delete(f"{path}/999", headers=headers),
    ]

    assert read_permission
    assert write_permission
    assert delete_permission
    assert [response.status_code for response in responses] == [403, 403, 403, 403, 403]


@pytest.mark.parametrize(CRUD_PARAM_NAMES, CRUD_CASES)
def test_business_routes_enforce_operation_permissions(
    client: TestClient,
    auth_headers_for: AuthHeadersFactory,
    path: str,
    read_permission: str,
    write_permission: str,
    delete_permission: str,
    payload: dict[str, Any],
    update: dict[str, Any],
) -> None:
    """Business CRUD routes require the permission matching each operation."""

    read_headers = auth_headers_for(permission_codes=[read_permission])
    write_headers = auth_headers_for(permission_codes=[write_permission])
    delete_headers = auth_headers_for(permission_codes=[delete_permission])

    assert client.get(path, headers=write_headers).status_code == 403
    assert client.get(f"{path}/999", headers=delete_headers).status_code == 403
    assert client.post(path, headers=read_headers, json=payload).status_code == 403
    assert client.put(f"{path}/999", headers=read_headers, json=update).status_code == 403
    assert client.delete(f"{path}/999", headers=write_headers).status_code == 403


@pytest.mark.parametrize(CRUD_PARAM_NAMES, CRUD_CASES)
def test_business_routes_allow_user_with_permissions(
    client: TestClient,
    auth_headers_for: AuthHeadersFactory,
    path: str,
    read_permission: str,
    write_permission: str,
    delete_permission: str,
    payload: dict[str, Any],
    update: dict[str, Any],
) -> None:
    """Business CRUD routes allow users with matching read, write and delete permissions."""

    headers = auth_headers_for(permission_codes=[read_permission, write_permission, delete_permission])

    create_response = client.post(path, headers=headers, json=deepcopy(payload))
    assert create_response.status_code == 201
    created = create_response.json()

    list_response = client.get(path, headers=headers)
    get_response = client.get(f"{path}/{created['id']}", headers=headers)
    update_response = client.put(f"{path}/{created['id']}", headers=headers, json=deepcopy(update))
    delete_response = client.delete(f"{path}/{created['id']}", headers=headers)
    missing_response = client.get(f"{path}/{created['id']}", headers=headers)

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


@pytest.mark.parametrize(CRUD_PARAM_NAMES, CRUD_CASES)
def test_business_routes_allow_superadmin(
    client: TestClient,
    admin_headers: dict[str, str],
    path: str,
    read_permission: str,
    write_permission: str,
    delete_permission: str,
    payload: dict[str, Any],
    update: dict[str, Any],
) -> None:
    """Business CRUD routes allow superadmin users through the existing bypass."""

    create_response = client.post(path, headers=admin_headers, json=deepcopy(payload))
    assert create_response.status_code == 201
    created = create_response.json()

    list_response = client.get(path, headers=admin_headers)
    get_response = client.get(f"{path}/{created['id']}", headers=admin_headers)
    update_response = client.put(f"{path}/{created['id']}", headers=admin_headers, json=deepcopy(update))
    delete_response = client.delete(f"{path}/{created['id']}", headers=admin_headers)
    missing_response = client.get(f"{path}/{created['id']}", headers=admin_headers)

    assert read_permission
    assert write_permission
    assert delete_permission
    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert delete_response.status_code == 204
    assert missing_response.status_code == 404
