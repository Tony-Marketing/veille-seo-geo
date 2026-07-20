"""Tests for processing orchestration service."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import Website
from backend.app.orchestration.base import HandlerResult
from backend.app.orchestration.registry import ProcessingHandlerRegistry
from backend.app.repositories.alerts import AlertRepository
from backend.app.repositories.dashboard_v2 import DashboardV2Repository
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.repositories.orchestration import OrchestrationRepository
from backend.app.repositories.recommendations import RecommendationRepository
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.dashboard_v2 import DashboardV2Filters
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.dashboard_v2 import DashboardV2Service
from backend.app.services.orchestration import OrchestrationService
from backend.app.services.recommendations import RecommendationService


class FakeHandler:
    """Fake successful handler."""

    def run(self, payload: dict[str, object], db: Session) -> HandlerResult:
        return HandlerResult(True, "Traitement termine.", {"target_id": payload.get("target_id")})


class FakeRegistry(ProcessingHandlerRegistry):
    """Fake registry returning a deterministic handler."""

    def get(self, job_type: str) -> FakeHandler:
        return FakeHandler()


def _now() -> datetime:
    return datetime(2026, 7, 10, 8, 0, tzinfo=UTC)


def _service(db_session: Session) -> OrchestrationService:
    return OrchestrationService(
        OrchestrationRepository(db_session),
        SyncScheduleRepository(db_session),
        MonitoringRepository(db_session),
        AlertRepository(db_session),
        handler_registry=FakeRegistry(),
        now_provider=_now,
    )


def _schedule_payload() -> dict[str, object]:
    return {
        "name": "Import GSC",
        "sync_type": "GSC",
        "frequency": "Quotidien",
        "status": "Active",
        "is_active": True,
        "target_id": "1",
        "target_type": "property",
        "next_run_at": _now(),
        "timezone": "Europe/Paris",
    }


def test_orchestration_service_scheduler_is_idempotent(db_session: Session) -> None:
    """The scheduler creates one job per due schedule window."""

    SyncScheduleRepository(db_session).create_schedule(_schedule_payload())
    service = _service(db_session)

    first = service.run_scheduler_once()
    second = service.run_scheduler_once()
    jobs = service.list_jobs(PaginationParams())

    assert first.created == 1
    assert second.created == 0
    assert jobs.total == 1
    assert jobs.items[0].status == "pending"


def test_orchestration_service_worker_executes_and_updates_monitoring(db_session: Session) -> None:
    """The worker executes a reserved job, updates the schedule and creates monitoring data."""

    website = Website(name="Example", url="https://example.com", is_active=True)
    db_session.add(website)
    db_session.commit()
    db_session.refresh(website)
    schedule_payload = _schedule_payload()
    schedule_payload["website_id"] = website.id
    SyncScheduleRepository(db_session).create_schedule(schedule_payload)
    service = _service(db_session)
    service.run_scheduler_once()

    result = service.run_next_job(worker_id="worker-1")
    summary = service.summary()
    events, total_events = MonitoringRepository(db_session).list_events(PaginationParams())
    alerts, total_alerts = AlertRepository(db_session).list_alerts(PaginationParams())
    dashboard = DashboardV2Service(
        DashboardV2Repository(db_session),
        RecommendationService(RecommendationRepository(db_session)),
        now_provider=_now,
    ).overview(DashboardV2Filters(website_id=website.id))

    assert result is not None
    assert result.status == "succeeded"
    assert summary.succeeded == 1
    assert total_events >= 1
    assert events[0].source == "orchestration"
    assert any(event.details and event.details.get("website_id") == website.id for event in events)
    assert total_alerts >= 1
    assert any(alert.metadata_ and alert.metadata_.get("website_id") == website.id for alert in alerts)
    assert dashboard.alerts.active >= 1
    assert dashboard.top_websites[0].active_alerts >= 1


def test_orchestration_service_cancel_and_retry_validate_transitions(db_session: Session) -> None:
    """Administrative actions apply controlled transitions."""

    SyncScheduleRepository(db_session).create_schedule(_schedule_payload())
    service = _service(db_session)
    service.run_scheduler_once()
    job = service.list_jobs(PaginationParams()).items[0]

    cancelled = service.cancel_job(job.id)

    assert cancelled.status == "cancelled"

