"""Tests for AlertRepository."""

from datetime import UTC, datetime
from importlib import import_module

from sqlalchemy.orm import Session

from backend.app.models import Alert
from backend.app.repositories.alerts import AlertRepository
from backend.app.schemas.pagination import PaginationParams


def _alert_data(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "source_type": "GSC",
        "source_id": "event-1",
        "category": "sync",
        "severity": "Warning",
        "status": "Active",
        "title": "Warning - GSC - sync",
        "message": "Import en retard",
        "metadata_": {"schedule_id": 1},
        "deduplication_key": "monitoring:sync:GSC:Import en retard",
        "first_seen_at": datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
        "last_seen_at": datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
    }
    data.update(overrides)
    return data


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def test_alert_repository_creates_lists_filters_and_counts(db_session: Session) -> None:
    """The repository persists and filters alerts without business logic."""

    repository = AlertRepository(db_session)
    first = repository.create_alert(_alert_data())
    repository.create_alert(
        _alert_data(
            source_type="GA4",
            source_id="event-2",
            category="connector",
            severity="Critical",
            message="Connecteur indisponible",
            deduplication_key="monitoring:connector:GA4:Connecteur indisponible",
        ),
    )

    items, total = repository.list_alerts(
        PaginationParams(page=1, page_size=10, search="Import"),
        severity="Warning",
        category="sync",
    )

    assert total == 1
    assert items[0].id == first.id
    assert repository.count_alerts() == 2
    assert repository.count_alerts(severity="Critical") == 1
    last_seen_at = repository.get_last_alert_seen_at()
    assert last_seen_at is not None
    assert _as_utc(last_seen_at) == datetime(2026, 7, 10, 8, 0, tzinfo=UTC)


def test_alert_repository_finds_active_deduplication_key_only(db_session: Session) -> None:
    """Active duplicate lookup ignores resolved historical alerts."""

    repository = AlertRepository(db_session)
    resolved = Alert(**_alert_data(status="Resolved", resolved_at=datetime(2026, 7, 10, 9, 0, tzinfo=UTC)))
    db_session.add(resolved)
    db_session.commit()

    assert repository.get_active_by_deduplication_key("monitoring:sync:GSC:Import en retard") is None

    active = repository.create_alert(_alert_data(source_id="event-2"))

    assert repository.get_active_by_deduplication_key(active.deduplication_key) is not None


def test_alerts_migration_revision_is_declared() -> None:
    """The Alembic migration is explicit and chained after monitoring."""

    migration = import_module("backend.alembic.versions.20260710_0013_create_alerts")
    assert migration.revision == "20260710_0013"
    assert migration.down_revision == "20260709_0012"
