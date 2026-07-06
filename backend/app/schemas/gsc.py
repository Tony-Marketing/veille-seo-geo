"""Pydantic schemas for Google Search Console backend."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class GscImportStatus(StrEnum):
    """Known GSC import execution states."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GscOAuthStatus(StrEnum):
    """Known OAuth credential states."""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    REVOKED = "REVOKED"


class GscOAuthAuthorizationUrlRead(BaseModel):
    """Prepared OAuth authorization URL."""

    authorization_url: str
    scopes: list[str]
    configured: bool


class GscOAuthCallback(BaseModel):
    """Payload used by the preparatory OAuth callback."""

    code: str = Field(min_length=1)
    scopes: list[str] = Field(default_factory=list)


class GscOAuthCredentialRead(TimestampRead):
    """OAuth credential metadata returned by the API."""

    id: int
    provider: str
    scopes: list[str]
    token_expires_at: datetime | None
    status: GscOAuthStatus
    error_message: str | None
    created_by_id: int | None
    updated_by_id: int | None


class GscOAuthStatusRead(BaseModel):
    """OAuth status summary."""

    configured: bool
    active_credentials_count: int
    latest_credential: GscOAuthCredentialRead | None


class GscPropertyRead(TimestampRead):
    """GSC property returned by the API."""

    id: int
    website_id: int | None
    site_url: str
    property_type: str
    permission_level: str | None
    is_verified: bool
    last_synced_at: datetime | None


class GscImportRunCreate(BaseModel):
    """Payload used to run a mocked GSC import."""

    property_id: int = Field(gt=0)
    date_start: date | None = None
    date_end: date | None = None
    import_type: str = Field(default="full", max_length=40)


class GscImportRunRead(TimestampRead):
    """GSC import run returned by the API."""

    id: int
    property_id: int
    status: GscImportStatus
    import_type: str
    date_start: date | None
    date_end: date | None
    rows_imported: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None


class GscPerformanceRead(TimestampRead):
    """GSC performance row returned by the API."""

    id: int
    property_id: int
    import_run_id: int | None
    date: date
    page: str
    query: str
    device: str
    country: str
    search_type: str
    clicks: int
    impressions: int
    ctr: float
    position: float


class GscCoverageRead(TimestampRead):
    """GSC coverage snapshot returned by the API."""

    id: int
    property_id: int
    import_run_id: int | None
    date: date
    category: str
    state: str
    pages_count: int


class GscIndexingInspectionRead(TimestampRead):
    """GSC indexing inspection returned by the API."""

    id: int
    property_id: int
    import_run_id: int | None
    inspected_url: str
    coverage_state: str | None
    indexing_state: str | None
    verdict: str | None
    robots_txt_state: str | None
    page_fetch_state: str | None
    google_canonical: str | None
    user_canonical: str | None
    last_crawl_time: datetime | None
    inspected_at: datetime


class GscSitemapRead(TimestampRead):
    """GSC sitemap returned by the API."""

    id: int
    property_id: int
    import_run_id: int | None
    sitemap_url: str
    path: str | None
    last_submitted: datetime | None
    last_downloaded: datetime | None
    is_pending: bool
    is_sitemaps_index: bool
    sitemap_type: str | None
    errors: int
    warnings: int
    contents: dict[str, Any] | None


GscPropertyList = PaginatedResponse[GscPropertyRead]
GscImportRunList = PaginatedResponse[GscImportRunRead]
GscPerformanceList = PaginatedResponse[GscPerformanceRead]
GscCoverageList = PaginatedResponse[GscCoverageRead]
GscIndexingInspectionList = PaginatedResponse[GscIndexingInspectionRead]
GscSitemapList = PaginatedResponse[GscSitemapRead]
