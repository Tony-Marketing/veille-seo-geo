"""Tests for Google Analytics service."""

from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.connectors.google_analytics import GoogleAnalyticsMetricRow, GoogleAnalyticsOAuthTokenData
from backend.app.core.security import decrypt_secret
from backend.app.models import GoogleAnalyticsDimension, GoogleAnalyticsMetric
from backend.app.repositories.google_analytics import GoogleAnalyticsRepository
from backend.app.schemas.google_analytics import (
    GoogleAnalyticsImportFilters,
    GoogleAnalyticsImportRequest,
    GoogleAnalyticsImportStatus,
    GoogleAnalyticsMetricFilters,
    GoogleAnalyticsOAuthConnectRequest,
    GoogleAnalyticsOAuthRefreshRequest,
    GoogleAnalyticsPropertyCreate,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.google_analytics import GoogleAnalyticsService


class FakeGoogleAnalyticsConnector:
    """Deterministic connector stub."""

    def fetch_metrics(
        self,
        *,
        property_id: str,
        start_date: date,
        end_date: date,
        metrics: list[str],
        dimensions: list[str],
    ) -> list[GoogleAnalyticsMetricRow]:
        return [
            GoogleAnalyticsMetricRow(
                date=start_date,
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
                average_session_duration=42.5,
                engagement_rate=0.75,
                conversions=2,
                total_revenue=120.0,
            ),
        ]

    def connect_oauth(
        self,
        *,
        access_token: str,
        refresh_token: str | None = None,
        token_scopes: list[str] | None = None,
        token_expires_at: datetime | None = None,
    ) -> GoogleAnalyticsOAuthTokenData:
        return GoogleAnalyticsOAuthTokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_scopes=token_scopes or [],
            token_expires_at=token_expires_at,
        )

    def refresh_oauth(self, *, refresh_token: str) -> GoogleAnalyticsOAuthTokenData:
        return GoogleAnalyticsOAuthTokenData(
            access_token="new-access-token",
            refresh_token=refresh_token,
            token_scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            token_expires_at=datetime.now(UTC) + timedelta(hours=1),
        )


def _service(db_session: Session) -> GoogleAnalyticsService:
    return GoogleAnalyticsService(
        GoogleAnalyticsRepository(db_session),
        connector=FakeGoogleAnalyticsConnector(),
    )


def test_google_analytics_service_creates_and_lists_properties(db_session: Session) -> None:
    """The service manages GA4 properties."""

    service = _service(db_session)

    created = service.create_property(
        GoogleAnalyticsPropertyCreate(
            property_id="properties/123",
            property_name="Example GA4",
            measurement_id="G-TEST123",
        ),
    )
    properties = service.list_properties(PaginationParams())

    assert created.id is not None
    assert properties.total == 1
    with pytest.raises(HTTPException):
        service.create_property(
            GoogleAnalyticsPropertyCreate(
                property_id="properties/123",
                property_name="Duplicate",
            ),
        )


def test_google_analytics_service_encrypts_and_refreshes_oauth_tokens(db_session: Session) -> None:
    """OAuth tokens are encrypted and refreshed without exposing secrets."""

    service = _service(db_session)
    created = service.create_property(
        GoogleAnalyticsPropertyCreate(property_id="properties/123", property_name="Example GA4"),
    )

    connected = service.connect_oauth(
        GoogleAnalyticsOAuthConnectRequest(
            property_id=created.id,
            access_token="access-token",
            refresh_token="refresh-token",
            token_scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            token_expires_at=datetime.now(UTC) + timedelta(hours=1),
        ),
    )
    refreshed = service.refresh_oauth(GoogleAnalyticsOAuthRefreshRequest(property_id=created.id))
    stored = GoogleAnalyticsRepository(db_session).get_property(created.id)

    assert connected.status == "CONNECTED"
    assert refreshed.status == "REFRESHED"
    assert stored is not None
    assert stored.encrypted_access_token != "new-access-token"
    assert stored.encrypted_refresh_token != "refresh-token"
    assert decrypt_secret(stored.encrypted_access_token or "") == "new-access-token"
    assert decrypt_secret(stored.encrypted_refresh_token or "") == "refresh-token"


def test_google_analytics_service_runs_idempotent_import(db_session: Session) -> None:
    """Manual imports are journaled and upsert imported rows idempotently."""

    service = _service(db_session)
    created = service.create_property(
        GoogleAnalyticsPropertyCreate(property_id="properties/123", property_name="Example GA4"),
    )
    payload = GoogleAnalyticsImportRequest(
        property_id=created.id,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 7),
    )

    first_import = service.run_manual_import(payload)
    second_import = service.run_manual_import(payload)

    assert first_import.status == "COMPLETED"
    assert second_import.status == "COMPLETED"
    assert first_import.imported_rows == 1
    assert second_import.imported_rows == 1
    assert first_import.duration_seconds is not None
    assert first_import.duration_seconds >= 0
    assert db_session.query(GoogleAnalyticsMetric).count() == 1
    assert db_session.query(GoogleAnalyticsDimension).count() == 1


