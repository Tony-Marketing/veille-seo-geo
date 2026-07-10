"""Tests for alerts administration routes."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.api.v1.routes import alerts
from backend.app.core.security import create_access_token, hash_password
from backend.app.models import User


def _headers_for_user(db_session: Session) -> dict[str, str]:
    user = User(
        email="alerts-user@example.com",
        password_hash=hash_password("Password123"),
        is_active=True,
        is_superadmin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _alert_payload(status: str = "Active") -> dict[str, object]:
    now = datetime(2026, 7, 10, 8, 0, tzinfo=UTC).isoformat()
    return {
        "id": 1,
        "source_type": "GSC",
        "source_id": "event-1",
        "category": "sync",
        "severity": "Warning",
        "status": status,
        "title": "Warning - GSC - sync",
        "message": "Import en retard",
        "metadata": {"schedule_id": 1},
        "deduplication_key": "monitoring:sync:GSC:Import en retard",
        "first_seen_at": now,
        "last_seen_at": now,
        "acknowledged_at": now if status == "Acknowledged" else None,
        "acknowledged_by_user_id": 1 if status == "Acknowledged" else None,
        "resolved_at": now if status == "Resolved" else None,
        "created_at": now,
        "updated_at": now,
    }


class FakeAlertService:
    """Route service stub."""

    def list_alerts(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_alert_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def get_alert(self, alert_id: int) -> dict[str, object]:
        return _alert_payload()

    def refresh_from_monitoring(self) -> dict[str, object]:
        return {"created": 1, "updated": 0, "total_processed": 1, "alerts": [_alert_payload()]}

    def acknowledge_alert(self, alert_id: int, *, user_id: int | None = None) -> dict[str, object]:
        return _alert_payload(status="Acknowledged")

    def resolve_alert(self, alert_id: int) -> dict[str, object]:
        return _alert_payload(status="Resolved")

    def summary(self) -> dict[str, object]:
        return {
            "total": 1,
            "active": 1,
            "acknowledged": 0,
            "resolved": 0,
            "info": 0,
            "warning": 1,
            "critical": 0,
            "last_alert_at": datetime(2026, 7, 10, 8, 0, tzinfo=UTC).isoformat(),
        }


def test_alerts_routes_reject_anonymous_user(client: TestClient) -> None:
    """Alert routes require authentication."""

    responses = [
        client.get("/api/v1/alerts"),
        client.get("/api/v1/alerts/1"),
        client.post("/api/v1/alerts/refresh-from-monitoring"),
        client.post("/api/v1/alerts/1/acknowledge"),
        client.post("/api/v1/alerts/1/resolve"),
        client.get("/api/v1/alerts/summary"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401, 401]


def test_alerts_routes_reject_non_admin(client: TestClient, db_session: Session) -> None:
    """Alert routes require administrator rights."""

    response = client.get("/api/v1/alerts", headers=_headers_for_user(db_session))

    assert response.status_code == 403


def test_alerts_routes_allow_admin(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Alert routes allow superadmin users."""

    client.app.dependency_overrides[alerts.get_service] = lambda: FakeAlertService()
    try:
        alert_list = client.get(
            "/api/v1/alerts?status=Active&severity=Warning&category=sync&source=GSC",
            headers=admin_headers,
        )
        detail = client.get("/api/v1/alerts/1", headers=admin_headers)
        refresh = client.post("/api/v1/alerts/refresh-from-monitoring", headers=admin_headers)
        acknowledged = client.post("/api/v1/alerts/1/acknowledge", headers=admin_headers)
        resolved = client.post("/api/v1/alerts/1/resolve", headers=admin_headers)
        summary = client.get("/api/v1/alerts/summary", headers=admin_headers)

        assert alert_list.status_code == 200
        assert alert_list.json()["items"][0]["severity"] == "Warning"
        assert detail.status_code == 200
        assert refresh.json()["created"] == 1
        assert acknowledged.json()["status"] == "Acknowledged"
        assert resolved.json()["status"] == "Resolved"
        assert summary.json()["warning"] == 1
    finally:
        client.app.dependency_overrides.pop(alerts.get_service, None)
