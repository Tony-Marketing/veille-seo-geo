"""Pydantic schemas for the transverse recommendations engine."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class RecommendationSource(StrEnum):
    """Canonical persisted sources supported by the engine."""

    SEO = "SEO"
    GEO = "GEO"
    MONITORING = "MONITORING"
    ALERTS = "ALERTS"
    GSC = "GSC"
    GA4 = "GA4"
    BING = "BING"


class RecommendationPriority(StrEnum):
    """Deterministic recommendation priority levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecommendationImpact(StrEnum):
    """Primary business or technical impact."""

    SEO = "SEO"
    GEO = "GEO"
    TECHNIQUE = "TECHNIQUE"
    PERFORMANCE = "PERFORMANCE"
    BUSINESS = "BUSINESS"


class RecommendationDifficulty(StrEnum):
    """Optional estimated implementation difficulty."""

    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class RecommendationStatus(StrEnum):
    """Recommendation lifecycle states."""

    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class RecommendationFilters(BaseModel):
    """REST and service filters supported by recommendation listings."""

    website_id: int | None = Field(default=None, gt=0)
    source: RecommendationSource | None = None
    category: str | None = Field(default=None, max_length=80)
    priority: RecommendationPriority | None = None
    status: RecommendationStatus | None = None
    search: str | None = Field(default=None, max_length=255)


class RecommendationRead(TimestampRead):
    """Persisted recommendation returned by the REST API."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    website_id: int | None = None
    website_name: str | None = None
    source: RecommendationSource
    source_id: str
    category: str
    title: str
    description: str
    priority: RecommendationPriority
    impact: RecommendationImpact
    difficulty: RecommendationDifficulty | None = None
    score: float
    status: RecommendationStatus
    deduplication_key: str
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="metadata_")


class RecommendationList(PaginatedResponse[RecommendationRead]):
    """Paginated recommendations with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)


class RecommendationSummary(BaseModel):
    """Recommendation counters reusable by Dashboard V2 and Desktop."""

    total: int = 0
    open: int = 0
    acknowledged: int = 0
    resolved: int = 0
    ignored: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    by_priority: dict[str, int] = Field(default_factory=dict)
    by_category: dict[str, int] = Field(default_factory=dict)
    recent: list[RecommendationRead] = Field(default_factory=list)
    generated_at: datetime


class RecommendationStatusUpdate(BaseModel):
    """Payload used to transition one recommendation."""

    status: RecommendationStatus
