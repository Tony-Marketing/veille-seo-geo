"""Tests for Google Search Console models."""

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from backend.app.models import (
    GoogleSearchConsoleImport,
    GoogleSearchConsoleIndexCoverage,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleProperty,
    GoogleSearchConsoleSitemap,
)


def test_google_search_console_models_persist_relationships(db_session: Session) -> None:
    """Google Search Console models persist their core relationships."""

    property_item = GoogleSearchConsoleProperty(
        google_property_id="sc-domain:example.com",
        property_url="sc-domain:example.com",
        property_type="DOMAIN",
        display_name="Example",
    )
    db_session.add(property_item)
    db_session.commit()
    db_session.refresh(property_item)

    import_log = GoogleSearchConsoleImport(
        property_id=property_item.id,
        import_type="MANUAL",
        status="COMPLETED",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 7),
        dimensions=["query", "page"],
    )
    db_session.add(import_log)
    db_session.commit()
    db_session.refresh(import_log)

    performance = GoogleSearchConsolePerformance(
        property_id=property_item.id,
        import_id=import_log.id,
        date=date(2026, 7, 1),
        query="audit seo",
        page="https://example.com/",
        search_type="web",
        clicks=10,
        impressions=100,
        ctr=0.1,
        position=2.5,
    )
    index_coverage = GoogleSearchConsoleIndexCoverage(
        property_id=property_item.id,
        import_id=import_log.id,
        url="https://example.com/",
        coverage_state="INDEXED",
        referring_urls=["https://example.com/sitemap.xml"],
        last_crawled_at=datetime.now(UTC),
    )
    sitemap = GoogleSearchConsoleSitemap(
        property_id=property_item.id,
        import_id=import_log.id,
        sitemap_url="https://example.com/sitemap.xml",
        sitemap_type="WEB",
    )
    db_session.add_all([performance, index_coverage, sitemap])
    db_session.commit()
    db_session.refresh(property_item)
    db_session.refresh(import_log)

    assert property_item.id is not None
    assert property_item.performances == [performance]
    assert property_item.index_coverages == [index_coverage]
    assert property_item.sitemaps == [sitemap]
    assert property_item.imports == [import_log]
    assert import_log.performances == [performance]
    assert import_log.index_coverages == [index_coverage]
    assert import_log.sitemaps == [sitemap]
