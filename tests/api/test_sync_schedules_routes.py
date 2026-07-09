"""Tests for synchronization schedule routes."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.api.v1.routes import sync_schedules
from backend.app.core.security import create_access_token, hash_password
from backend.app.models import User


def _headers_for_user(db_session: Session) -> dict[str, str]:
    user = User(
        email="sync-user@example.com",
        password_hash=hash_password("Password123"),
        is_active=True,
        is_superadmin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _schedule_payload(schedule_id: int = 1) -> dict[str, object]:
    now = datetime(2026, 7, 9, 8, 0, tzinfo=UTC).isoformat()
    return {
        "id": schedule_id,
        "name": "Import GSC",
        "description": None,
        "sync_type": "GSC",
        "frequency": "Quotidien",
        "status": "Active",
        "is_active": True,
        "website_id": None,
        "target_id": None,
        "target_type": None,
        "last_run_at": None,
        "last_run_status": None,
        "last_run_message": None,
        "next_run_at": now,
        "timezone": "Europe/Paris",
        "created_by_user_id": 1,
        "updated_by_user_id": 1,
        "created_at": now,
        "updated_at": now,
    }


class FakeSyncScheduleService:
    """Route service stub."""

    def list_schedules(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_schedule_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def create_schedule(self, payload: object, *, user_id: int | None = None) -> dict[str, object]:
        return _schedule_payload()

    def get_schedule(self, schedule_id: int) -> dict[str, object]:
        return _schedule_payload(schedule_id)

    def update_schedule(self, schedule_id: int, payload: object, *, user_id: int | None = None) -> dict[str, object]:
        return _schedule_payload(schedule_id)

    def delete_schedule(self, schedule_id: int, *, user_id: int | None = None) -> None:
        return None

    def enable_schedule(self, schedule_id: int, *, user_id: int | None = None) -> dict[str, object]:
        return _schedule_payload(schedule_id)

    def disable_schedule(self, schedule_id: int, *, user_id: int | None = None) -> dict[str, object]:
        payload = _schedule_payload(schedule_id)
        payload["is_active"] = False
        payload["status"] = "Desactivee"
        payload["next_run_at"] = None
        return payload

    def recalculate_schedule(self, schedule_id: int, *, user_id: int | None = None) -> dict[str, object]:
        return _schedule_payload(schedule_id)


def test_sync_schedule_routes_reject_anonymous_user(client: TestClient) -> None:
    """Synchronization schedule routes require authentication."""

    responses = [
        client.get("/api/v1/sync-schedules"),
        client.post("/api/v1/sync-schedules", json={}),
        client.get("/api/v1/sync-schedules/1"),
        client.patch("/api/v1/sync-schedules/1", json={}),
        client.delete("/api/v1/sync-schedules/1"),
        client.post("/api/v1/sync-schedules/1/enable"),
        client.post("/api/v1/sync-schedules/1/disable"),
        client.post("/api/v1/sync-schedules/1/recalculate"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401, 401, 401, 401]


def test_sync_schedule_routes_reject_non_admin(client: TestClient, db_session: Session) -> None:
    """Synchronization schedule routes require administrator rights."""

    headers = _headers_for_user(db_session)

    response = client.get("/api/v1/sync-schedules", headers=headers)

    assert response.status_code == 403


def test_sync_schedule_routes_allow_admin(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Synchronization schedule routes allow superadmin users."""

    client.app.dependency_overrides[sync_schedules.get_service] = lambda: FakeSyncScheduleService()
    try:
        assert client.get("/api/v1/sync-schedules", headers=admin_headers).status_code == 200
        create_response = client.post(
            "/api/v1/sync-schedules",
            headers=admin_headers,
            json={"name": "Import GSC", "sync_type": "GSC", "frequency": "Quotidien"},
        )
        assert create_response.status_code == 201
        assert client.get("/api/v1/sync-schedules/1", headers=admin_headers).status_code == 200
        assert client.patch("/api/v1/sync-schedules/1", headers=admin_headers, json={}).status_code == 200
        assert client.delete("/api/v1/sync-schedules/1", headers=admin_headers).status_code == 204
        assert client.post("/api/v1/sync-schedules/1/enable", headers=admin_headers).status_code == 200
        assert client.post("/api/v1/sync-schedules/1/disable", headers=admin_headers).status_code == 200
        assert client.post("/api/v1/sync-schedules/1/recalculate", headers=admin_headers).status_code == 200
    finally:
        client.app.dependency_overrides.pop(sync_schedules.get_service, None)

