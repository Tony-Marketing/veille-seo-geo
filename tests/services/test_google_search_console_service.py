"""Tests for Google Search Console service."""

from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.connectors.google_search_console import (
    GoogleSearchConsoleConnector,
    GoogleSearchConsoleConnectorError,
    GoogleSearchConsoleIndexCoverageData,
    GoogleSearchConsolePerformanceData,
    GoogleSearchConsolePropertyData,
    GoogleSearchConsoleSitemapData,
)
from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.google_search_console import (
    GoogleSearchConsoleImportRequest,
    GoogleSearchConsoleImportStatus,
    GoogleSearchConsoleImportType,
    GoogleSearchConsolePerformanceFilters,
    GoogleSearchConsolePropertyCreate,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.google_search_console import GoogleSearchConsoleService


class FakeGoogleSearchConsoleConnector(GoogleSearchConsoleConnector):
    """Deterministic connector used by service tests."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[str] = []

    def list_properties(self) -> list[GoogleSearchConsolePropertyData]:
        self.calls.append("list_properties")
        if self.fail:
            raise GoogleSearchConsoleConnectorError("Quota Google atteint.")
        return [
            GoogleSearchConsolePropertyData(
                site_url="https://example.com/",
                property_type="URL_PREFIX",
                permission_level="siteOwner",
            ),
        ]

    def fetch_performance(
        self,
        site_url: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[GoogleSearchConsolePerformanceData]:
        self.calls.append(f"fetch_performance:{site_url}")
        if self.fail:
            raise GoogleSearchConsoleConnectorError("Quota Google atteint.")
        return [
            GoogleSearchConsolePerformanceData(
                date=date(2026, 7, 1),
                page="https://example.com/",
                query="example",
                country="fra",
                device="DESKTOP",
                clicks=10,
                impressions=100,
                ctr=0.1,
                position=2.4,
            ),
        ]

    def fetch_index_coverage(self, site_url: str) -> list[GoogleSearchConsoleIndexCoverageData]:
        self.calls.append(f"fetch_index_coverage:{site_url}")
        if self.fail:
            raise GoogleSearchConsoleConnectorError("Quota Google atteint.")
        return [
            GoogleSearchConsoleIndexCoverageData(
                url="https://example.com/",
                coverage_state="Indexed",
                indexing_state="INDEXING_ALLOWED",
                verdict="PASS",
            ),
        ]

    def fetch_sitemaps(self, site_url: str) -> list[GoogleSearchConsoleSitemapData]:
        self.calls.append(f"fetch_sitemaps:{site_url}")
        if self.fail:
            raise GoogleSearchConsoleConnectorError("Quota Google atteint.")
        return [
            GoogleSearchConsoleSitemapData(
                sitemap_url="https://example.com/sitemap.xml",
                status="OK",
                warnings=0,
                errors=0,
            ),
        ]


def _service(
    db_session: Session,
    connector: GoogleSearchConsoleConnector | None = None,
) -> GoogleSearchConsoleService:
    return GoogleSearchConsoleService(
        GoogleSearchConsoleRepository(db_session),
        connector=connector or FakeGoogleSearchConsoleConnector(),
    )


def test_google_search_console_service_imports_properties(db_session: Session) -> None:
    """The service imports properties through the connector."""

    result = _service(db_session).run_import(
        GoogleSearchConsoleImportRequest(import_type=GoogleSearchConsoleImportType.PROPERTIES),
    )

    assert result.status == GoogleSearchConsoleImportStatus.COMPLETED
    assert result.items_processed == 1
    assert result.items_created == 1
    assert GoogleSearchConsoleRepository(db_session).get_property_by_site_url("https://example.com/") is not None


def test_google_search_console_service_full_import_is_idempotent(db_session: Session) -> None:
    """Running the same import twice updates rows instead of duplicating them."""

    service = _service(db_session)
    gsc_property = service.create_property(GoogleSearchConsolePropertyCreate(site_url="https://example.com/"))
    payload = GoogleSearchConsoleImportRequest(
        import_type=GoogleSearchConsoleImportType.FULL,
        property_id=gsc_property.id,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 1),
    )

    first = service.run_import(payload)
    second = service.run_import(payload)
    repository = GoogleSearchConsoleRepository(db_session)

    assert first.items_created == 3
    assert second.items_created == 0
    assert second.items_updated == 3
    assert repository.list_performances(
        GoogleSearchConsolePerformanceFilters(property_id=gsc_property.id),
        PaginationParams(),
    )[1] == 1


def test_google_search_console_service_rejects_unknown_property(db_session: Session) -> None:
    """Property-scoped imports fail before calling the connector when the property does not exist."""

    connector = FakeGoogleSearchConsoleConnector()
    with pytest.raises(HTTPException) as exc_info:
        _service(db_session, connector).run_import(
            GoogleSearchConsoleImportRequest(
                import_type=GoogleSearchConsoleImportType.PERFORMANCE,
                property_id=999,
            ),
        )

    assert exc_info.value.status_code == 404
    assert connector.calls == []


def test_google_search_console_service_records_connector_errors(db_session: Session) -> None:
    """Connector errors are stored in import history."""

    connector = FakeGoogleSearchConsoleConnector(fail=True)
    service = _service(db_session, connector)
    gsc_property = service.create_property(GoogleSearchConsolePropertyCreate(site_url="https://example.com/"))

    result = service.run_import(
        GoogleSearchConsoleImportRequest(
            import_type=GoogleSearchConsoleImportType.PERFORMANCE,
            property_id=gsc_property.id,
        ),
    )

    assert result.status == GoogleSearchConsoleImportStatus.FAILED
    assert result.error_message == "Quota Google atteint."
