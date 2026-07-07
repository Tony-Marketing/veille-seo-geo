"""Google Analytics 4 connector interface and default implementation."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Protocol


@dataclass(frozen=True)
class GoogleAnalyticsPropertyData:
    """Property data returned by a Google Analytics connector."""

    property_id: str
    property_name: str
    account_name: str | None = None
    measurement_id: str | None = None


@dataclass(frozen=True)
class GoogleAnalyticsMetricRow:
    """Metric row returned by a Google Analytics connector."""

    date: date
    source: str | None = None
    medium: str | None = None
    campaign: str | None = None
    device_category: str | None = None
    country: str | None = None
    users: int = 0
    new_users: int = 0
    sessions: int = 0
    engaged_sessions: int = 0
    screen_page_views: int = 0
    average_session_duration: float = 0.0
    engagement_rate: float = 0.0
    conversions: float = 0.0
    total_revenue: float = 0.0


@dataclass(frozen=True)
class GoogleAnalyticsOAuthTokenData:
    """OAuth token data returned by a Google Analytics connector."""

    access_token: str
    refresh_token: str | None = None
    token_scopes: list[str] = field(default_factory=list)
    token_expires_at: datetime | None = None


class GoogleAnalyticsConnector(Protocol):
    """Protocol implemented by Google Analytics connectors."""

    def list_properties(self) -> list[GoogleAnalyticsPropertyData]:
        """Return properties visible to the configured Google account."""

    def fetch_metrics(
        self,
        *,
        property_id: str,
        start_date: date,
        end_date: date,
        metrics: list[str],
        dimensions: list[str],
    ) -> list[GoogleAnalyticsMetricRow]:
        """Return metric rows for one property."""

    def connect_oauth(
        self,
        *,
        access_token: str,
        refresh_token: str | None = None,
        token_scopes: list[str] | None = None,
        token_expires_at: datetime | None = None,
    ) -> GoogleAnalyticsOAuthTokenData:
        """Prepare OAuth token data from a connection flow."""

    def refresh_oauth(self, *, refresh_token: str) -> GoogleAnalyticsOAuthTokenData:
        """Refresh OAuth token data."""


class NotConfiguredGoogleAnalyticsConnector:
    """Default connector that prevents implicit Internet calls."""

    def list_properties(self) -> list[GoogleAnalyticsPropertyData]:
        """Return no properties when no real connector is configured."""

        return []

    def fetch_metrics(
        self,
        *,
        property_id: str,
        start_date: date,
        end_date: date,
        metrics: list[str],
        dimensions: list[str],
    ) -> list[GoogleAnalyticsMetricRow]:
        """Raise until a real connector is injected."""

        raise RuntimeError("Google Analytics connector is not configured.")

    def connect_oauth(
        self,
        *,
        access_token: str,
        refresh_token: str | None = None,
        token_scopes: list[str] | None = None,
        token_expires_at: datetime | None = None,
    ) -> GoogleAnalyticsOAuthTokenData:
        """Raise until a real connector is injected."""

        raise RuntimeError("Google Analytics connector is not configured.")

    def refresh_oauth(self, *, refresh_token: str) -> GoogleAnalyticsOAuthTokenData:
        """Raise until a real connector is injected."""

        raise RuntimeError("Google Analytics connector is not configured.")
