"""Tests for MonitoringEvent model."""

from datetime import UTC, datetime
from uuid import UUID

from backend.app.models import MonitoringEvent


def test_monitoring_event_model_fields() -> None:
    """MonitoringEvent exposes the expected persisted fields."""

    event = MonitoringEvent(
        event_type="sync",
        severity="warning",
        source="GSC",
        message="Import en retard",
        details={"schedule_id": 1},
        created_at=datetime(2026, 7, 9, 8, 0, tzinfo=UTC),
    )

    assert isinstance(event.id, UUID) or event.id is None
    assert event.event_type == "sync"
    assert event.severity == "warning"
    assert event.source == "GSC"
    assert event.message == "Import en retard"
    assert event.details == {"schedule_id": 1}
    assert event.created_at is not None
