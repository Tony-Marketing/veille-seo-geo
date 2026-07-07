"""Google Search Console connector interface and default implementation."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class GoogleSearchConsolePropertyData:
    """Property data returned by a Google Search Console connector."""

    google_property_id: str
    property_url: str
    property_type: str = "URL_PREFIX"
    display_name: str | None = None
    permission_level: str | None = None


@dataclass(frozen=True)
class GoogleSearchConsolePerformanceRow:
    """Performance row returned by a Google Search Console connector."""

    date: date
    query: str | None = None
    page: str | None = None
    country: str | None = None
    device: str | None = None
    search_type: str = "web"
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    position: float = 0.0


@dataclass(frozen=True)
class GoogleSearchConsoleIndexCoverageRow:
    """Index coverage row returned by a Google Search Console connector."""

    url: str
    coverage_state: str
    google_state: str | None = None
    indexing_state: str | None = None
    page_fetch_state: str | None = None
    robots_txt_state: str | None = None
    verdict: str | None = None
    issue_type: str | None = None
    sitemap: str | None = None
    referring_urls: list[str] = field(default_factory=list)
    last_crawled_at: datetime | None = None


@dataclass(frozen=True)
class GoogleSearchConsoleSitemapRow:
    """Sitemap row returned by a Google Search Console connector."""

    sitemap_url: str
    sitemap_type: str | None = None
    is_pending: bool = False
    is_sitemaps_index: bool = False
    submitted_at: datetime | None = None
    last_downloaded_at: datetime | None = None
    warnings: int = 0
    errors: int = 0
    contents: dict[str, Any] | None = None


class GoogleSearchConsoleConnector(Protocol):
    """Protocol implemented by Google Search Console connectors."""

    def list_properties(self) -> list[GoogleSearchConsolePropertyData]:
        """Return properties visible to the configured Google account."""

    def fetch_performance(
        self,
        *,
        property_url: str,
        start_date: date,
        end_date: date,
        dimensions: list[str],
        search_type: str = "web",
    ) -> list[GoogleSearchConsolePerformanceRow]:
        """Return performance rows for one property."""

    def fetch_index_coverage(self, *, property_url: str) -> list[GoogleSearchConsoleIndexCoverageRow]:
        """Return index coverage rows for one property."""

    def fetch_sitemaps(self, *, property_url: str) -> list[GoogleSearchConsoleSitemapRow]:
        """Return sitemap rows for one property."""


class NotConfiguredGoogleSearchConsoleConnector:
    """Default connector that prevents implicit Internet calls."""

    def list_properties(self) -> list[GoogleSearchConsolePropertyData]:
        """Return no properties when no real connector is configured."""

        return []

    def fetch_performance(
        self,
        *,
        property_url: str,
        start_date: date,
        end_date: date,
        dimensions: list[str],
        search_type: str = "web",
    ) -> list[GoogleSearchConsolePerformanceRow]:
        """Raise until a real connector is injected."""

        raise RuntimeError("Google Search Console connector is not configured.")

    def fetch_index_coverage(self, *, property_url: str) -> list[GoogleSearchConsoleIndexCoverageRow]:
        """Raise until a real connector is injected."""

        raise RuntimeError("Google Search Console connector is not configured.")

    def fetch_sitemaps(self, *, property_url: str) -> list[GoogleSearchConsoleSitemapRow]:
        """Raise until a real connector is injected."""

        raise RuntimeError("Google Search Console connector is not configured.")
