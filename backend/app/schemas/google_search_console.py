"""Pydantic schemas for Google Search Console backend."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class GoogleSearchConsoleImportType(StrEnum):
    """Import families supported by the Google Search Console backend."""

    PROPERTIES = "properties"
    PERFORMANCE = "performance"
    INDEX_COVERAGE = "index_coverage"
    SITEMAPS = "sitemaps"
    FULL = "full"


class GoogleSearchConsoleImportStatus(StrEnum):
    """Known lifecycle states for one import."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class GoogleSearchConsolePropertyCreate(BaseModel):
    """Payload used to create a Google Search Console property manually."""

    site_url: str = Field(min_length=1, max_length=500)
    website_id: int | None = None
    property_type: str = Field(default="URL_PREFIX", max_length=40)
    permission_level: str | None = Field(default=None, max_length=80)
    status: str = Field(default="ACTIVE", max_length=30)


class GoogleSearchConsolePropertyUpdate(BaseModel):
    """Payload used to update a Google Search Console property."""

    website_id: int | None = None
    property_type: str | None = Field(default=None, max_length=40)
    permission_level: str | None = Field(default=None, max_length=80)
    status: str | None = Field(default=None, max_length=30)
    last_synced_at: datetime | None = None


class GoogleSearchConsolePropertyRead(TimestampRead):
    """Google Search Console property returned by the API."""

    id: int
    website_id: int | None
    site_url: str
    property_type: str
    permission_level: str | None
    status: str
    last_synced_at: datetime | None


class GoogleSearchConsolePerformanceRead(TimestampRead):
    """Google Search Console performance row returned by the API."""

    id: int
    property_id: int
    date: date
    page: str | None
    query: str | None
    country: str | None
    device: str | None
    clicks: int
    impressions: int
    ctr: float
    position: float


class GoogleSearchConsoleIndexCoverageRead(TimestampRead):
    """Google Search Console index coverage row returned by the API."""

    id: int
    property_id: int
    url: str
    coverage_state: str
    indexing_state: str | None
    verdict: str | None
    page_fetch_state: str | None
    google_canonical: str | None
    user_canonical: str | None
    last_crawl_time: datetime | None
    inspected_at: datetime | None


class GoogleSearchConsoleSitemapRead(TimestampRead):
    """Google Search Console sitemap returned by the API."""

    id: int
    property_id: int
    sitemap_url: str
    status: str | None
    last_submitted_at: datetime | None
    last_downloaded_at: datetime | None
    warnings: int
    errors: int
    contents: dict[str, Any] | None


class GoogleSearchConsoleImportRead(TimestampRead):
    """Google Search Console import history item returned by the API."""

    id: int
    property_id: int | None
    import_type: str
    status: GoogleSearchConsoleImportStatus
    started_at: datetime | None
    finished_at: datetime | None
    items_processed: int
    items_created: int
    items_updated: int
    items_skipped: int
    error_message: str | None
    import_metadata: dict[str, Any] | None


class GoogleSearchConsoleImportRequest(BaseModel):
    """Payload used to launch a manual Google Search Console import."""

    import_type: GoogleSearchConsoleImportType = GoogleSearchConsoleImportType.FULL
    property_id: int | None = Field(default=None, gt=0)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_import_scope(self) -> "GoogleSearchConsoleImportRequest":
        """Ensure property-scoped imports identify one property."""

        if self.import_type != GoogleSearchConsoleImportType.PROPERTIES and self.property_id is None:
            raise ValueError("property_id est requis pour cet import.")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date doit etre inferieure ou egale a end_date.")
        return self


class GoogleSearchConsolePerformanceFilters(BaseModel):
    """Filters accepted for performance listing."""

    property_id: int = Field(gt=0)
    start_date: date | None = None
    end_date: date | None = None
    page: str | None = None
    query: str | None = None
    country: str | None = None
    device: str | None = None


class GoogleSearchConsoleIndexCoverageFilters(BaseModel):
    """Filters accepted for index coverage listing."""

    property_id: int = Field(gt=0)
    coverage_state: str | None = None
    verdict: str | None = None


class GoogleSearchConsoleSitemapFilters(BaseModel):
    """Filters accepted for sitemap listing."""

    property_id: int = Field(gt=0)
    status: str | None = None


class GoogleSearchConsoleImportFilters(BaseModel):
    """Filters accepted for import history listing."""

    property_id: int | None = Field(default=None, gt=0)
    import_type: Literal["properties", "performance", "index_coverage", "sitemaps", "full"] | None = None
    status: str | None = None


GoogleSearchConsolePropertyList = PaginatedResponse[GoogleSearchConsolePropertyRead]
GoogleSearchConsolePerformanceList = PaginatedResponse[GoogleSearchConsolePerformanceRead]
GoogleSearchConsoleIndexCoverageList = PaginatedResponse[GoogleSearchConsoleIndexCoverageRead]
GoogleSearchConsoleSitemapList = PaginatedResponse[GoogleSearchConsoleSitemapRead]
GoogleSearchConsoleImportList = PaginatedResponse[GoogleSearchConsoleImportRead]
