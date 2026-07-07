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
    GoogleAnalyticsImportRequest,
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
