"""Injectable Google Search Console connector boundary."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


class GoogleSearchConsoleConnectorError(Exception):
    """Raised when the Google Search Console connector cannot fetch data."""


@dataclass(frozen=True)
class GoogleSearchConsolePropertyData:
    """Property data returned by the connector."""

    site_url: str
    property_type: str = "URL_PREFIX"
    permission_level: str | None = None
    status: str = "ACTIVE"


@dataclass(frozen=True)
class GoogleSearchConsolePerformanceData:
    """Performance row returned by the connector."""

    date: date
    page: str | None = None
    query: str | None = None
    country: str | None = None
    device: str | None = None
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    position: float = 0.0


@dataclass(frozen=True)
class GoogleSearchConsoleIndexCoverageData:
    """Index coverage row returned by the connector."""

    url: str
    coverage_state: str
    indexing_state: str | None = None
    verdict: str | None = None
    page_fetch_state: str | None = None
    google_canonical: str | None = None
    user_canonical: str | None = None
    last_crawl_time: datetime | None = None
    inspected_at: datetime | None = None


@dataclass(frozen=True)
class GoogleSearchConsoleSitemapData:
    """Sitemap row returned by the connector."""

    sitemap_url: str
    status: str | None = None
    last_submitted_at: datetime | None = None
    last_downloaded_at: datetime | None = None
    warnings: int = 0
    errors: int = 0
    contents: dict[str, Any] | None = None


@dataclass(frozen=True)
class GoogleSearchConsoleImportData:
    """Grouped data returned by the connector for one import."""

    properties: list[GoogleSearchConsolePropertyData] = field(default_factory=list)
    performances: list[GoogleSearchConsolePerformanceData] = field(default_factory=list)
    index_coverages: list[GoogleSearchConsoleIndexCoverageData] = field(default_factory=list)
    sitemaps: list[GoogleSearchConsoleSitemapData] = field(default_factory=list)


class GoogleSearchConsoleConnector(ABC):
    """Connector contract implemented by real and fake Google Search Console clients."""

    @abstractmethod
    def list_properties(self) -> list[GoogleSearchConsolePropertyData]:
        """Return Google Search Console properties available to the backend."""

    @abstractmethod
    def fetch_performance(
        self,
        site_url: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[GoogleSearchConsolePerformanceData]:
        """Return performance rows for one property."""

    @abstractmethod
    def fetch_index_coverage(self, site_url: str) -> list[GoogleSearchConsoleIndexCoverageData]:
        """Return index coverage rows for one property."""

    @abstractmethod
    def fetch_sitemaps(self, site_url: str) -> list[GoogleSearchConsoleSitemapData]:
        """Return sitemap rows for one property."""


class PreparedGoogleSearchConsoleConnector(GoogleSearchConsoleConnector):
    """Prepared non-network connector used until Google credentials are configured."""

    def list_properties(self) -> list[GoogleSearchConsolePropertyData]:
        """Return no data without making network calls."""

        return []

    def fetch_performance(
        self,
        site_url: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[GoogleSearchConsolePerformanceData]:
        """Return no performance rows without making network calls."""

        return []

    def fetch_index_coverage(self, site_url: str) -> list[GoogleSearchConsoleIndexCoverageData]:
        """Return no index coverage rows without making network calls."""

        return []

    def fetch_sitemaps(self, site_url: str) -> list[GoogleSearchConsoleSitemapData]:
        """Return no sitemap rows without making network calls."""

        return []
