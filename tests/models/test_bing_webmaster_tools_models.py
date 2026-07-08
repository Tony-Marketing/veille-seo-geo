"""Tests for Bing Webmaster Tools models."""

from datetime import date

from sqlalchemy.orm import Session

from backend.app.models import (
    BingWebmasterConnection,
    BingWebmasterCrawlStat,
    BingWebmasterImportRun,
    BingWebmasterMetric,
    BingWebmasterSite,
    BingWebmasterSitemap,
)


def test_bing_webmaster_tools_models_persist_relationships(db_session: Session) -> None:
    """Bing Webmaster Tools models persist their core relationships."""

    connection = BingWebmasterConnection(auth_type="API_KEY", client_id="client-id")
    db_session.add(connection)
    db_session.commit()
    db_session.refresh(connection)

    site = BingWebmasterSite(
        connection_id=connection.id,
        site_url="https://example.com/",
        is_verified=True,
    )
    db_session.add(site)
    db_session.commit()
    db_session.refresh(site)

    import_run = BingWebmasterImportRun(
        connection_id=connection.id,
        bing_site_id=site.id,
        import_type="MANUAL",
        status="COMPLETED",
        items_processed=3,
    )
    db_session.add(import_run)
    db_session.commit()
    db_session.refresh(import_run)

    metric = BingWebmasterMetric(
        bing_site_id=site.id,
        import_id=import_run.id,
        date=date(2026, 7, 1),
        query="audit seo",
        page_url="https://example.com/audit",
        country="FRA",
        device="DESKTOP",
        clicks=10,
        impressions=100,
        ctr=0.1,
        average_position=2.5,
    )
    crawl_stat = BingWebmasterCrawlStat(
        bing_site_id=site.id,
        import_id=import_run.id,
        date=date(2026, 7, 1),
        url="https://example.com/missing",
        http_status=404,
        issue_type="NOT_FOUND",
        issue_category="CRAWL",
        severity="ERROR",
    )
    sitemap = BingWebmasterSitemap(
        bing_site_id=site.id,
        import_id=import_run.id,
        sitemap_url="https://example.com/sitemap.xml",
        status="OK",
        url_count=42,
    )
    db_session.add_all([metric, crawl_stat, sitemap])
    db_session.commit()
    db_session.refresh(connection)
    db_session.refresh(site)
    db_session.refresh(import_run)
    db_session.refresh(metric)
    db_session.refresh(crawl_stat)

    assert connection.id is not None
    assert connection.is_active is True
    assert connection.scopes == []
    assert site.is_active is True
    assert site.metrics == [metric]
    assert site.crawl_stats == [crawl_stat]
    assert site.sitemaps == [sitemap]
    assert connection.sites == [site]
    assert connection.import_runs == [import_run]
    assert import_run.metrics == [metric]
    assert import_run.crawl_stats == [crawl_stat]
    assert import_run.sitemaps == [sitemap]
    assert metric.created_at is not None
    assert crawl_stat.created_at is not None
