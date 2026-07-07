"""Pydantic schemas for Google Analytics 4."""

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class GoogleAnalyticsImportStatus(StrEnum):
    """Known Google Analytics import statuses."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class GoogleAnalyticsPropertyCreate(BaseModel):
    """Payload used to create a Google Analytics property."""

    website_id: int | None = Field(default=None, gt=0)
    property_id: str = Field(min_length=1, max_length=100)
    property_name: str = Field(min_length=1, max_length=255)
    account_name: str | None = Field(default=None, max_length=255)
    measurement_id: str | None = Field(default=None, max_length=80)
    enabled: bool = True


class GoogleAnalyticsPropertyUpdate(BaseModel):
    """Payload used to update a Google Analytics property."""

    website_id: int | None = Field(default=None, gt=0)
    property_id: str | None = Field(default=None, min_length=1, max_length=100)
    property_name: str | None = Field(default=None, min_length=1, max_length=255)
    account_name: str | None = Field(default=None, max_length=255)
    measurement_id: str | None = Field(default=None, max_length=80)
    enabled: bool | None = None


class GoogleAnalyticsPropertyRead(TimestampRead):
    """Google Analytics property returned by the API."""

    id: int
    website_id: int | None
    property_id: str
    property_name: str
    account_name: str | None
    measurement_id: str | None
    token_expires_at: datetime | None
    enabled: bool


class GoogleAnalyticsMetricRead(TimestampRead):
    """Google Analytics metrics returned by the API."""

    id: int
    property_id: int
    import_id: int | None
    date: date
    source: str | None
    medium: str | None
    campaign: str | None
    device_category: str | None
    country: str | None
    users: int
    new_users: int
    sessions: int
    engaged_sessions: int
    screen_page_views: int
    average_session_duration: float
    engagement_rate: float
    conversions: float
    total_revenue: float


class GoogleAnalyticsImportRequest(BaseModel):
    """Payload used to launch a manual Google Analytics import."""

    property_id: int = Field(gt=0)
    start_date: date
    end_date: date
    metrics: list[str] = Field(
        default_factory=lambda: [
            "users",
            "newUsers",
            "sessions",
            "engagedSessions",
            "screenPageViews",
            "averageSessionDuration",
            "engagementRate",
            "conversions",
            "totalRevenue",
        ],
    )
    dimensions: list[str] = Field(
        default_factory=lambda: ["date", "source", "medium", "campaign", "deviceCategory", "country"],
    )


class GoogleAnalyticsImportRead(TimestampRead):
    """Import execution log returned by the API."""

    id: int
    property_id: int
    started_at: datetime | None
    finished_at: datetime | None
    status: GoogleAnalyticsImportStatus
    imported_rows: int
    error_message: str | None
    duration_seconds: float | None = None


class GoogleAnalyticsOAuthConnectRequest(BaseModel):
    """Payload used to prepare a Google Analytics OAuth connection."""

    property_id: int = Field(gt=0)
    access_token: str = Field(min_length=1)
    refresh_token: str | None = Field(default=None, min_length=1)
    token_scopes: list[str] = Field(default_factory=list)
    token_expires_at: datetime | None = None


class GoogleAnalyticsOAuthRefreshRequest(BaseModel):
    """Payload used to refresh a Google Analytics OAuth token."""

    property_id: int = Field(gt=0)


class GoogleAnalyticsOAuthResponse(BaseModel):
    """OAuth operation response without exposing tokens."""

    property_id: int
    token_scopes: list[str] = Field(default_factory=list)
    token_expires_at: datetime | None = None
    status: str = "OK"


GoogleAnalyticsPropertyList = PaginatedResponse[GoogleAnalyticsPropertyRead]
GoogleAnalyticsImportList = PaginatedResponse[GoogleAnalyticsImportRead]
