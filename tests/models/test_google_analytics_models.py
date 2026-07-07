"""Tests for Google Analytics models."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import (
    GoogleAnalyticsDimension,
    GoogleAnalyticsImport,
    GoogleAnalyticsMetric,
    GoogleAnalyticsProperty,
)


def test_google_analytics_models_persist_relationships(db_session: Session) -> None:
    """Google Analytics models persist their core relationships."""

    property_item = GoogleAnalyticsProperty(
        property_id="properties/123",
        property_name="Example GA4",
        account_name="Example Account",
        measurement_id="G-TEST123",
    )
    db_session.add(property_item)
    db_session.commit()
    db_session.refresh(property_item)

    import_log = GoogleAnalyticsImport(
        property_id=property_item.id,
        status="COMPLETED",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        imported_rows=1,
    )
    db_session.add(import_log)
    db_session.commit()
    db_session.refresh(import_log)

    metric = GoogleAnalyticsMetric(
        property_id=property_item.id,
        import_id=import_log.id,
        date=datetime(2026, 7, 1).date(),
        source="google",
        medium="organic",
        campaign="brand",
        device_category="desktop",
        country="France",
        users=10,
        new_users=4,
        sessions=12,
        engaged_sessions=9,
        screen_page_views=30,
    )
    db_session.add(metric)
    db_session.commit()
    db_session.refresh(metric)

    dimension = GoogleAnalyticsDimension(
        metric_id=metric.id,
        source="google",
        medium="organic",
        campaign="brand",
        device_category="desktop",
        country="France",
    )
    db_session.add(dimension)
    db_session.commit()
    db_session.refresh(property_item)
    db_session.refresh(import_log)
    db_session.refresh(metric)

    assert property_item.metrics == [metric]
    assert property_item.imports == [import_log]
    assert import_log.metrics == [metric]
    assert metric.dimension == dimension
    assert dimension.metric == metric
