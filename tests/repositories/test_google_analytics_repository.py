"""Tests for Google Analytics repository."""

from datetime import date

from sqlalchemy.orm import Session

from backend.app.models import GoogleAnalyticsDimension, GoogleAnalyticsImport, GoogleAnalyticsMetric
from backend.app.repositories.google_analytics import GoogleAnalyticsRepository
from backend.app.schemas.pagination import PaginationParams


def test_google_analytics_repository_creates_and_lists_properties(db_session: Session) -> None:
    """The repository persists and lists properties."""

    repository = GoogleAnalyticsRepository(db_session)
    property_item = repository.create(
        {
            "property_id": "properties/123",
            "property_name": "Example GA4",
            "measurement_id": "G-TEST123",
        },
    )

    items, total = repository.list_properties(PaginationParams())

    assert property_item.id is not None
    assert total == 1
    assert items == [property_item]
    assert repository.get_property_by_property_id("properties/123") == property_item


def test_google_analytics_repository_upserts_metrics_and_dimensions(db_session: Session) -> None:
    """The repository upserts GA4 metric rows idempotently."""

    repository = GoogleAnalyticsRepository(db_session)
    property_item = repository.create(
        {
            "property_id": "properties/123",
            "property_name": "Example GA4",
        },
    )
    import_log = repository.create_import(
        {
            "property_id": property_item.id,
            "status": "RUNNING",
        },
    )

    first_metric = repository.upsert_metric(
        {
            "property_id": property_item.id,
            "import_id": import_log.id,
            "date": date(2026, 7, 1),
            "source": "google",
            "medium": "organic",
            "campaign": "brand",
            "device_category": "desktop",
            "country": "France",
            "users": 10,
            "sessions": 12,
        },
    )
    second_metric = repository.upsert_metric(
        {
            "property_id": property_item.id,
            "import_id": import_log.id,
            "date": date(2026, 7, 1),
            "source": "google",
            "medium": "organic",
            "campaign": "brand",
            "device_category": "desktop",
            "country": "France",
            "users": 20,
            "sessions": 24,
        },
    )

    assert first_metric.id == second_metric.id
    assert second_metric.users == 20
    assert second_metric.dimension is not None
    assert second_metric.dimension.source == "google"
    assert db_session.query(GoogleAnalyticsMetric).count() == 1
    assert db_session.query(GoogleAnalyticsDimension).count() == 1
    assert db_session.query(GoogleAnalyticsImport).count() == 1


def test_google_analytics_repository_filters_imports_by_property(db_session: Session) -> None:
    """The repository can filter import logs by property."""

    repository = GoogleAnalyticsRepository(db_session)
    first_property = repository.create({"property_id": "properties/123", "property_name": "Example GA4"})
    second_property = repository.create({"property_id": "properties/456", "property_name": "Other GA4"})
    repository.create_import({"property_id": first_property.id, "status": "COMPLETED", "imported_rows": 1})
    repository.create_import({"property_id": second_property.id, "status": "COMPLETED", "imported_rows": 1})

    items, total = repository.list_imports(PaginationParams(), property_id=first_property.id)

    assert total == 1
    assert items[0].property_id == first_property.id
