"""Tests for monitoring administration routes."""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.api.v1.routes import monitoring
from backend.app.core.security import create_access_token, hash_password
from backend.app.models import User


def _headers_for_user(db_session: Session) -> dict[str, str]:
    user = User(
        email="monitoring-user@example.com",
        password_hash=hash_password("Password123"),
        is_active=True,
        is_superadmin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _event_payload() -> dict[str, object]:
    now = datetime(2026, 7, 9, 8, 0, tzinfo=UTC).isoformat()
    return {
        "id": str(uuid4()),
        "event_type": "sync",
        "severity": "warning",
        "source": "GSC",
        "message": "Import en retard",
        "details": {"schedule_id": 1},
        "created_at": now,
    }


def _schedule_payload() -> dict[str, object]:
    return {
        "id": 1,
        "name": "Import GSC",
        "sync_type": "GSC",
        "frequency": "Quotidien",
        "status": "Active",
        "is_active": True,
        "last_run_at": None,
        "last_run_status": None,
        "last_run_message": None,
        "next_run_at": datetime(2026, 7, 10, 8, 0, tzinfo=UTC).isoformat(),
    }


class FakeMonitoringService:
    """Route service stub."""

    def overview(self) -> dict[str, object]:
        return {
            "total_events": 1,
            "events_today": 1,
            "warning_events": 1,
            "error_events": 0,
            "critical_events": 0,
            "active_sync_schedules": 1,
            "inactive_sync_schedules": 0,
            "next_runs": [_schedule_payload()],
            "last_event": _event_payload(),
        }

    def list_events(self, params: object, *, severity: object | None = None, event_type: object | None = None) -> dict:
        return {"items": [_event_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def list_connectors(self) -> list[dict[str, object]]:
        return [
            {
                "name": "Google Search Console",
                "status": "operational",
                "enabled": True,
                "last_sync": None,
                "next_sync": None,
            },
        ]

    def list_sync_schedules(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_schedule_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}


def test_monitoring_routes_reject_anonymous_user(client: TestClient) -> None:
    """Monitoring routes require authentication."""

    responses = [
        client.get("/api/v1/admin/monitoring/overview"),
        client.get("/api/v1/admin/monitoring/events"),
        client.get("/api/v1/admin/monitoring/connectors"),
        client.get("/api/v1/admin/monitoring/sync-schedules"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401]


def test_monitoring_routes_reject_non_admin(client: TestClient, db_session: Session) -> None:
    """Monitoring routes require administrator rights."""

    headers = _headers_for_user(db_session)

    response = client.get("/api/v1/admin/monitoring/overview", headers=headers)

    assert response.status_code == 403


def test_monitoring_routes_allow_admin(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Monitoring routes allow superadmin users."""

    client.app.dependency_overrides[monitoring.get_service] = lambda: FakeMonitoringService()
    try:
        overview = client.get("/api/v1/admin/monitoring/overview", headers=admin_headers)
        events = client.get(
            "/api/v1/admin/monitoring/events?severity=warning&event_type=sync",
            headers=admin_headers,
        )
        connectors = client.get("/api/v1/admin/monitoring/connectors", headers=admin_headers)
        schedules = client.get("/api/v1/admin/monitoring/sync-schedules", headers=admin_headers)

        assert overview.status_code == 200
        assert overview.json()["total_events"] == 1
        assert events.status_code == 200
        assert events.json()["items"][0]["severity"] == "warning"
        assert connectors.status_code == 200
        assert connectors.json()[0]["name"] == "Google Search Console"
        assert schedules.status_code == 200
        assert schedules.json()["items"][0]["sync_type"] == "GSC"
    finally:
        client.app.dependency_overrides.pop(monitoring.get_service, None)
