"""Pydantic schemas for Google Search Console."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class GoogleSearchConsolePropertyType(StrEnum):
    """Known Google Search Console property types."""

    DOMAIN = "DOMAIN"
    URL_PREFIX = "URL_PREFIX"


class GoogleSearchConsoleImportStatus(StrEnum):
    """Known Google Search Console import statuses."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class GoogleSearchConsolePropertyCreate(BaseModel):
    """Payload used to create a Google Search Console property."""

    website_id: int | None = Field(default=None, gt=0)
    google_property_id: str = Field(min_length=1, max_length=500)
    property_url: str = Field(min_length=1, max_length=500)
    property_type: GoogleSearchConsolePropertyType = GoogleSearchConsolePropertyType.URL_PREFIX
    display_name: str | None = Field(default=None, max_length=255)
    permission_level: str | None = Field(default=None, max_length=80)
    is_active: bool = True


class GoogleSearchConsolePropertyUpdate(BaseModel):
    """Payload used to update a Google Search Console property."""

    website_id: int | None = Field(default=None, gt=0)
    google_property_id: str | None = Field(default=None, min_length=1, max_length=500)
    property_url: str | None = Field(default=None, min_length=1, max_length=500)
    property_type: GoogleSearchConsolePropertyType | None = None
    display_name: str | None = Field(default=None, max_length=255)
    permission_level: str | None = Field(default=None, max_length=80)
    is_active: bool | None = None


class GoogleSearchConsoleOAuthTokenUpdate(BaseModel):
    """Payload used to store encrypted OAuth tokens."""

    access_token: str | None = Field(default=None, min_length=1)
    refresh_token: str | None = Field(default=None, min_length=1)
    token_scopes: list[str] = Field(default_factory=list)
    token_expires_at: datetime | None = None


class GoogleSearchConsolePropertyRead(TimestampRead):
    """Google Search Console property returned by the API."""

    id: int
    website_id: int | None
    google_property_id: str
    property_url: str
    property_type: GoogleSearchConsolePropertyType
    display_name: str | None
    permission_level: str | None
    is_active: bool
    token_scopes: list[str]
    token_expires_at: datetime | None
    last_sync_at: datetime | None = None


class GoogleSearchConsolePerformanceFilters(BaseModel):
    """REST filters supported by the performance listing endpoint."""

    start_date: date | None = None
    end_date: date | None = None
    page: str | None = Field(default=None, max_length=1000)
    query: str | None = Field(default=None, max_length=1000)
    country: str | None = Field(default=None, max_length=10)
    device: str | None = Field(default=None, max_length=40)


class GoogleSearchConsolePerformanceCreate(BaseModel):
    """Payload used to create or upsert performance metrics."""

    property_id: int = Field(gt=0)
    import_id: int | None = Field(default=None, gt=0)
    date: date
    query: str | None = Field(default=None, max_length=1000)
    page: str | None = Field(default=None, max_length=1000)
    country: str | None = Field(default=None, max_length=10)
    device: str | None = Field(default=None, max_length=40)
    search_type: str = Field(default="web", max_length=40)
    clicks: int = Field(default=0, ge=0)
    impressions: int = Field(default=0, ge=0)
    ctr: float = Field(default=0.0, ge=0)
    position: float = Field(default=0.0, ge=0)


class GoogleSearchConsolePerformanceRead(TimestampRead):
    """Performance metrics returned by the API."""

    id: int
    property_id: int
    import_id: int | None
    date: date
    query: str | None
    page: str | None
    country: str | None
    device: str | None
    search_type: str
    clicks: int
    impressions: int
    ctr: float
    position: float