def test_google_analytics_service_rejects_invalid_import_requests(db_session: Session) -> None:
    """The service validates import periods and property state before using the connector."""

    service = _service(db_session)
    created = service.create_property(
        GoogleAnalyticsPropertyCreate(property_id="properties/123", property_name="Example GA4", enabled=False),
    )

    with pytest.raises(HTTPException):
        service.run_manual_import(
            GoogleAnalyticsImportRequest(
                property_id=created.id,
                start_date=date(2026, 7, 7),
                end_date=date(2026, 7, 1),
            ),
        )
    with pytest.raises(HTTPException):
        service.run_manual_import(
            GoogleAnalyticsImportRequest(
                property_id=created.id,
                start_date=date(2026, 7, 1),
                end_date=date(2026, 7, 7),
            ),
        )


def test_google_analytics_service_lists_metrics_with_filters_and_pagination(db_session: Session) -> None:
    """The service exposes filtered and paginated metrics for the API."""

    service = _service(db_session)
    created = service.create_property(
        GoogleAnalyticsPropertyCreate(property_id="properties/123", property_name="Example GA4"),
    )
    service.run_manual_import(
        GoogleAnalyticsImportRequest(
            property_id=created.id,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 7),
        ),
    )

    metrics = service.list_metrics(
        PaginationParams(page=1, page_size=10, sort="sessions", order="desc"),
        filters=GoogleAnalyticsMetricFilters(property_id=created.id, source="google", search="organic"),
    )

    assert metrics.total == 1
    assert metrics.pages == 1
    assert metrics.filters["property_id"] == created.id
    assert metrics.items[0].sessions == 12


def test_google_analytics_service_rejects_invalid_metric_filters_and_sort(db_session: Session) -> None:
    """The service validates metric periods and converts repository sort errors."""

    service = _service(db_session)

    with pytest.raises(HTTPException) as invalid_period:
        service.list_metrics(
            PaginationParams(),
            filters=GoogleAnalyticsMetricFilters(date_from=date(2026, 7, 7), date_to=date(2026, 7, 1)),
        )
    with pytest.raises(HTTPException) as invalid_sort:
        service.list_metrics(PaginationParams(sort="not_allowed"))

    assert invalid_period.value.status_code == 422
    assert invalid_sort.value.status_code == 422


def test_google_analytics_service_computes_overview_and_breakdowns(db_session: Session) -> None:
    """The service computes KPIs and specialized endpoint data backend-side."""

    service = _service(db_session)
    created = service.create_property(
        GoogleAnalyticsPropertyCreate(property_id="properties/123", property_name="Example GA4"),
    )
    service.run_manual_import(
        GoogleAnalyticsImportRequest(
            property_id=created.id,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 7),
        ),
    )

    overview = service.overview(GoogleAnalyticsMetricFilters(property_id=created.id))
    traffic = service.traffic(GoogleAnalyticsMetricFilters(property_id=created.id))
    acquisition = service.acquisition(GoogleAnalyticsMetricFilters(property_id=created.id))
    engagement = service.engagement(GoogleAnalyticsMetricFilters(property_id=created.id))
    conversions = service.conversions(GoogleAnalyticsMetricFilters(property_id=created.id))
    revenue = service.revenue(GoogleAnalyticsMetricFilters(property_id=created.id))

    assert overview.data.sessions == 12
    assert overview.data.users == 10
    assert overview.data.new_users == 4
    assert overview.data.engagement_rate == 0.75
    assert overview.data.average_session_duration == 42.5
    assert overview.data.conversions == 2.0
    assert overview.data.total_revenue == 120.0
    assert traffic.dimension == "source"
    assert traffic.data[0].dimension == "google"
    assert acquisition.dimension == "medium"
    assert acquisition.data[0].dimension == "organic"
    assert engagement.dimension == "device_category"
    assert conversions.data[0].conversions == 2.0
    assert revenue.data[0].total_revenue == 120.0


def test_google_analytics_service_returns_enriched_history(db_session: Session) -> None:
    """The service enriches import history with property information."""

    service = _service(db_session)
    created = service.create_property(
        GoogleAnalyticsPropertyCreate(property_id="properties/123", property_name="Example GA4"),
    )
    service.run_manual_import(
        GoogleAnalyticsImportRequest(
            property_id=created.id,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 7),
        ),
    )

    history = service.history(
        PaginationParams(),
        filters=GoogleAnalyticsImportFilters(property_id=created.id, status=GoogleAnalyticsImportStatus.COMPLETED),
    )

    assert history.total == 1
    assert history.filters["status"] == "COMPLETED"
    assert history.items[0].property_name == "Example GA4"
    assert history.items[0].google_property_id == "properties/123"
    assert history.items[0].duration_seconds is not None
