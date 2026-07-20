"""Pydantic v2 schemas for GEO Intelligence."""

import re
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse

PROVIDER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
INITIAL_GEO_PROVIDERS = ("chatgpt", "gemini", "claude", "copilot", "perplexity")


def normalize_provider(value: str) -> str:
    """Return one extensible normalized provider identifier."""

    normalized = value.strip().lower().replace(" ", "-")
    if not PROVIDER_PATTERN.fullmatch(normalized):
        raise ValueError("Le fournisseur doit etre un identifiant alphanumerique normalise.")
    return normalized


class GeoVisibilityFilters(BaseModel):
    """Filters shared by GEO Intelligence list and aggregation contracts."""

    website_id: int | None = Field(default=None, gt=0)
    provider: str | None = Field(default=None, max_length=80)
    entity: str | None = Field(default=None, max_length=255)
    prompt: str | None = Field(default=None, max_length=500)
    date_from: datetime | None = None
    date_to: datetime | None = None
    search: str | None = Field(default=None, max_length=255)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str | None) -> str | None:
        """Normalize optional provider filters."""

        return normalize_provider(value) if value else None


class GeoVisibilityImportItem(BaseModel):
    """One already-normalized GEO observation accepted by the import API."""

    website_id: int = Field(gt=0)
    provider: str = Field(min_length=1, max_length=80)
    prompt: str = Field(min_length=1, max_length=500)
    entity: str = Field(min_length=1, max_length=255)
    visibility_score: float = Field(ge=0, le=100)
    citation_count: int = Field(default=0, ge=0)
    source_count: int = Field(default=0, ge=0)
    ranking: int | None = Field(default=None, gt=0)
    answer_hash: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-fA-F]{64}$")
    captured_at: datetime

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        """Normalize the imported provider without using a closed enumeration."""

        return normalize_provider(value)

    @field_validator("prompt", "entity")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Reject blank normalized dimensions."""

        stripped = value.strip()
        if not stripped:
            raise ValueError("La valeur ne peut pas etre vide.")
        return stripped

    @field_validator("answer_hash")
    @classmethod
    def normalize_hash(cls, value: str) -> str:
        """Normalize the SHA-256 hexadecimal representation."""

        return value.lower()


class GeoVisibilityImportRequest(BaseModel):
    """Non-destructive batch import request."""

    observations: list[GeoVisibilityImportItem] = Field(min_length=1, max_length=1000)


class GeoVisibilitySnapshotRead(TimestampRead):
    """Persisted GEO visibility snapshot returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    website_id: int
    website_name: str | None = None
    provider: str
    prompt: str
    entity: str
    visibility_score: float
    citation_count: int
    source_count: int
    ranking: int | None = None
    answer_hash: str
    captured_at: datetime


class GeoVisibilitySnapshotList(PaginatedResponse[GeoVisibilitySnapshotRead]):
    """Paginated snapshots with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)


class GeoVisibilityImportResult(BaseModel):
    """Explicit idempotent import counters."""

    received: int
    created: int
    duplicates: int
    rejected: int = 0
    items: list[GeoVisibilitySnapshotRead] = Field(default_factory=list)


class GeoProviderSummary(BaseModel):
    """One provider comparison row."""

    provider: str
    captures: int = 0
    average_visibility_score: float | None = None
    citation_count: int = 0
    source_count: int = 0
    appearance_frequency: float | None = None
    latest_capture_at: datetime | None = None


class GeoVisibilitySummary(BaseModel):
    """Consolidated and explainable GEO Intelligence KPIs."""

    captures: int = 0
    average_visibility_score: float | None = None
    providers_covered: list[str] = Field(default_factory=list)
    citation_count: int = 0
    source_count: int = 0
    appearance_frequency: float | None = None
    latest_capture_at: datetime | None = None
    by_provider: list[GeoProviderSummary] = Field(default_factory=list)
    generated_at: datetime


class GeoVisibilityHistoryPoint(BaseModel):
    """Daily comparable GEO Intelligence aggregation."""

    date: date
    provider: str
    captures: int
    average_visibility_score: float
    citation_count: int
    source_count: int
    appearance_frequency: float


class GeoVisibilityHistory(BaseModel):
    """Historical series grouped by provider and capture day."""

    points: list[GeoVisibilityHistoryPoint] = Field(default_factory=list)
    generated_at: datetime


class GeoProviderRead(BaseModel):
    """Provider exposed by the injectable connector registry."""

    provider: str
    configured: bool


class GeoProviderList(BaseModel):
    """Open list of known GEO Intelligence providers."""

    providers: list[GeoProviderRead] = Field(default_factory=list)


class GeoRecommendationSignal(BaseModel):
    """Domain signal consumed by the transverse Recommendation Engine."""

    website_id: int
    provider: str
    prompt: str
    entity: str
    rule_code: str
    source_object_id: str
    title: str
    description: str
    factors: dict[str, Any] = Field(default_factory=dict)
