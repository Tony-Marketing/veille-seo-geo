"""Standalone scheduler loop for processing orchestration."""

from collections.abc import Callable
from time import sleep

from backend.app.core.database import SessionLocal
from backend.app.repositories.alerts import AlertRepository
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.repositories.orchestration import OrchestrationRepository
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.services.orchestration import OrchestrationService


def run_scheduler_once() -> object:
    """Run one scheduler cycle outside FastAPI."""

    with SessionLocal() as db:
        service = OrchestrationService(
            OrchestrationRepository(db),
            SyncScheduleRepository(db),
            MonitoringRepository(db),
            AlertRepository(db),
        )
        return service.run_scheduler_once()


def run_scheduler_loop(*, interval_seconds: int = 60, stop_requested: Callable[[], bool] | None = None) -> None:
    """Run scheduler cycles until stop_requested returns True."""

    should_stop = stop_requested or (lambda: False)
    while not should_stop():
        run_scheduler_once()
        sleep(interval_seconds)

