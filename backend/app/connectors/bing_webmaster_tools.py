"""Bing Webmaster Tools connector interface and default implementations."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol


class BingWebmasterAuthenticationError(RuntimeError):
    """Raised when Bing Webmaster Tools credentials are rejected."""


class BingWebmasterNetworkError(RuntimeError):
    """Raised when Bing Webmaster Tools cannot be reached."""


@dataclass(frozen=True)
class BingWebmasterCredentials:
    """Credential bundle passed from the service to the connector."""

    auth_type: str
    client_id: str | None = None
    client_secret: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    api_key: str | None = None
    token_expires_at: datetime | None = None
    scopes: list[str] | None = None


@dataclass(frozen=True)
class BingWebmasterSiteData:
    """Site data returned by a Bing Webmaster Tools connector."""

    site_url: str
    is_verified: bool = True


@dataclass(frozen=True)
class BingWebmasterMetricRow:
    """Search performance row returned by a Bing Webmaster Tools connector."""

    date: date
    query: str | None = None
    page_url: str | None = None
    country: str | None = None
    device: str | None = None
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    average_position: float = 0.0


@dataclass(frozen=True)
class BingWebmasterCrawlStatRow:
    """Crawl statistic row returned by a Bing Webmaster Tools connector."""

    date: date
    url: str
    http_status: int | None = None
    issue_type: str | None = None
    issue_category: str | None = None
    severity: str | None = None
    details: str | None = None


@dataclass(frozen=True)
class BingWebmasterSitemapRow:
    """Sitemap row returned by a Bing Webmaster Tools connector."""

    sitemap_url: str
    status: str | None = None
    submitted_at: datetime | None = None
    last_crawled_at: datetime | None = None
    url_count: int = 0
    error_count: int = 0
    warning_count: int = 0


@dataclass(frozen=True)
class BingWebmasterTokenData:
    """Refreshed OAuth token data returned by a Bing Webmaster Tools connector."""

    access_token: str
    refresh_token: str | None = None
    token_expires_at: datetime | None = None
    scopes: list[str] | None = None


class BingWebmasterConnector(Protocol):
    """Protocol implemented by Bing Webmaster Tools connectors."""

    def list_sites(self, credentials: BingWebmasterCredentials) -> list[BingWebmasterSiteData]:
        """Return sites visible to the configured Bing account."""

    def fetch_metrics(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
        date_from: date,
        date_to: date,
    ) -> list[BingWebmasterMetricRow]:
        """Return performance metrics for one site."""

    def fetch_crawl_stats(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
        date_from: date,
        date_to: date,
    ) -> list[BingWebmasterCrawlStatRow]:
        """Return crawl statistics for one site."""

    def fetch_sitemaps(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
    ) -> list[BingWebmasterSitemapRow]:
        """Return sitemaps for one site."""

    def refresh_access_token(self, credentials: BingWebmasterCredentials) -> BingWebmasterTokenData:
        """Refresh OAuth token data."""


class NotConfiguredBingWebmasterConnector:
    """Default connector that prevents implicit Internet calls."""

    def list_sites(self, credentials: BingWebmasterCredentials) -> list[BingWebmasterSiteData]:
        """Return no sites when no real connector is configured."""

        return []

    def fetch_metrics(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
        date_from: date,
        date_to: date,
    ) -> list[BingWebmasterMetricRow]:
        """Raise until a real connector is injected."""

        raise RuntimeError("Bing Webmaster Tools connector is not configured.")

    def fetch_crawl_stats(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
        date_from: date,
        date_to: date,
    ) -> list[BingWebmasterCrawlStatRow]:
        """Raise until a real connector is injected."""

        raise RuntimeError("Bing Webmaster Tools connector is not configured.")

    def fetch_sitemaps(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
    ) -> list[BingWebmasterSitemapRow]:
        """Raise until a real connector is injected."""

        raise RuntimeError("Bing Webmaster Tools connector is not configured.")

    def refresh_access_token(self, credentials: BingWebmasterCredentials) -> BingWebmasterTokenData:
        """Raise until a real connector is injected."""

        raise RuntimeError("Bing Webmaster Tools connector is not configured.")


class FakeBingWebmasterConnector:
    """Deterministic fake connector for tests and local service checks."""

    def __init__(self, *, mode: str = "success", duplicate_metrics: bool = False) -> None:
        self.mode = mode
        self.duplicate_metrics = duplicate_metrics
        self.calls: list[str] = []

    def list_sites(self, credentials: BingWebmasterCredentials) -> list[BingWebmasterSiteData]:
        """Return deterministic fake sites."""

        self._raise_if_needed()
        self.calls.append("list_sites")
        return [BingWebmasterSiteData(site_url="https://example.com/", is_verified=True)]

    def fetch_metrics(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
        date_from: date,
        date_to: date,
    ) -> list[BingWebmasterMetricRow]:
        """Return deterministic fake metrics."""

        self._raise_if_needed()
        self.calls.append("fetch_metrics")
        rows = [
            BingWebmasterMetricRow(
                date=date_from,
                query="audit seo",
                page_url=f"{site_url.rstrip('/')}/audit",
                country="FRA",
                device="DESKTOP",
                clicks=10,
                impressions=100,
                ctr=0.1,
                average_position=2.5,
            ),
        ]
        if self.duplicate_metrics:
            rows.append(rows[0])
        return [] if self.mode == "empty" else rows

    def fetch_crawl_stats(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
        date_from: date,
        date_to: date,
    ) -> list[BingWebmasterCrawlStatRow]:
        """Return deterministic fake crawl statistics."""

        self._raise_if_needed()
        self.calls.append("fetch_crawl_stats")
        if self.mode == "empty":
            return []
        return [
            BingWebmasterCrawlStatRow(
                date=date_from,
                url=f"{site_url.rstrip('/')}/missing",
                http_status=404,
                issue_type="NOT_FOUND",
                issue_category="CRAWL",
                severity="ERROR",
                details="Page introuvable",
            ),
        ]

    def fetch_sitemaps(
        self,
        credentials: BingWebmasterCredentials,
        site_url: str,
    ) -> list[BingWebmasterSitemapRow]:
        """Return deterministic fake sitemaps."""

        self._raise_if_needed()
        self.calls.append("fetch_sitemaps")
        if self.mode == "empty":
            return []
        return [
            BingWebmasterSitemapRow(
                sitemap_url=f"{site_url.rstrip('/')}/sitemap.xml",
                status="OK",
                url_count=42,
                error_count=0,
                warning_count=1,
            ),
        ]

    def refresh_access_token(self, credentials: BingWebmasterCredentials) -> BingWebmasterTokenData:
        """Return deterministic fake refreshed token data."""

        self._raise_if_needed()
        self.calls.append("refresh_access_token")
        return BingWebmasterTokenData(
            access_token="fake-refreshed-access-token",
            refresh_token=credentials.refresh_token,
            token_expires_at=credentials.token_expires_at,
            scopes=credentials.scopes or [],
        )

    def _raise_if_needed(self) -> None:
        if self.mode == "auth_error":
            raise BingWebmasterAuthenticationError("Authentification Bing Webmaster Tools refusee.")
        if self.mode == "network_error":
            raise BingWebmasterNetworkError("Bing Webmaster Tools indisponible.")
