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


def test_google_analytics_repository_lists_metrics_with_filters_pagination_and_sort(db_session: Session) -> None:
    """The repository filters, sorts and paginates metric rows."""

    repository = GoogleAnalyticsRepository(db_session)
    property_item = repository.create({"property_id": "properties/123", "property_name": "Example GA4"})
    other_property = repository.create({"property_id": "properties/456", "property_name": "Other GA4"})
    import_log = repository.create_import({"property_id": property_item.id, "status": "COMPLETED", "imported_rows": 2})
    repository.upsert_metric(
        _metric_payload(
            property_id=property_item.id,
            import_id=import_log.id,
            metric_date=date(2026, 7, 1),
            source="google",
            medium="organic",
            sessions=12,
            users=10,
        ),
    )
    repository.upsert_metric(
        _metric_payload(
            property_id=property_item.id,
            import_id=import_log.id,
            metric_date=date(2026, 7, 2),
            source="newsletter",
            medium="email",
            sessions=4,
            users=3,
        ),
    )
    repository.upsert_metric(
        _metric_payload(
            property_id=other_property.id,
            import_id=None,
            metric_date=date(2026, 7, 3),
            source="google",
            medium="organic",
            sessions=30,
            users=25,
        ),
    )

    items, total = repository.list_metrics(
        PaginationParams(page=1, page_size=1, sort="sessions", order="desc"),
        property_id=property_item.id,
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 2),
        search="google",
    )

    assert total == 1
    assert len(items) == 1
    assert items[0].source == "google"
    assert items[0].sessions == 12


def test_google_analytics_repository_rejects_unknown_metric_sort(db_session: Session) -> None:
    """The repository rejects arbitrary sort fields."""

    repository = GoogleAnalyticsRepository(db_session)

    try:
        repository.list_metrics(PaginationParams(sort="not_allowed"))
    except ValueError as exc:
        assert "non autorise" in str(exc)
    else:
        raise AssertionError("Unknown metric sort should be rejected.")


def test_google_analytics_repository_aggregates_metrics(db_session: Session) -> None:
    """The repository returns raw aggregate values for service KPIs."""

    repository = GoogleAnalyticsRepository(db_session)
    property_item = repository.create({"property_id": "properties/123", "property_name": "Example GA4"})
    repository.upsert_metric(
        _metric_payload(
            property_id=property_item.id,
            import_id=None,
            metric_date=date(2026, 7, 1),
            source="google",
            medium="organic",
            sessions=10,
            users=8,
            engagement_rate=0.5,
            average_session_duration=30.0,
            conversions=1.0,
            total_revenue=20.0,
        ),
    )
    repository.upsert_metric(
        _metric_payload(
            property_id=property_item.id,
            import_id=None,
            metric_date=date(2026, 7, 2),
            source="newsletter",
            medium="email",
            sessions=5,
            users=4,
            engagement_rate=0.8,
            average_session_duration=60.0,
            conversions=2.0,
            total_revenue=80.0,
        ),
    )

    totals = repository.aggregate_metrics(property_id=property_item.id)
    by_source = repository.aggregate_metrics_by_dimension("source", property_id=property_item.id)

    assert totals["rows"] == 2
    assert totals["sessions"] == 15
    assert totals["users"] == 12
    assert totals["conversions"] == 3.0
    assert totals["total_revenue"] == 100.0
    assert by_source[0]["dimension"] == "google"
    assert by_source[0]["sessions"] == 10


def test_google_analytics_repository_filters_imports_by_status_and_search(db_session: Session) -> None:
    """The repository filters import history by status and search text."""

    repository = GoogleAnalyticsRepository(db_session)
    property_item = repository.create({"property_id": "properties/123", "property_name": "Example GA4"})
    repository.create_import({"property_id": property_item.id, "status": "FAILED", "error_message": "Timeout"})
    repository.create_import({"property_id": property_item.id, "status": "COMPLETED", "error_message": None})

    items, total = repository.list_imports(PaginationParams(search="timeout"), status="FAILED")

    assert total == 1
    assert items[0].status == "FAILED"


def _metric_payload(
    *,
    property_id: int,
    import_id: int | None,
    metric_date: date,
    source: str,
    medium: str,
    sessions: int,
    users: int,
    engagement_rate: float = 0.0,
    average_session_duration: float = 0.0,
    conversions: float = 0.0,
    total_revenue: float = 0.0,
) -> dict[str, object]:
    return {
        "property_id": property_id,
        "import_id": import_id,
        "date": metric_date,
        "source": source,
        "medium": medium,
        "campaign": None,
        "device_category": "desktop",
        "country": "France",
        "users": users,
        "new_users": max(users - 1, 0),
        "sessions": sessions,
        "engaged_sessions": max(sessions - 1, 0),
        "screen_page_views": sessions * 2,
        "average_session_duration": average_session_duration,
        "engagement_rate": engagement_rate,
        "conversions": conversions,
        "total_revenue": total_revenue,
    }
