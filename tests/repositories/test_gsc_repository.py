"""Tests for Google Search Console repositories."""

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from backend.app.repositories.gsc import (
    GscDataRepository,
    GscImportRunRepository,
    GscOAuthCredentialRepository,
    GscPropertyRepository,
)
from backend.app.schemas.pagination import PaginationParams


def test_gsc_property_repository_upserts_by_site_url(db_session: Session) -> None:
    """Properties are idempotently upserted by site URL."""

    repository = GscPropertyRepository(db_session)

    first = repository.upsert_property(
        {"site_url": "https://example.com/", "property_type": "url_prefix", "permission_level": "siteOwner"},
    )
    second = repository.upsert_property(
        {
            "site_url": "https://example.com/",
            "property_type": "url_prefix",
            "permission_level": "siteFullUser",
            "is_verified": True,
        },
    )

    assert first.id == second.id
    assert second.permission_level == "siteFullUser"
    assert repository.count() == 1


def test_gsc_oauth_repository_counts_active_credentials(db_session: Session) -> None:
    """OAuth repository returns latest and active credential count."""

    repository = GscOAuthCredentialRepository(db_session)
    first = repository.create({"provider": "google", "scopes": [], "status": "PENDING"})
    second = repository.create({"provider": "google", "scopes": [], "status": "ACTIVE"})

    assert first.id != second.id
    assert repository.latest() == second
    assert repository.count_active() == 1


def test_gsc_data_repository_upserts_imported_rows(db_session: Session) -> None:
    """Imported datasets are idempotent."""

    property_repository = GscPropertyRepository(db_session)
    import_repository = GscImportRunRepository(db_session)
    data_repository = GscDataRepository(db_session)
    gsc_property = property_repository.create({"site_url": "https://example.com/"})
    import_run = import_repository.create({"property_id": gsc_property.id, "status": "RUNNING", "import_type": "full"})

    performance = {
        "property_id": gsc_property.id,
        "import_run_id": import_run.id,
        "date": date(2026, 7, 1),
        "page": "https://example.com/",
        "query": "example",
        "device": "DESKTOP",
        "country": "FRA",
        "search_type": "web",
        "clicks": 1,
        "impressions": 10,
        "ctr": 0.1,
        "position": 2.0,
    }
    data_repository.upsert_performance_rows([performance])
    data_repository.upsert_performance_rows([{**performance, "clicks": 2}])
    rows, total = data_repository.list_performance(gsc_property.id, PaginationParams())

    assert total == 1
    assert rows[0].clicks == 2

    coverage = {
        "property_id": gsc_property.id,
        "import_run_id": import_run.id,
        "date": date(2026, 7, 1),
        "category": "indexed",
        "state": "valid",
        "pages_count": 4,
    }
    data_repository.upsert_coverage_rows([coverage])
    data_repository.upsert_coverage_rows([{**coverage, "pages_count": 5}])
    coverage_rows, coverage_total = data_repository.list_coverage(gsc_property.id, PaginationParams())

    assert coverage_total == 1
    assert coverage_rows[0].pages_count == 5

    inspected_at = datetime.now(UTC)
    indexing = {
        "property_id": gsc_property.id,
        "import_run_id": import_run.id,
        "inspected_url": "https://example.com/",
        "coverage_state": "Indexed",
        "inspected_at": inspected_at,
    }
    data_repository.upsert_indexing_rows([indexing])
    data_repository.upsert_indexing_rows([{**indexing, "verdict": "PASS"}])
    indexing_rows, indexing_total = data_repository.list_indexing(gsc_property.id, PaginationParams())

    assert indexing_total == 1
    assert indexing_rows[0].verdict == "PASS"

    sitemap = {
        "property_id": gsc_property.id,
        "import_run_id": import_run.id,
        "sitemap_url": "https://example.com/sitemap.xml",
        "errors": 0,
        "warnings": 0,
    }
    data_repository.upsert_sitemaps([sitemap])
    data_repository.upsert_sitemaps([{**sitemap, "warnings": 1}])
    sitemaps, sitemap_total = data_repository.list_sitemaps(gsc_property.id, PaginationParams())

    assert sitemap_total == 1
    assert sitemaps[0].warnings == 1
