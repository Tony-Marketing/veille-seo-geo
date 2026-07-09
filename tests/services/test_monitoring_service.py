"""Tests for MonitoringService."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import GoogleSearchConsoleProperty, SyncSchedule
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.monitoring import MonitoringEventType, MonitoringSeverity
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.sync_schedules import SyncFrequency, SyncScheduleFilters, SyncScheduleStatus, SyncType
from backend.app.services.monitoring import MonitoringService
from backend.app.services.sync_schedules import SyncScheduleService


def _service(db_session: Session) -> MonitoringService:
    sync_repository = SyncScheduleRepository(db_session)
    return MonitoringService(
        MonitoringRepository(db_session),
        SyncScheduleService(sync_repository),
        now_provider=lambda: datetime(2026, 7, 9, 12, 0, tzinfo=UTC),
    )


def test_monitoring_service_returns_overview(db_session: Session) -> None:
    """The service aggregates events and synchronization schedules."""

    repository = MonitoringRepository(db_session)
    repository.create_event(
        {
            "event_type": "sync",
            "severity": "critical",
            "source": "GSC",
            "message": "Echec import",
            "created_at": datetime(2026, 7, 9, 8, 0, tzinfo=UTC),
        },
    )
    db_session.add(
        SyncSchedule(
            name="Import GSC",
            sync_type=SyncType.GSC.value,
            frequency=SyncFrequency.DAILY.value,
            status=SyncScheduleStatus.ACTIVE.value,
            is_active=True,
            next_run_at=datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
        ),
    )
    db_session.add(
        SyncSchedule(
            name="Import GA4",
            sync_type=SyncType.GA4.value,
            frequency=SyncFrequency.MANUAL.value,
            status=SyncScheduleStatus.DISABLED.value,
            is_active=False,
        ),
    )
    db_session.commit()

    overview = _service(db_session).overview()

    assert overview.total_events == 1
    assert overview.events_today == 1
    assert overview.critical_events == 1
    assert overview.active_sync_schedules == 1
    assert overview.inactive_sync_schedules == 1
    assert overview.next_runs[0].name == "Import GSC"
    assert overview.last_event is not None


def test_monitoring_service_lists_events_with_filters(db_session: Session) -> None:
    """The service returns paginated filtered events."""

    MonitoringRepository(db_session).create_event(
        {
            "event_type": "connector",
            "severity": "warning",
            "source": "Bing",
            "message": "A surveiller",
            "created_at": datetime(2026, 7, 9, 8, 0, tzinfo=UTC),
        },
    )

    result = _service(db_session).list_events(
        PaginationParams(page=1, page_size=10),
        severity=MonitoringSeverity.WARNING,
        event_type=MonitoringEventType.CONNECTOR,
    )

    assert result.total == 1
    assert result.items[0].source == "Bing"
    assert result.filters == {"severity": "warning", "event_type": "connector"}


def test_monitoring_service_returns_connector_health_and_schedules(db_session: Session) -> None:
    """Connector health and schedules are read-only projections."""

    db_session.add(
        GoogleSearchConsoleProperty(
            google_property_id="sc-domain:example.com",
            property_url="https://example.com",
            is_active=True,
        ),
    )
    db_session.add(
        SyncSchedule(
            name="Import GSC",
            sync_type=SyncType.GSC.value,
            frequency=SyncFrequency.DAILY.value,
            status=SyncScheduleStatus.ACTIVE.value,
            is_active=True,
            next_run_at=datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
        ),
    )
    db_session.commit()

    service = _service(db_session)
    connectors = service.list_connectors()
    schedules = service.list_sync_schedules(
        PaginationParams(page=1, page_size=10),
        filters=SyncScheduleFilters(sync_type=SyncType.GSC),
    )

    assert connectors[0].name == "Google Search Console"
    assert connectors[0].status == "operational"
    assert connectors[0].enabled is True
    assert connectors[0].next_sync is not None
    assert schedules.total == 1
    assert schedules.items[0].sync_type == SyncType.GSC
