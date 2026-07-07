"""Tests for Google Search Console service."""

from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.connectors.google_search_console import (
    GoogleSearchConsoleIndexCoverageRow,
    GoogleSearchConsolePerformanceRow,
    GoogleSearchConsolePropertyData,
    GoogleSearchConsoleSitemapRow,
)
from backend.app.core.security import decrypt_secret
from backend.app.models import (
    GoogleSearchConsoleIndexCoverage,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleSitemap,
)
from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.google_search_console import (
    GoogleSearchConsoleManualImportRequest,
    GoogleSearchConsoleOAuthTokenUpdate,
    GoogleSearchConsolePerformanceFilters,
    GoogleSearchConsolePropertyCreate,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.google_search_console import GoogleSearchConsoleService


class FakeGoogleSearchConsoleConnector:
    """Deterministic connector stub."""

    def list_properties(self) -> list[GoogleSearchConsolePropertyData]:
        return [
            GoogleSearchConsolePropertyData(
                google_property_id="sc-domain:example.com",
                property_url="sc-domain:example.com",
                property_type="DOMAIN",
            ),
        ]

    def fetch_performance(
        self,
        *,
        property_url: str,
        start_date: date,
        end_date: date,
        dimensions: list[str],
        search_type: str = "web",
    ) -> list[GoogleSearchConsolePerformanceRow]:
        return [
            GoogleSearchConsolePerformanceRow(
                date=start_date,
                query="audit seo",
                page="https://example.com/",
                country="FRA",
                device="DESKTOP",
                search_type=search_type,
                clicks=10,
                impressions=100,
                ctr=0.1,
                position=2.0,
            ),
        ]

    def fetch_index_coverage(self, *, property_url: str) -> list[GoogleSearchConsoleIndexCoverageRow]:
        return [
            GoogleSearchConsoleIndexCoverageRow(
                url="https://example.com/",
                coverage_state="INDEXED",
                verdict="PASS",
            ),
        ]

    def fetch_sitemaps(self, *, property_url: str) -> list[GoogleSearchConsoleSitemapRow]:
        return [
            GoogleSearchConsoleSitemapRow(
                sitemap_url="https://example.com/sitemap.xml",
                sitemap_type="WEB",
                contents={"contents": [{"type": "WEB", "submitted": 42}]},
            ),
        ]


def _service(db_session: Session) -> GoogleSearchConsoleService:
    return GoogleSearchConsoleService(
        GoogleSearchConsoleRepository(db_session),
        connector=FakeGoogleSearchConsoleConnector(),
    )


def test_google_search_console_service_creates_and_lists_properties(db_session: Session) -> None:
    """The service manages properties and remote connector data."""

    service = _service(db_session)

    created = service.create_property(
        GoogleSearchConsolePropertyCreate(
            google_property_id="sc-domain:example.com",
            property_url="sc-domain:example.com",
            property_type="DOMAIN",
        ),
    )
    remote = service.list_remote_properties()

    assert created.id is not None
    assert remote[0].google_property_id == "sc-domain:example.com"
    with pytest.raises(HTTPException):
        service.create_property(
            GoogleSearchConsolePropertyCreate(
                google_property_id="sc-domain:example.com",
                property_url="sc-domain:example.com",
            ),
        )


def test_google_search_console_service_encrypts_oauth_tokens(db_session: Session) -> None:
    """OAuth tokens are encrypted before storage and never exposed by read schemas."""

    service = _service(db_session)
    created = service.create_property(
        GoogleSearchConsolePropertyCreate(
            google_property_id="sc-domain:example.com",
            property_url="sc-domain:example.com",
        ),
    )

    read = service.update_oauth_tokens(
        created.id,
        GoogleSearchConsoleOAuthTokenUpdate(
            access_token="access-token",
            refresh_token="refresh-token",
            token_scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
            token_expires_at=datetime.now(UTC) + timedelta(hours=1),
        ),
    )
    stored = GoogleSearchConsoleRepository(db_session).get_property(created.id)

    assert read.token_scopes == ["https://www.googleapis.com/auth/webmasters.readonly"]
    assert stored is not None
    assert stored.encrypted_access_token != "access-token"
    assert stored.encrypted_refresh_token != "refresh-token"
    assert decrypt_secret(stored.encrypted_access_token or "") == "access-token"
    assert decrypt_secret(stored.encrypted_refresh_token or "") == "refresh-token"


def test_google_search_console_service_runs_idempotent_import(db_session: Session) -> None:
    """Manual imports are journaled and upsert imported rows idempotently."""

    service = _service(db_session)
    created = service.create_property(
        GoogleSearchConsolePropertyCreate(
            google_property_id="sc-domain:example.com",
            property_url="sc-domain:example.com",
        ),
    )
    payload = GoogleSearchConsoleManualImportRequest(
        property_id=created.id,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 7),
        dimensions=["query", "page"],
    )

    first_import = service.run_manual_import(payload)
    second_import = service.run_manual_import(payload)

    assert first_import.status == "COMPLETED"
    assert second_import.status == "COMPLETED"
    assert first_import.rows_imported == 3
    assert second_import.rows_imported == 3
    assert db_session.query(GoogleSearchConsolePerformance).count() == 1
    assert db_session.query(GoogleSearchConsoleIndexCoverage).count() == 1
    assert db_session.query(GoogleSearchConsoleSitemap).count() == 1
    assert first_import.duration_seconds is not None
    assert first_import.duration_seconds >= 0


