"""Tests for Bing Webmaster Tools repository."""

from datetime import date

from sqlalchemy.orm import Session

from backend.app.models import BingWebmasterCrawlStat, BingWebmasterMetric, BingWebmasterSitemap
from backend.app.repositories.bing_webmaster_tools import BingWebmasterToolsRepository
from backend.app.schemas.pagination import PaginationParams


def test_bing_webmaster_repository_creates_lists_and_deactivates_connections(db_session: Session) -> None:
    """The repository persists, lists and deactivates connections."""

    repository = BingWebmasterToolsRepository(db_session)
    connection = repository.create({"auth_type": "API_KEY", "client_id": "client-id", "api_key_encrypted": "secret"})

    items, total = repository.list_connections(PaginationParams())
    deactivated = repository.deactivate_connection(connection)

    assert connection.id is not None
    assert total == 1
    assert items == [connection]
    assert repository.get_connection(connection.id) == connection
    assert deactivated.is_active is False


def test_bing_webmaster_repository_upserts_sites_and_imported_rows(db_session: Session) -> None:
    """The repository upserts Bing sites and imported rows idempotently."""

    repository = BingWebmasterToolsRepository(db_session)
    connection = repository.create({"auth_type": "API_KEY", "client_id": "client-id"})
    site = repository.upsert_site(
        {"connection_id": connection.id, "site_url": "https://example.com/", "is_verified": True},
    )
    import_run = repository.create_import_run(
        {"connection_id": connection.id, "bing_site_id": site.id, "status": "RUNNING"},
    )

    first_metric = repository.upsert_metric(_metric_payload(site.id, import_run.id, clicks=1))
    second_metric = repository.upsert_metric(_metric_payload(site.id, import_run.id, clicks=5))
    crawl_stat = repository.upsert_crawl_stat(
        {
            "bing_site_id": site.id,
            "import_id": import_run.id,
            "date": date(2026, 7, 1),
            "url": "https://example.com/missing",
            "http_status": 404,
            "issue_type": "NOT_FOUND",
        },
    )
    sitemap = repository.upsert_sitemap(
        {
            "bing_site_id": site.id,
            "import_id": import_run.id,
            "sitemap_url": "https://example.com/sitemap.xml",
            "status": "OK",
            "url_count": 42,
        },
    )

    assert first_metric.id == second_metric.id
    assert second_metric.clicks == 5
    assert isinstance(crawl_stat, BingWebmasterCrawlStat)
    assert isinstance(sitemap, BingWebmasterSitemap)
    assert db_session.query(BingWebmasterMetric).count() == 1
    assert db_session.query(BingWebmasterCrawlStat).count() == 1
    assert db_session.query(BingWebmasterSitemap).count() == 1


def test_bing_webmaster_repository_filters_paginates_searches_and_sorts(db_session: Session) -> None:
    """The repository applies filters, search, pagination and whitelisted sort fields."""

    repository = BingWebmasterToolsRepository(db_session)
    connection = repository.create({"auth_type": "API_KEY", "client_id": "client-id"})
    first_site = repository.upsert_site({"connection_id": connection.id, "site_url": "https://example.com/"})
    second_site = repository.upsert_site({"connection_id": connection.id, "site_url": "https://other.example/"})
    repository.upsert_metric(_metric_payload(first_site.id, None, clicks=10, metric_date=date(2026, 7, 1)))
    repository.upsert_metric(
        _metric_payload(
            second_site.id,
            None,
            clicks=3,
            metric_date=date(2026, 7, 3),
            query="veille geo",
            page_url="https://other.example/geo",
        ),
    )
    repository.upsert_crawl_stat(
        {
            "bing_site_id": first_site.id,
            "date": date(2026, 7, 1),
            "url": "https://example.com/missing",
            "http_status": 404,
            "issue_type": "NOT_FOUND",
            "severity": "ERROR",
        },
    )
    repository.upsert_sitemap(
        {"bing_site_id": first_site.id, "sitemap_url": "https://example.com/sitemap.xml", "status": "OK"},
    )

    metrics, metric_total = repository.list_metrics(
        PaginationParams(page=1, page_size=1, search="audit", sort="clicks", order="desc"),
        bing_site_id=first_site.id,
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 2),
    )
    crawl_stats, crawl_total = repository.list_crawl_stats(
        PaginationParams(search="missing"),
        bing_site_id=first_site.id,
        status=404,
        severity="ERROR",
    )
    sitemaps, sitemap_total = repository.list_sitemaps(
        PaginationParams(search="sitemap"),
        bing_site_id=first_site.id,
        status="OK",
    )
    import_runs, import_total = repository.list_import_runs(PaginationParams())

    assert metric_total == 1
    assert metrics[0].query == "audit seo"
    assert crawl_total == 1
    assert crawl_stats[0].issue_type == "NOT_FOUND"
    assert sitemap_total == 1
    assert sitemaps[0].status == "OK"
    assert import_total == 0
    assert import_runs == []


def test_bing_webmaster_repository_rejects_unknown_sort(db_session: Session) -> None:
    """The repository rejects arbitrary sort fields."""

    repository = BingWebmasterToolsRepository(db_session)

    try:
        repository.list_metrics(PaginationParams(sort="not_allowed"))
    except ValueError as exc:
        assert "non autorise" in str(exc)
    else:
        raise AssertionError("Unknown sort should be rejected.")


def _metric_payload(
    bing_site_id: int,
    import_id: int | None,
    *,
    clicks: int,
    metric_date: date = date(2026, 7, 1),
    query: str = "audit seo",
    page_url: str = "https://example.com/audit",
) -> dict[str, object]:
    return {
        "bing_site_id": bing_site_id,
        "import_id": import_id,
        "date": metric_date,
        "query": query,
        "page_url": page_url,
        "country": "FRA",
        "device": "DESKTOP",
        "clicks": clicks,
        "impressions": 100,
        "ctr": 0.1,
        "average_position": 2.5,
    }