class GoogleSearchConsoleIndexCoverageCreate(BaseModel):
    """Payload used to create or upsert index coverage data."""

    property_id: int = Field(gt=0)
    import_id: int | None = Field(default=None, gt=0)
    url: str = Field(min_length=1, max_length=1000)
    coverage_state: str = Field(min_length=1, max_length=80)
    google_state: str | None = Field(default=None, max_length=120)
    indexing_state: str | None = Field(default=None, max_length=120)
    page_fetch_state: str | None = Field(default=None, max_length=120)
    robots_txt_state: str | None = Field(default=None, max_length=120)
    verdict: str | None = Field(default=None, max_length=80)
    issue_type: str | None = Field(default=None, max_length=255)
    sitemap: str | None = Field(default=None, max_length=1000)
    referring_urls: list[str] = Field(default_factory=list)
    last_crawled_at: datetime | None = None


class GoogleSearchConsoleIndexCoverageRead(TimestampRead):
    """Index coverage data returned by the API."""

    id: int
    property_id: int
    import_id: int | None
    url: str
    coverage_state: str
    google_state: str | None
    indexing_state: str | None
    page_fetch_state: str | None
    robots_txt_state: str | None
    verdict: str | None
    issue_type: str | None
    sitemap: str | None
    referring_urls: list[str]
    last_crawled_at: datetime | None


class GoogleSearchConsoleSitemapCreate(BaseModel):
    """Payload used to create or upsert sitemap data."""

    property_id: int = Field(gt=0)
    import_id: int | None = Field(default=None, gt=0)
    sitemap_url: str = Field(min_length=1, max_length=1000)
    sitemap_type: str | None = Field(default=None, max_length=80)
    is_pending: bool = False
    is_sitemaps_index: bool = False
    submitted_at: datetime | None = None
    last_downloaded_at: datetime | None = None
    warnings: int = Field(default=0, ge=0)
    errors: int = Field(default=0, ge=0)
    contents: dict[str, Any] | None = None


class GoogleSearchConsoleSitemapRead(TimestampRead):
    """Sitemap data returned by the API."""

    id: int
    property_id: int
    import_id: int | None
    sitemap_url: str
    sitemap_type: str | None
    is_pending: bool
    is_sitemaps_index: bool
    submitted_at: datetime | None
    last_downloaded_at: datetime | None
    warnings: int
    errors: int
    contents: dict[str, Any] | None
    url_count: int = 0


class GoogleSearchConsoleImportCreate(BaseModel):
    """Payload used to create a Google Search Console import log."""

    property_id: int = Field(gt=0)
    import_type: str = Field(default="MANUAL", max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    dimensions: list[str] = Field(default_factory=list)
    rows_requested: int = Field(default=0, ge=0)


class GoogleSearchConsoleManualImportRequest(BaseModel):
    """Payload used to launch a manual import."""

    property_id: int = Field(gt=0)
    start_date: date
    end_date: date
    dimensions: list[str] = Field(default_factory=lambda: ["query", "page"])
    search_type: str = Field(default="web", max_length=40)


class GoogleSearchConsoleImportRead(TimestampRead):
    """Import execution log returned by the API."""

    id: int
    property_id: int
    import_type: str
    status: GoogleSearchConsoleImportStatus
    start_date: date | None
    end_date: date | None
    dimensions: list[str]
    rows_requested: int
    rows_imported: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None = None


GoogleSearchConsolePropertyList = PaginatedResponse[GoogleSearchConsolePropertyRead]
GoogleSearchConsolePerformanceList = PaginatedResponse[GoogleSearchConsolePerformanceRead]
GoogleSearchConsoleSitemapList = PaginatedResponse[GoogleSearchConsoleSitemapRead]
GoogleSearchConsoleImportList = PaginatedResponse[GoogleSearchConsoleImportRead]


class GoogleSearchConsoleIndexCoverageList(PaginatedResponse[GoogleSearchConsoleIndexCoverageRead]):
    """Paginated index coverage rows with backend-computed aggregates."""

    valid_pages: int = 0
    excluded_pages: int = 0
    errors: int = 0
    warnings: int = 0
