"""Tests for processing orchestration repository."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.repositories.orchestration import OrchestrationRepository
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.pagination import PaginationParams


def _job_payload(now: datetime, *, status: str = "pending") -> dict[str, object]:
    return {
        "job_type": "gsc",
        "status": status,
        "priority": 100,
        "payload": {"target_id": "1"},
        "idempotency_key": f"job-{now.isoformat()}-{status}",
        "attempts": 0,
        "max_attempts": 3,
        "available_at": now,
    }


def _schedule_payload(now: datetime) -> dict[str, object]:
    return {
        "name": "Import GSC",
        "sync_type": "GSC",
        "frequency": "Quotidien",
        "status": "Active",
        "is_active": True,
        "target_id": "1",
        "target_type": "property",
        "next_run_at": now,
        "timezone": "Europe/Paris",
    }


def test_orchestration_repository_creates_lists_reserves_and_logs(db_session: Session) -> None:
    """The repository persists jobs, reserves the next job and stores logs."""

    now = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    repository = OrchestrationRepository(db_session)
    job = repository.create_job(_job_payload(now))
    reserved = repository.reserve_next_job(
        worker_id="worker-1",
        now=now,
        lock_expires_at=now + timedelta(minutes=15),
    )
    log = repository.create_log({"job_id": job.id, "level": "info", "event": "reserved", "message": "Reserve."})
    logs, total_logs = repository.list_logs(job.id, PaginationParams())
    items, total = repository.list_jobs(PaginationParams(), status="reserved")

    assert reserved is not None
    assert reserved.id == job.id
    assert reserved.worker_id == "worker-1"
    assert log.id is not None
    assert logs == [log]
    assert total_logs == 1
    assert items == [reserved]
    assert total == 1


def test_orchestration_repository_lists_due_schedules_and_workers(db_session: Session) -> None:
    """The repository returns due schedules and worker heartbeats."""

    now = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    schedule = SyncScheduleRepository(db_session).create_schedule(_schedule_payload(now))
    repository = OrchestrationRepository(db_session)
    worker = repository.upsert_worker(worker_id="worker-1", status="idle", last_heartbeat_at=now)
    due = repository.list_due_schedules(now)
    workers = repository.list_workers()

    assert due == [schedule]
    assert workers == [worker]


def test_orchestration_repository_rejects_unknown_sort(db_session: Session) -> None:
    """The repository rejects arbitrary sort fields."""

    repository = OrchestrationRepository(db_session)

    try:
        repository.list_jobs(PaginationParams(sort="not_allowed"))
    except ValueError as exc:
        assert "non autorise" in str(exc)
    else:
        raise AssertionError("Unknown sort should be rejected.")

