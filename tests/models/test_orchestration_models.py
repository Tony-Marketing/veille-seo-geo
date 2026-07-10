"""Tests for processing orchestration models."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import ProcessingJob, ProcessingJobLog, ProcessingWorker


def test_processing_models_persist_relationships(db_session: Session) -> None:
    """Processing jobs, logs and workers are persisted with expected fields."""

    job = ProcessingJob(
        job_type="gsc",
        status="pending",
        priority=100,
        payload={"target_id": "1"},
        idempotency_key="schedule:1:gsc:2026-07-10T08:00:00+00:00",
        attempts=0,
        max_attempts=3,
        available_at=datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    log = ProcessingJobLog(job_id=job.id, level="info", event="created", message="Job cree.")
    worker = ProcessingWorker(
        worker_id="worker-1",
        status="idle",
        last_heartbeat_at=datetime(2026, 7, 10, 8, 1, tzinfo=UTC),
        current_job_id=job.id,
    )
    db_session.add_all([log, worker])
    db_session.commit()
    db_session.refresh(job)

    assert job.id is not None
    assert job.logs[0].event == "created"
    assert worker.current_job_id == job.id

