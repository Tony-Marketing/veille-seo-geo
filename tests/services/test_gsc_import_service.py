"""Tests for Google Search Console import service."""

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from backend.app.connectors.google_search_console import GoogleSearchConsoleClient
from backend.app.repositories.gsc import GscDataRepository, GscImportRunRepository, GscPropertyRepository
from backend.app.schemas.gsc import GscImportRunCreate
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.gsc_import import GoogleSearchConsoleImportService


class FakeImportClient(GoogleSearchConsoleClient):
    """Deterministic import client with no network calls."""

    def fetch_performance(
        self,
        site_url: str,
        date_start: date | None,
        date_end: date | None,
    ) -> list[dict[str, object]]:
        return [
            {
                "date": date_start or date(2026, 7, 1),
                "page": f"{site_url}page",
                "query": "example",
                "device": "DESKTOP",
                "country": "FRA",
                "search_type": "web",
                "clicks": 10,
                "impressions": 100,
                "ctr": 0.1,
                "position": 2.5,
            },
        ]

    def fetch_coverage(self, site_url: str) -> list[dict[str, object]]:
        return [{"date": date(2026, 7, 1), "category": "indexed", "state": "valid", "pages_count": 12}]

    def inspect_urls(self, site_url: str) -> list[dict[str, object]]:
        return [
            {
                "inspected_url": f"{site_url}page",
                "coverage_state": "Indexed",
                "indexing_state": "INDEXING_ALLOWED",
                "verdict": "PASS",
                "inspected_at": datetime(2026, 7, 1, tzinfo=UTC),
            },
        ]

    def list_sitemaps(self, site_url: str) -> list[dict[str, object]]:
        return [{"sitemap_url": f"{site_url}sitemap.xml", "errors": 0, "warnings": 0}]


def test_gsc_import_service_imports_idempotently(db_session: Session) -> None:
    """Repeated imports update existing rows instead of duplicating them."""

    property_repository = GscPropertyRepository(db_session)
    import_repository = GscImportRunRepository(db_session)
    data_repository = GscDataRepository(db_session)
    gsc_property = property_repository.create({"site_url": "https://example.com/"})
    service = GoogleSearchConsoleImportService(
        property_repository,
        import_repository,
        data_repository,
        client=FakeImportClient(),
    )
    payload = GscImportRunCreate(property_id=gsc_property.id, date_start=date(2026, 7, 1), date_end=date(2026, 7, 2))

    first = service.run_import(payload)
    second = service.run_import(payload)
    performance_rows, performance_total = data_repository.list_performance(gsc_property.id, PaginationParams())
    coverage_rows, coverage_total = data_repository.list_coverage(gsc_property.id, PaginationParams())
    indexing_rows, indexing_total = data_repository.list_indexing(gsc_property.id, PaginationParams())
    sitemaps, sitemap_total = data_repository.list_sitemaps(gsc_property.id, PaginationParams())

    assert first.status == "COMPLETED"
    assert second.status == "COMPLETED"
    assert first.rows_imported == 4
    assert second.rows_imported == 4
    assert performance_total == 1
    assert coverage_total == 1
    assert indexing_total == 1
    assert sitemap_total == 1
    assert performance_rows[0].clicks == 10
    assert coverage_rows[0].pages_count == 12
    assert indexing_rows[0].verdict == "PASS"
    assert sitemaps[0].sitemap_url.endswith("sitemap.xml")
