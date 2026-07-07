"""Tests for Google Search Console SQLAlchemy models."""

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from backend.app.models import (
    GoogleSearchConsoleImport,
    GoogleSearchConsoleIndexCoverage,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleProperty,
    GoogleSearchConsoleSitemap,
)


def test_google_search_console_model_relationships(db_session: Session) -> None:
    """Google Search Console models are linked through relationships."""

    gsc_property = GoogleSearchConsoleProperty(
        site_url="https://example.com/",
        property_type="URL_PREFIX",
        permission_level="siteOwner",
        status="ACTIVE",
    )
    db_session.add(gsc_property)
    db_session.commit()
    db_session.refresh(gsc_property)

    performance = GoogleSearchConsolePerformance(
        property_id=gsc_property.id,
        date=date(2026, 7, 1),
        page="https://example.com/",
        query="example",
        country="fra",
        device="DESKTOP",
        clicks=10,
        impressions=100,
        ctr=0.1,
        position=3.2,
    )
    index_coverage = GoogleSearchConsoleIndexCoverage(
        property_id=gsc_property.id,
        url="https://example.com/",
        coverage_state="Indexed",
        indexing_state="INDEXING_ALLOWED",
        verdict="PASS",
        inspected_at=datetime.now(UTC),
    )
    sitemap = GoogleSearchConsoleSitemap(
        property_id=gsc_property.id,
        sitemap_url="https://example.com/sitemap.xml",
        status="OK",
        warnings=0,
        errors=0,
        contents={"submitted": 10},
    )
    import_history = GoogleSearchConsoleImport(
        property_id=gsc_property.id,
        import_type="full",
        status="COMPLETED",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        items_processed=3,
    )
    db_session.add_all([performance, index_coverage, sitemap, import_history])
    db_session.commit()
    db_session.refresh(gsc_property)

    assert gsc_property.performances == [performance]
    assert gsc_property.index_coverages == [index_coverage]
    assert gsc_property.sitemaps == [sitemap]
    assert gsc_property.imports == [import_history]
    assert performance.property == gsc_property
    assert index_coverage.property == gsc_property
    assert sitemap.property == gsc_property
    assert import_history.property == gsc_property
