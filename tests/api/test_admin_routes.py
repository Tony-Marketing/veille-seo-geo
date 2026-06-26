"""Tests des routes REST d'administration."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.core.security import create_access_token, hash_password
from backend.app.models import User


def _headers_for_user(db_session: Session, *, is_superadmin: bool = False) -> dict[str, str]:
    user = User(
        email=f"user-{is_superadmin}@example.com",
        password_hash=hash_password("Password123"),
        is_active=True,
        is_superadmin=is_superadmin,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


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


def test_user_role_permission_routes_reject_anonymous(client: TestClient) -> None:
    """Administration CRUD routes require authentication."""

    for path in ("/api/v1/users", "/api/v1/roles", "/api/v1/permissions"):
        response = client.get(path)

        assert response.status_code == 401


def test_user_role_permission_routes_reject_non_admin(client: TestClient, db_session: Session) -> None:
    """Administration CRUD routes reject authenticated non-admin users."""

    headers = _headers_for_user(db_session)
    for path in ("/api/v1/users", "/api/v1/roles", "/api/v1/permissions"):
        response = client.get(path, headers=headers)

        assert response.status_code == 403


def test_user_role_permission_routes_allow_admin(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Administration CRUD routes allow superadmin users."""

    for path in ("/api/v1/users", "/api/v1/roles", "/api/v1/permissions"):
        response = client.get(path, headers=admin_headers)

        assert response.status_code == 200


def test_configuration_import_and_export(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Configuration can be imported idempotently and exported."""

    payload = {
        "settings": [{"key": "app.timezone", "value": "Europe/Paris", "category": "global", "is_public": True}],
        "ai_providers": [{"name": "OpenAI", "default_model": "gpt-4o", "is_active": True}],
        "ai_models": [{"provider_id": 1, "name": "GPT-4o", "api_identifier": "gpt-4o", "is_active": True}],
        "system_parameters": [{"category": "seo", "key": "crawler.user_agent", "value": "VeilleBot"}],
        "permissions": [{"code": "admin.read", "label": "Lire administration", "module": "admin"}],
        "roles": [
            {
                "name": "Administrateur",
                "description": "Acces complet",
                "is_system": True,
                "permissions": [{"code": "admin.read", "label": "Lire administration", "module": "admin"}],
            },
        ],
    }

    import_response = client.post("/api/v1/admin/config/import", headers=admin_headers, json=payload)
    export_response = client.get("/api/v1/admin/config/export", headers=admin_headers)
    second_import_response = client.post("/api/v1/admin/config/import", headers=admin_headers, json=payload)

    assert import_response.status_code == 200
    assert export_response.status_code == 200
    assert second_import_response.status_code == 200
    assert import_response.json()["created"]["settings"] == 1
    assert second_import_response.json()["updated"]["settings"] == 1
    exported = export_response.json()
    assert exported["settings"][0]["key"] == "app.timezone"
    assert exported["ai_providers"][0]["name"] == "OpenAI"


def test_administration_migration_is_explicit() -> None:
    """Alembic migration must not rely on global metadata create/drop helpers."""

    migration = Path("backend/alembic/versions/20260626_0001_create_administration_backend.py").read_text(
        encoding="utf-8",
    )

    assert "Base.metadata.create_all" not in migration
    assert "Base.metadata.drop_all" not in migration
    assert "op.create_table" in migration
    assert "op.drop_table" in migration
