"""Tests for MonitoringRepository."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import (
    BingWebmasterConnection,
    BingWebmasterImportRun,
    GoogleAnalyticsImport,
    GoogleAnalyticsProperty,
    GoogleSearchConsoleImport,
    GoogleSearchConsoleProperty,
)
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.schemas.pagination import PaginationParams


def test_monitoring_repository_creates_lists_and_counts_events(db_session: Session) -> None:
    """The repository persists and filters monitoring events."""

    repository = MonitoringRepository(db_session)
    repository.create_event(
        {
            "event_type": "sync",
            "severity": "warning",
            "source": "GSC",
            "message": "Import en retard",
            "details": {"schedule_id": 1},
            "created_at": datetime(2026, 7, 9, 8, 0, tzinfo=UTC),
        },
    )
    repository.create_event(
        {
            "event_type": "connector",
            "severity": "error",
            "source": "GA4",
            "message": "Connecteur en erreur",
            "created_at": datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        },
    )

    items, total = repository.list_events(PaginationParams(page=1, page_size=10), severity="warning")

    assert total == 1
    assert items[0].source == "GSC"
    assert repository.count_events() == 2
    assert repository.count_events(severity="error") == 1
    assert repository.count_events(created_from=datetime(2026, 7, 9, tzinfo=UTC)) == 1
    assert repository.get_last_event() is not None


def test_monitoring_repository_reads_connector_stats(db_session: Session) -> None:
    """Connector stats are derived from persisted data only."""

    db_session.add(
        GoogleSearchConsoleProperty(
            google_property_id="sc-domain:example.com",
            property_url="https://example.com",
            is_active=True,
        ),
    )
    db_session.add(
        GoogleAnalyticsProperty(
            property_id="123",
            property_name="Example",
            enabled=True,
        ),
    )
    db_session.add(BingWebmasterConnection(is_active=True, last_sync_at=datetime(2026, 7, 9, 7, 0, tzinfo=UTC)))
    db_session.commit()
    db_session.add(
        GoogleSearchConsoleImport(
            property_id=1,
            status="COMPLETED",
            completed_at=datetime(2026, 7, 9, 8, 0, tzinfo=UTC),
        ),
    )
    db_session.add(
        GoogleAnalyticsImport(
            property_id=1,
            status="FAILED",
            finished_at=datetime(2026, 7, 9, 9, 0, tzinfo=UTC),
        ),
    )
    db_session.add(
        BingWebmasterImportRun(
            connection_id=1,
            status="COMPLETED",
            finished_at=datetime(2026, 7, 9, 10, 0, tzinfo=UTC),
        ),
    )
    db_session.commit()

    repository = MonitoringRepository(db_session)

    assert repository.google_search_console_stats()["enabled"] == 1
    assert repository.google_search_console_stats()["latest_sync"] == datetime(2026, 7, 9, 8, 0, tzinfo=UTC)
    assert repository.google_analytics_stats()["errors"] == 1
    assert repository.bing_webmaster_tools_stats()["latest_sync"] == datetime(2026, 7, 9, 10, 0, tzinfo=UTC)