def test_google_search_console_service_exposes_desktop_api_complements(db_session: Session) -> None:
    """The service calculates the REST complements needed by Sprint 24B."""

    service = _service(db_session)
    created = service.create_property(
        GoogleSearchConsolePropertyCreate(
            google_property_id="sc-domain:example.com",
            property_url="sc-domain:example.com",
        ),
    )
    service.run_manual_import(
        GoogleSearchConsoleManualImportRequest(
            property_id=created.id,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 7),
        ),
    )
    repository = GoogleSearchConsoleRepository(db_session)
    repository.upsert_index_coverage(
        {
            "property_id": created.id,
            "url": "https://example.com/excluded",
            "coverage_state": "EXCLUDED",
        },
    )
    repository.upsert_index_coverage(
        {
            "property_id": created.id,
            "url": "https://example.com/error",
            "coverage_state": "ERROR",
            "verdict": "FAIL",
        },
    )
    repository.upsert_index_coverage(
        {
            "property_id": created.id,
            "url": "https://example.com/warning",
            "coverage_state": "WARNING",
            "verdict": "PARTIAL",
        },
    )

    properties = service.list_properties(PaginationParams())
    performances = service.list_performances(
        PaginationParams(),
        property_id=created.id,
        filters=GoogleSearchConsolePerformanceFilters(
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 7),
            page="https://example.com/",
            query="audit seo",
            country="FRA",
            device="DESKTOP",
        ),
    )
    indexation = service.list_index_coverages(PaginationParams(), property_id=created.id)
    sitemaps = service.list_sitemaps(PaginationParams(), property_id=created.id)
    imports = service.list_imports(PaginationParams(), property_id=created.id)

    assert properties.items[0].last_sync_at is not None
    assert performances.total == 1
    assert indexation.valid_pages == 1
    assert indexation.excluded_pages == 1
    assert indexation.errors == 1
    assert indexation.warnings == 1
    assert sitemaps.items[0].url_count == 42
    assert imports.items[0].duration_seconds is not None


def test_google_search_console_service_rejects_invalid_import_dates(db_session: Session) -> None:
    """The service validates import periods before using the connector."""

    service = _service(db_session)
    created = service.create_property(
        GoogleSearchConsolePropertyCreate(
            google_property_id="sc-domain:example.com",
            property_url="sc-domain:example.com",
        ),
    )

    with pytest.raises(HTTPException):
        service.run_manual_import(
            GoogleSearchConsoleManualImportRequest(
                property_id=created.id,
                start_date=date(2026, 7, 7),
                end_date=date(2026, 7, 1),
            ),
        )
