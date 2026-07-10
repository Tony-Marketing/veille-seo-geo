"""Tests for AlertService."""

from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.repositories.alerts import AlertRepository
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.schemas.alerts import AlertFilters, AlertSeverity, AlertStatus
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.alerts import AlertService


def _service(db_session: Session) -> AlertService:
    return AlertService(
        AlertRepository(db_session),
        MonitoringRepository(db_session),
        now_provider=lambda: datetime(2026, 7, 10, 12, 0, tzinfo=UTC),
    )


def _monitoring_event(
    db_session: Session,
    *,
    severity: str = "warning",
    source: str = "GSC",
    message: str = "Import en retard",
) -> None:
    MonitoringRepository(db_session).create_event(
        {
            "event_type": "sync",
            "severity": severity,
            "source": source,
            "message": message,
            "details": {"schedule_id": 1, "access_token": "hidden"},
            "created_at": datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
        },
    )


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def test_alert_service_generates_alerts_from_monitoring_without_duplicates(db_session: Session) -> None:
    """Monitoring events create alerts and active duplicates are updated."""

    _monitoring_event(db_session)
    service = _service(db_session)

    first_refresh = service.refresh_from_monitoring()
    second_refresh = service.refresh_from_monitoring()

    assert first_refresh.created == 1
    assert first_refresh.updated == 0
    assert second_refresh.created == 0
    assert second_refresh.updated == 1
    assert service.summary().total == 1
    assert service.summary().warning == 1
    assert first_refresh.alerts[0].metadata == {"schedule_id": 1}


def test_alert_service_filters_acknowledges_resolves_and_summarizes(db_session: Session) -> None:
    """The service owns alert lifecycle transitions and filters."""

    _monitoring_event(db_session, severity="error", source="GA4", message="Connecteur indisponible")
    service = _service(db_session)
    created = service.refresh_from_monitoring().alerts[0]

    filtered = service.list_alerts(
        PaginationParams(page=1, page_size=10),
        filters=AlertFilters(
            status=AlertStatus.ACTIVE,
            severity=AlertSeverity.CRITICAL,
            category="sync",
            source_type="GA4",
        ),
    )
    acknowledged = service.acknowledge_alert(created.id, user_id=42)
    resolved = service.resolve_alert(created.id)
    summary = service.summary()

    assert filtered.total == 1
    assert acknowledged.status == AlertStatus.ACKNOWLEDGED
    assert acknowledged.acknowledged_by_user_id == 42
    assert acknowledged.acknowledged_at is not None
    assert _as_utc(acknowledged.acknowledged_at) == datetime(2026, 7, 10, 12, 0, tzinfo=UTC)
    assert resolved.status == AlertStatus.RESOLVED
    assert summary.resolved == 1
    assert summary.critical == 1


def test_alert_service_rejects_acknowledge_on_resolved_alert(db_session: Session) -> None:
    """Resolved alerts cannot be acknowledged again."""

    _monitoring_event(db_session)
    service = _service(db_session)
    alert = service.refresh_from_monitoring().alerts[0]
    service.resolve_alert(alert.id)

    with pytest.raises(HTTPException) as exc_info:
        service.acknowledge_alert(alert.id, user_id=1)

    assert exc_info.value.status_code == 422
