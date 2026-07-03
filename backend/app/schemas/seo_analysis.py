"""Pydantic schemas for SEO analysis."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class SeoAnalysisStatus(StrEnum):
    """Known lifecycle states for a SEO analysis."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SeoAnalysisCreate(BaseModel):
    """Payload used to create a SEO analysis."""

    crawl_id: int = Field(gt=0)


class SeoAnalysisUpdate(BaseModel):
    """Payload used to update SEO analysis execution state."""

    status: SeoAnalysisStatus | None = None
    progress_percent: int | None = Field(default=None, ge=0, le=100)
    error_message: str | None = None


class SeoAnalysisRead(TimestampRead):
    """SEO analysis returned by the API."""

    id: int
    crawl_session_id: int
    status: SeoAnalysisStatus
    progress_percent: int
    global_score: float | None
    pages_total: int
    pages_analyzed: int
    issues_total: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None


class SeoPageAnalysisRead(TimestampRead):
    """SEO page analysis returned by the API."""

    id: int
    seo_analysis_id: int
    crawl_page_id: int
    status: SeoAnalysisStatus
    score: float | None
    issues_count: int
    error_message: str | None
    analyzed_at: datetime | None


class SeoAnalysisIssueRead(TimestampRead):
    """SEO issue returned by the API."""

    id: int
    seo_analysis_id: int
    seo_page_analysis_id: int | None
    crawl_page_id: int | None
    family: str
    criterion: str
    severity: str
    code: str
    message: str
    details: str | None


SeoAnalysisList = PaginatedResponse[SeoAnalysisRead]

