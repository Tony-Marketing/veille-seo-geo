"""Pydantic schemas for crawl sessions and pages."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class CrawlSessionStatus(StrEnum):
    """Known lifecycle states for a crawl session."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CrawlCreate(BaseModel):
    """Payload used to create a crawl session."""

    website_id: int | None = None
    start_url: str | None = Field(default=None, min_length=8, max_length=500)
    max_depth: int = Field(default=2, ge=0, le=10)
    max_pages: int = Field(default=100, ge=1, le=1000)

    @model_validator(mode="after")
    def require_website_or_start_url(self) -> "CrawlCreate":
        """Require enough information to determine the crawl start URL."""

        if self.website_id is None and not self.start_url:
            raise ValueError("website_id ou start_url est requis.")
        return self


class CrawlStart(BaseModel):
    """Optional launch overrides."""

    max_depth: int | None = Field(default=None, ge=0, le=10)
    max_pages: int | None = Field(default=None, ge=1, le=1000)


class CrawlRead(TimestampRead):
    """Crawl session returned by the API."""

    id: int
    website_id: int | None
    start_url: str
    normalized_start_url: str
    status: CrawlSessionStatus
    max_depth: int
    max_pages: int
    pages_found: int
    pages_crawled: int
    pages_failed: int
    pending_urls: int
    max_depth_reached: int
    cancel_requested: bool
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    last_progress_at: datetime | None


class CrawlPageRead(TimestampRead):
    """Page discovered during a crawl session."""

    id: int
    crawl_session_id: int
    website_id: int | None
    url: str
    normalized_url: str
    final_url: str | None
    final_normalized_url: str | None
    depth: int
    status_code: int | None
    content_type: str | None
    is_redirect: bool
    redirect_url: str | None
    redirect_count: int
    response_time_ms: int | None
    error_message: str | None
    discovered_at: datetime
    visited_at: datetime | None


CrawlList = PaginatedResponse[CrawlRead]
CrawlPageList = PaginatedResponse[CrawlPageRead]

