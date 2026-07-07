"""Tests for Google Search Console repository."""

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.models import (
    GoogleSearchConsoleImport,
    GoogleSearchConsoleIndexCoverage,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleSitemap,
)
from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.pagination import PaginationParams


def test_google_search_console_repository_creates_and_lists_properties(db_session: Session) -> None:
    """The repository persists and lists properties."""

    repository = GoogleSearchConsoleRepository(db_session)
    property_item = repository.create(
        {
            "google_property_id": "sc-domain:example.com",
            "property_url": "sc-domain:example.com",
            "property_type": "DOMAIN",
        },
    )

    items, total = repository.list_properties(PaginationParams())

    assert property_item.id is not None
    assert total == 1
    assert items == [property_item]
    assert repository.get_property_by_google_id("sc-domain:example.com") == property_item


def test_google_search_console_repository_upserts_imported_rows(db_session: Session) -> None:
    """The repository upserts performance, index and sitemap rows idempotently."""

    repository = GoogleSearchConsoleRepository(db_session)
    property_item = repository.create(
        {
            "google_property_id": "sc-domain:example.com",
            "property_url": "sc-domain:example.com",
            "property_type": "DOMAIN",
        },
    )
    import_log = repository.create_import(
        {
            "property_id": property_item.id,
            "import_type": "MANUAL",
            "status": "RUNNING",
            "start_date": date(2026, 7, 1),
            "end_date": date(2026, 7, 7),
            "dimensions": ["query", "page"],
        },
    )

    first_performance = repository.upsert_performance(
        {
            "property_id": property_item.id,
            "import_id": import_log.id,
            "date": date(2026, 7, 1),
            "query": "audit seo",
            "page": "https://example.com/",
            "search_type": "web",
            "clicks": 1,
            "impressions": 10,
            "ctr": 0.1,
            "position": 3.0,
        },
    )
    second_performance = repository.upsert_performance(
        {
            "property_id": property_item.id,
            "import_id": import_log.id,
            "date": date(2026, 7, 1),
            "query": "audit seo",
            "page": "https://example.com/",
            "search_type": "web",
            "clicks": 5,
            "impressions": 20,
            "ctr": 0.25,
            "position": 2.0,
        },
    )
    index_coverage = repository.upsert_index_coverage(
        {
            "property_id": property_item.id,
            "import_id": import_log.id,
            "url": "https://example.com/",
            "coverage_state": "INDEXED",
        },
    )
    sitemap = repository.upsert_sitemap(
        {
            "property_id": property_item.id,
            "import_id": import_log.id,
            "sitemap_url": "https://example.com/sitemap.xml",
            "sitemap_type": "WEB",
        },
    )

    assert first_performance.id == second_performance.id
    assert second_performance.clicks == 5
    assert isinstance(index_coverage, GoogleSearchConsoleIndexCoverage)
    assert isinstance(sitemap, GoogleSearchConsoleSitemap)
    assert db_session.query(GoogleSearchConsolePerformance).count() == 1
    assert db_session.query(GoogleSearchConsoleIndexCoverage).count() == 1
    assert db_session.query(GoogleSearchConsoleSitemap).count() == 1
    assert db_session.query(GoogleSearchConsoleImport).count() == 1


def test_google_search_console_repository_filters_lists_by_property(db_session: Session) -> None:
    """The repository can filter stored rows by property."""

    repository = GoogleSearchConsoleRepository(db_session)
    first_property = repository.create(
        {
            "google_property_id": "sc-domain:example.com",
            "property_url": "sc-domain:example.com",
            "property_type": "DOMAIN",
        },
    )
    second_property = repository.create(
        {
            "google_property_id": "sc-domain:other.com",
            "property_url": "sc-domain:other.com",
            "property_type": "DOMAIN",
        },
    )
    repository.upsert_sitemap(
        {
            "property_id": first_property.id,
            "sitemap_url": "https://example.com/sitemap.xml",
        },
    )
    repository.upsert_sitemap(
        {
            "property_id": second_property.id,
            "sitemap_url": "https://other.com/sitemap.xml",
        },
    )

    items, total = repository.list_sitemaps(PaginationParams(), property_id=first_property.id)

    assert total == 1
    assert items[0].property_id == first_property.id


def test_google_search_console_repository_filters_performances(db_session: Session) -> None:
    """The repository applies SQL filters to stored performance rows."""

    repository = GoogleSearchConsoleRepository(db_session)
    property_item = repository.create(
        {
            "google_property_id": "sc-domain:example.com",
            "property_url": "sc-domain:example.com",
            "property_type": "DOMAIN",
        },
    )
    repository.upsert_performance(
        {
            "property_id": property_item.id,
            "date": date(2026, 7, 1),
            "query": "audit seo",
            "page": "https://example.com/audit",
            "country": "FRA",
            "device": "DESKTOP",
            "search_type": "web",
        },
    )
    repository.upsert_performance(
        {
            "property_id": property_item.id,
            "date": date(2026, 7, 3),
            "query": "veille geo",
            "page": "https://example.com/geo",
            "country": "BEL",
            "device": "MOBILE",
            "search_type": "web",
        },
    )

    items, total = repository.list_performances(
        PaginationParams(),
        property_id=property_item.id,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 2),
        page="https://example.com/audit",
        query="audit seo",
        country="FRA",
        device="DESKTOP",
    )

    assert total == 1
    assert items[0].query == "audit seo"
    assert items[0].page == "https://example.com/audit"


def test_google_search_console_repository_reads_sync_dates_and_index_statuses(db_session: Session) -> None:
    """The repository exposes raw data needed by service-level calculations."""

    repository = GoogleSearchConsoleRepository(db_session)
    property_item = repository.create(
        {
            "google_property_id": "sc-domain:example.com",
            "property_url": "sc-domain:example.com",
            "property_type": "DOMAIN",
        },
    )
    completed_at = datetime(2026, 7, 7, 12, 0, 0)
    older_completed_at = completed_at - timedelta(hours=1)
    repository.create_import(
        {
            "property_id": property_item.id,
            "import_type": "MANUAL",
            "status": "COMPLETED",
            "completed_at": older_completed_at,
        },
    )
    repository.create_import(
        {
            "property_id": property_item.id,
            "import_type": "MANUAL",
            "status": "COMPLETED",
            "completed_at": completed_at,
        },
    )
    repository.upsert_index_coverage(
        {
            "property_id": property_item.id,
            "url": "https://example.com/",
            "coverage_state": "INDEXED",
            "verdict": "PASS",
        },
    )

    latest_by_id = repository.get_latest_import_completed_at_by_property_ids(
        [property_item.id],
        statuses=("COMPLETED",),
    )

    assert repository.get_latest_import_completed_at(property_item.id, statuses=("COMPLETED",)) == completed_at
    assert latest_by_id == {property_item.id: completed_at}
    assert repository.list_index_coverage_statuses(property_id=property_item.id) == [
        ("INDEXED", "PASS", None, None),
    ]
