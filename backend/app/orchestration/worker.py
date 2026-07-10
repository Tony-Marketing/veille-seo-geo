"""Standalone worker loop for processing orchestration."""

from collections.abc import Callable
from time import sleep
from uuid import uuid4

from backend.app.core.database import SessionLocal
from backend.app.repositories.alerts import AlertRepository
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.repositories.orchestration import OrchestrationRepository
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.services.orchestration import OrchestrationService


def run_worker_once(*, worker_id: str | None = None) -> object | None:
    """Reserve and run one available job outside FastAPI."""

    logical_worker_id = worker_id or f"worker-{uuid4().hex}"
    with SessionLocal() as db:
        service = OrchestrationService(
            OrchestrationRepository(db),
            SyncScheduleRepository(db),
            MonitoringRepository(db),
            AlertRepository(db),
        )
        return service.run_next_job(worker_id=logical_worker_id)


def run_worker_loop(
    *,
    worker_id: str | None = None,
    idle_sleep_seconds: int = 5,
    stop_requested: Callable[[], bool] | None = None,
) -> None:
    """Run jobs until stop_requested returns True."""

    logical_worker_id = worker_id or f"worker-{uuid4().hex}"
    should_stop = stop_requested or (lambda: False)
    while not should_stop():
        result = run_worker_once(worker_id=logical_worker_id)
        if result is None:
            sleep(idle_sleep_seconds)
