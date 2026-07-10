"""Tests for orchestration administration routes."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.api.v1.routes import orchestration
from backend.app.core.security import create_access_token, hash_password
from backend.app.models import User


def _headers_for_user(db_session: Session) -> dict[str, str]:
    user = User(
        email="orchestration-user@example.com",
        password_hash=hash_password("Password123"),
        is_active=True,
        is_superadmin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _job_payload(status: str = "pending") -> dict[str, object]:
    now = datetime(2026, 7, 10, 8, 0, tzinfo=UTC).isoformat()
    return {
        "id": 1,
        "schedule_id": 1,
        "job_type": "gsc",
        "status": status,
        "priority": 100,
        "payload": {"target_id": "1"},
        "idempotency_key": "schedule:1:gsc:2026-07-10T08:00:00+00:00",
        "attempts": 0,
        "max_attempts": 3,
        "available_at": now,
        "reserved_at": None,
        "started_at": None,
        "finished_at": None,
        "failed_at": None,
        "message": "Job cree.",
        "details": None,
        "worker_id": None,
        "lock_expires_at": None,
        "monitoring_event_id": None,
        "created_at": now,
        "updated_at": now,
    }


class FakeOrchestrationService:
    """Route service stub."""

    def list_jobs(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_job_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def get_job(self, job_id: int) -> dict[str, object]:
        return _job_payload()

    def list_job_logs(self, job_id: int, params: object) -> dict[str, object]:
        now = datetime(2026, 7, 10, 8, 0, tzinfo=UTC).isoformat()
        return {
            "items": [
                {
                    "id": 1,
                    "job_id": job_id,
                    "level": "info",
                    "event": "created",
                    "message": "Cree.",
                    "context": {},
                    "created_at": now,
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
            "filters": {},
        }

    def retry_job(self, job_id: int) -> dict[str, object]:
        return _job_payload(status="retry_scheduled")

    def cancel_job(self, job_id: int) -> dict[str, object]:
        return _job_payload(status="cancelled")

    def summary(self) -> dict[str, object]:
        return {"pending": 1, "total": 1, "active_workers": 0}

    def list_workers(self) -> list[dict[str, object]]:
        now = datetime(2026, 7, 10, 8, 0, tzinfo=UTC).isoformat()
        return [
            {
                "id": 1,
                "worker_id": "worker-1",
                "status": "idle",
                "last_heartbeat_at": now,
                "current_job_id": None,
                "version": None,
                "metadata": None,
                "created_at": now,
                "updated_at": now,
            },
        ]

    def run_scheduler_once(self) -> dict[str, object]:
        return {"scanned": 1, "created": 1, "skipped": 0, "errors": 0, "jobs": [_job_payload()]}


def test_orchestration_routes_reject_anonymous_user(client: TestClient) -> None:
    """Orchestration routes require authentication."""

    responses = [
        client.get("/api/v1/orchestration/jobs"),
        client.get("/api/v1/orchestration/jobs/1"),
        client.get("/api/v1/orchestration/jobs/1/logs"),
        client.post("/api/v1/orchestration/jobs/1/retry"),
        client.post("/api/v1/orchestration/jobs/1/cancel"),
        client.get("/api/v1/orchestration/summary"),
        client.get("/api/v1/orchestration/workers"),
        client.post("/api/v1/orchestration/scheduler/run-once"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401, 401, 401, 401]


def test_orchestration_routes_reject_non_admin(client: TestClient, db_session: Session) -> None:
    """Orchestration routes require administrator rights."""

    response = client.get("/api/v1/orchestration/jobs", headers=_headers_for_user(db_session))

    assert response.status_code == 403


def test_orchestration_routes_allow_admin(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Orchestration routes allow superadmin users."""

    client.app.dependency_overrides[orchestration.get_service] = lambda: FakeOrchestrationService()
    try:
        jobs = client.get("/api/v1/orchestration/jobs?status=pending&job_type=gsc", headers=admin_headers)
        detail = client.get("/api/v1/orchestration/jobs/1", headers=admin_headers)
        logs = client.get("/api/v1/orchestration/jobs/1/logs", headers=admin_headers)
        retry = client.post("/api/v1/orchestration/jobs/1/retry", headers=admin_headers)
        cancel = client.post("/api/v1/orchestration/jobs/1/cancel", headers=admin_headers)
        summary = client.get("/api/v1/orchestration/summary", headers=admin_headers)
        workers = client.get("/api/v1/orchestration/workers", headers=admin_headers)
        scheduler = client.post("/api/v1/orchestration/scheduler/run-once", headers=admin_headers)

        assert jobs.status_code == 200
        assert jobs.json()["items"][0]["job_type"] == "gsc"
        assert detail.status_code == 200
        assert logs.json()["items"][0]["event"] == "created"
        assert retry.json()["status"] == "retry_scheduled"
        assert cancel.json()["status"] == "cancelled"
        assert summary.json()["pending"] == 1
        assert workers.json()[0]["worker_id"] == "worker-1"
        assert scheduler.json()["created"] == 1
    finally:
        client.app.dependency_overrides.pop(orchestration.get_service, None)
