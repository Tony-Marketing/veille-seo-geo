"""Pydantic schemas for GEO analysis."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class GeoAnalysisStatus(StrEnum):
    """Known lifecycle states for a GEO analysis."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class GeoProviderStatus(StrEnum):
    """Known lifecycle states for one GEO provider result."""

    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


class GeoAnalysisCreate(BaseModel):
    """Payload used to create a GEO analysis."""

    seo_analysis_id: int = Field(gt=0)
    providers: list[str] = Field(default_factory=lambda: ["openai"], min_length=1)


class GeoProviderResultRead(TimestampRead):
    """Provider result returned by the API."""

    id: int
    geo_analysis_id: int
    crawl_page_id: int | None
    provider_name: str
    model_name: str | None
    status: str
    prompt: str | None
    raw_response: str | None
    normalized_response: dict[str, Any] | None
    error_message: str | None
    duration_ms: int | None


class GeoRecommendationRead(TimestampRead):
    """GEO recommendation returned by the API."""

    id: int
    geo_analysis_id: int
    provider_result_id: int | None
    crawl_page_id: int | None
    recommendation_type: str
    severity: str
    priority: int
    title: str
    description: str
    source: str | None
    impact_score: float | None


class GeoAnalysisRead(TimestampRead):
    """GEO analysis returned by the API."""

    id: int
    seo_analysis_id: int
    crawl_session_id: int
    status: GeoAnalysisStatus
    progress_percent: int
    geo_score: float | None
    llm_score: float | None
    global_score: float | None
    providers_requested: list[str]
    pages_total: int
    pages_analyzed: int
    provider_results_count: int
    recommendations_count: int
    summary: str | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    provider_results: list[GeoProviderResultRead] = Field(default_factory=list)
    recommendations: list[GeoRecommendationRead] = Field(default_factory=list)


GeoAnalysisList = PaginatedResponse[GeoAnalysisRead]
