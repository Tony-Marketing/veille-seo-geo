"""Pydantic schemas for Bing Webmaster Tools."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.app.schemas.common import OrmModel, TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class BingWebmasterAuthType(StrEnum):
    """Supported Bing Webmaster Tools authentication modes."""

    API_KEY = "API_KEY"
    OAUTH = "OAUTH"


class BingWebmasterImportStatus(StrEnum):
    """Known Bing Webmaster Tools import statuses."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class BingWebmasterConnectionCreate(BaseModel):
    """Payload used to create a Bing Webmaster Tools connection."""

    website_id: int | None = Field(default=None, gt=0)
    auth_type: BingWebmasterAuthType = BingWebmasterAuthType.API_KEY
    client_id: str | None = Field(default=None, max_length=255)
    client_secret: str | None = Field(default=None, min_length=1)
    access_token: str | None = Field(default=None, min_length=1)
    refresh_token: str | None = Field(default=None, min_length=1)
    api_key: str | None = Field(default=None, min_length=1)
    token_expires_at: datetime | None = None
    scopes: list[str] = Field(default_factory=list)
    is_active: bool = True


class BingWebmasterConnectionUpdate(BaseModel):
    """Payload used to update a Bing Webmaster Tools connection."""

    website_id: int | None = Field(default=None, gt=0)
    auth_type: BingWebmasterAuthType | None = None
    client_id: str | None = Field(default=None, max_length=255)
    client_secret: str | None = Field(default=None, min_length=1)
    access_token: str | None = Field(default=None, min_length=1)
    refresh_token: str | None = Field(default=None, min_length=1)
    api_key: str | None = Field(default=None, min_length=1)
    token_expires_at: datetime | None = None
    scopes: list[str] | None = None
    is_active: bool | None = None


class BingWebmasterConnectionRead(TimestampRead):
    """Bing Webmaster Tools connection returned by the API without secrets."""

    id: int
    website_id: int | None
    auth_type: BingWebmasterAuthType
    client_id: str | None
    token_expires_at: datetime | None
    scopes: list[str]
    is_active: bool
    last_sync_at: datetime | None
    last_error: str | None
    has_client_secret: bool = False
    has_access_token: bool = False
    has_refresh_token: bool = False
    has_api_key: bool = False


class BingWebmasterSiteRead(TimestampRead):
    """Bing Webmaster Tools site returned by the API."""

    id: int
    connection_id: int
    website_id: int | None
    site_url: str
    is_verified: bool
    is_active: bool
    last_import_at: datetime | None


class BingWebmasterMetricRead(OrmModel):
    """Bing Webmaster Tools metric row returned by the API."""

    id: int
    bing_site_id: int
    import_id: int | None
    date: date
    query: str | None
    page_url: str | None
    country: str | None
    device: str | None
    clicks: int
    impressions: int
    ctr: float
    average_position: float
    created_at: datetime


class BingWebmasterCrawlStatRead(OrmModel):
    """Bing Webmaster Tools crawl statistic returned by the API."""

    id: int
    bing_site_id: int
    import_id: int | None
    date: date
    url: str
    http_status: int | None
    issue_type: str | None
    issue_category: str | None
    severity: str | None
    details: str | None
    created_at: datetime


class BingWebmasterSitemapRead(TimestampRead):
    """Bing Webmaster Tools sitemap returned by the API."""

    id: int
    bing_site_id: int
    import_id: int | None
    sitemap_url: str
    status: str | None
    submitted_at: datetime | None
    last_crawled_at: datetime | None
    url_count: int
    error_count: int
    warning_count: int


class BingWebmasterImportRequest(BaseModel):
    """Payload used to launch a manual Bing Webmaster Tools import."""

    connection_id: int = Field(gt=0)
    bing_site_id: int | None = Field(default=None, gt=0)
    date_from: date
    date_to: date
    import_type: str = Field(default="MANUAL", max_length=50)


class BingWebmasterImportRunRead(OrmModel):
    """Bing Webmaster Tools import execution log returned by the API."""

    id: int
    connection_id: int
    bing_site_id: int | None
    import_type: str
    status: BingWebmasterImportStatus
    started_at: datetime | None
    finished_at: datetime | None
    items_processed: int
    error_message: str | None
    created_at: datetime
    duration_seconds: float | None = None


class BingWebmasterMetricFilters(BaseModel):
    """REST filters supported by Bing Webmaster Tools metric endpoints."""

    website_id: int | None = Field(default=None, gt=0)
    bing_site_id: int | None = Field(default=None, gt=0)
    date_from: date | None = None
    date_to: date | None = None
    query: str | None = Field(default=None, max_length=1000)
    page_url: str | None = Field(default=None, max_length=1000)
    country: str | None = Field(default=None, max_length=10)
    device: str | None = Field(default=None, max_length=40)
    search: str | None = Field(default=None, max_length=255)


class BingWebmasterCrawlStatFilters(BaseModel):
    """REST filters supported by Bing Webmaster Tools crawl statistic endpoints."""

    website_id: int | None = Field(default=None, gt=0)
    bing_site_id: int | None = Field(default=None, gt=0)
    date_from: date | None = None
    date_to: date | None = None
    status: int | None = Field(default=None, ge=100, le=599)
    issue_type: str | None = Field(default=None, max_length=255)
    severity: str | None = Field(default=None, max_length=80)
    search: str | None = Field(default=None, max_length=255)


class BingWebmasterSitemapFilters(BaseModel):
    """REST filters supported by Bing Webmaster Tools sitemap endpoints."""

    website_id: int | None = Field(default=None, gt=0)
    bing_site_id: int | None = Field(default=None, gt=0)
    status: str | None = Field(default=None, max_length=80)
    search: str | None = Field(default=None, max_length=255)


class BingWebmasterImportRunFilters(BaseModel):
    """REST filters supported by Bing Webmaster Tools import history endpoints."""

    connection_id: int | None = Field(default=None, gt=0)
    bing_site_id: int | None = Field(default=None, gt=0)
    status: BingWebmasterImportStatus | None = None
    import_type: str | None = Field(default=None, max_length=50)
    search: str | None = Field(default=None, max_length=255)


class BingWebmasterMetricListResponse(PaginatedResponse[BingWebmasterMetricRead]):
    """Paginated Bing Webmaster Tools metrics with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)


class BingWebmasterCrawlStatListResponse(PaginatedResponse[BingWebmasterCrawlStatRead]):
    """Paginated Bing Webmaster Tools crawl statistics with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)


class BingWebmasterSitemapListResponse(PaginatedResponse[BingWebmasterSitemapRead]):
    """Paginated Bing Webmaster Tools sitemaps with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)


class BingWebmasterImportRunListResponse(PaginatedResponse[BingWebmasterImportRunRead]):
    """Paginated Bing Webmaster Tools import history with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)


BingWebmasterConnectionListResponse = PaginatedResponse[BingWebmasterConnectionRead]
BingWebmasterSiteListResponse = PaginatedResponse[BingWebmasterSiteRead]
