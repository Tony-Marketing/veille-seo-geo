"""Pydantic schemas for Dashboard V2."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from backend.app.schemas.pagination import PaginatedResponse


class DashboardV2Period(StrEnum):
    """Whitelisted dashboard periods."""

    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    CUSTOM = "custom"


class DashboardV2Source(StrEnum):
    """Whitelisted dashboard data sources."""

    SEO = "seo"
    GEO = "geo"
    GSC = "gsc"
    GA4 = "ga4"
    BING = "bing"
    CRAWL = "crawl"
    MONITORING = "monitoring"
    ALERTS = "alerts"
    ORCHESTRATION = "orchestration"


class DashboardV2HealthStatus(StrEnum):
    """Health status buckets."""

    CRITICAL = "critical"
    WARNING = "warning"
    GOOD = "good"
    EXCELLENT = "excellent"
    UNAVAILABLE = "unavailable"


class DashboardV2Granularity(StrEnum):
    """Whitelisted trend granularities."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class DashboardV2TrendMetric(StrEnum):
    """Whitelisted trend metrics."""

    SEO_SCORE = "seo_score"
    GEO_SCORE = "geo_score"
    GSC_CLICKS = "gsc_clicks"
    GSC_IMPRESSIONS = "gsc_impressions"
    GA4_SESSIONS = "ga4_sessions"
    GA4_USERS = "ga4_users"
    BING_CLICKS = "bing_clicks"
    BING_IMPRESSIONS = "bing_impressions"
    ALERTS_ACTIVE = "alerts_active"
    JOBS_FAILED = "jobs_failed"
    JOBS_BLOCKED = "jobs_blocked"


class DashboardV2RecommendationSeverity(StrEnum):
    """Recommendation severities exposed by Dashboard V2."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


DashboardV2Order = Literal["asc", "desc"]


class DashboardV2Filters(BaseModel):
    """Normalized filters used by Dashboard V2 service methods."""

    website_id: int | None = None
    entity_id: int | None = None
    is_active: bool | None = None
    date_from: date | None = None
    date_to: date | None = None
    period: DashboardV2Period = DashboardV2Period.LAST_30_DAYS
    compare_to_previous: bool = True
    source: list[DashboardV2Source] = Field(default_factory=list)
    health_status: DashboardV2HealthStatus | None = None
    search: str | None = None
    sort: str | None = None
    order: DashboardV2Order = "asc"


class DashboardV2ResolvedPeriod(BaseModel):
    """Concrete date interval used for dashboard aggregation."""

    date_from: date
    date_to: date
    period: DashboardV2Period


class DashboardV2MetricDelta(BaseModel):
    """Current value with optional previous period comparison."""

    value: float | int | None = None
    previous_value: float | int | None = None
    delta_percent: float | None = None


class DashboardV2SourceAvailability(BaseModel):
    """Availability state for one source."""

    source: DashboardV2Source
    available: bool = False
    status: str = "unavailable"


class DashboardV2HealthComponent(BaseModel):
    """One component used by the global health score."""

    name: str
    score: float | None = None
    status: DashboardV2HealthStatus = DashboardV2HealthStatus.UNAVAILABLE
    available: bool = False


class DashboardV2HealthScore(BaseModel):
    """Global health score and component breakdown."""

    score: float | None = None
    status: DashboardV2HealthStatus = DashboardV2HealthStatus.UNAVAILABLE
    components: list[DashboardV2HealthComponent] = Field(default_factory=list)
    available_components: list[str] = Field(default_factory=list)
    missing_components: list[str] = Field(default_factory=list)


class DashboardV2SeoKpis(BaseModel):
    """SEO KPIs available to the dashboard."""

    analyses_count: int = 0
    completed_analyses: int = 0
    failed_analyses: int = 0
    average_score: float | None = None
    global_score: float | None = None
    pages_total: int = 0
    pages_analyzed: int = 0
    coverage_rate: float | None = None
    issues_total: int = 0
    critical_issues: int = 0
    warning_issues: int = 0
    latest_analysis_at: datetime | None = None


class DashboardV2GeoKpis(BaseModel):
    """GEO KPIs available to the dashboard."""

    analyses_count: int = 0
    completed_analyses: int = 0
    partial_analyses: int = 0
    failed_analyses: int = 0
    geo_score: float | None = None
    llm_score: float | None = None
    global_score: float | None = None
    pages_total: int = 0
    pages_analyzed: int = 0
    coverage_rate: float | None = None
    provider_results_count: int = 0
    provider_failed_count: int = 0
    recommendations_count: int = 0
    priority_recommendations: int = 0
    latest_analysis_at: datetime | None = None


class DashboardV2GscKpis(BaseModel):
    """Google Search Console KPIs."""

    properties_count: int = 0
    active_properties: int = 0
    clicks: int = 0
    impressions: int = 0
    ctr: float | None = None
    position: float | None = None
    valid_pages: int = 0
    excluded_pages: int = 0
    index_errors: int = 0
    index_warnings: int = 0
    sitemap_errors: int = 0
    sitemap_warnings: int = 0
    failed_imports: int = 0
    latest_import_at: datetime | None = None


class DashboardV2Ga4Kpis(BaseModel):
    """Google Analytics 4 KPIs."""

    properties_count: int = 0
    active_properties: int = 0
    sessions: int = 0
    users: int = 0
    new_users: int = 0
    engaged_sessions: int = 0
    screen_page_views: int = 0
    average_session_duration: float | None = None
    engagement_rate: float | None = None
    conversions: float = 0.0
    total_revenue: float = 0.0
    failed_imports: int = 0
    latest_import_at: datetime | None = None


class DashboardV2BingKpis(BaseModel):
    """Bing Webmaster Tools KPIs."""

    connections_count: int = 0
    active_connections: int = 0
    sites_count: int = 0
    verified_sites: int = 0
    clicks: int = 0
    impressions: int = 0
    ctr: float | None = None
    position: float | None = None
    crawl_errors: int = 0
    sitemap_errors: int = 0
    sitemap_warnings: int = 0
    failed_imports: int = 0
    latest_import_at: datetime | None = None


class DashboardV2MonitoringKpis(BaseModel):
    """Monitoring counters."""

    total_events: int = 0
    period_events: int = 0
    warning_events: int = 0
    error_events: int = 0
    critical_events: int = 0
    by_source: dict[str, int] = Field(default_factory=dict)
    by_type: dict[str, int] = Field(default_factory=dict)
    last_event_at: datetime | None = None


class DashboardV2AlertKpis(BaseModel):
    """Alert counters."""

    total: int = 0
    active: int = 0
    acknowledged: int = 0
    resolved: int = 0
    info: int = 0
    warning: int = 0
    critical: int = 0
    last_alert_at: datetime | None = None


class DashboardV2WorkerKpis(BaseModel):
    """Worker counters."""

    total_workers: int = 0
    active_workers: int = 0
    stopped_workers: int = 0
    status: str = "not_configured"
    last_heartbeat_at: datetime | None = None


class DashboardV2OperationsKpis(BaseModel):
    """Processing and operations counters."""

    pending_jobs: int = 0
    reserved_jobs: int = 0
    running_jobs: int = 0
    retry_scheduled_jobs: int = 0
    succeeded_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0
    blocked_jobs: int = 0
    total_jobs: int = 0
    last_activity_at: datetime | None = None
    workers: DashboardV2WorkerKpis = Field(default_factory=DashboardV2WorkerKpis)


class DashboardV2TrendPoint(BaseModel):
    """One trend point."""

    date: date
    value: float | int
    previous_value: float | int | None = None
    delta_percent: float | None = None


class DashboardV2TrendSeries(BaseModel):
    """One trend series."""

    metric: DashboardV2TrendMetric
    label: str
    source: DashboardV2Source
    points: list[DashboardV2TrendPoint] = Field(default_factory=list)


class DashboardV2WebsiteSummary(BaseModel):
    """Dashboard summary for one website."""

    website_id: int
    name: str
    url: str
    is_active: bool
    health_score: float | None = None
    health_status: DashboardV2HealthStatus = DashboardV2HealthStatus.UNAVAILABLE
    seo_score: float | None = None
    geo_score: float | None = None
    gsc_clicks: int = 0
    gsc_impressions: int = 0
    ga4_sessions: int = 0
    bing_clicks: int = 0
    bing_impressions: int = 0
    active_alerts: int = 0
    failed_or_blocked_jobs: int = 0
    last_activity_at: datetime | None = None
    available_sources: list[str] = Field(default_factory=list)
    missing_sources: list[str] = Field(default_factory=list)


class DashboardV2WebsiteList(PaginatedResponse[DashboardV2WebsiteSummary]):
    """Paginated website dashboard response."""

    filters: dict[str, Any] = Field(default_factory=dict)


class DashboardV2Recommendation(BaseModel):
    """One deterministic dashboard recommendation."""

    type: str
    severity: DashboardV2RecommendationSeverity
    priority: int = Field(ge=1, le=5)
    title: str
    message: str
    source: DashboardV2Source
    website_id: int | None = None
    source_id: str | None = None
    navigation_target: str
    created_at: datetime | None = None
    website_name: str | None = None


class DashboardV2RecommendationList(PaginatedResponse[DashboardV2Recommendation]):
    """Paginated recommendation response."""

    filters: dict[str, Any] = Field(default_factory=dict)


class DashboardV2OverviewResponse(BaseModel):
    """Complete Dashboard V2 overview response."""

    generated_at: datetime
    filters: dict[str, Any] = Field(default_factory=dict)
    period: DashboardV2ResolvedPeriod
    previous_period: DashboardV2ResolvedPeriod | None = None
    sources: list[DashboardV2SourceAvailability] = Field(default_factory=list)
    global_health: DashboardV2HealthScore
    seo: DashboardV2SeoKpis
    geo: DashboardV2GeoKpis
    gsc: DashboardV2GscKpis
    ga4: DashboardV2Ga4Kpis
    bing: DashboardV2BingKpis
    technical: DashboardV2HealthComponent
    operations: DashboardV2OperationsKpis
    monitoring: DashboardV2MonitoringKpis
    alerts: DashboardV2AlertKpis
    workers: DashboardV2WorkerKpis
    top_websites: list[DashboardV2WebsiteSummary] = Field(default_factory=list)
    top_recommendations: list[DashboardV2Recommendation] = Field(default_factory=list)
    partial_data: list[str] = Field(default_factory=list)


class DashboardV2TrendsResponse(BaseModel):
    """Dashboard V2 trend response."""

    generated_at: datetime
    filters: dict[str, Any] = Field(default_factory=dict)
    granularity: DashboardV2Granularity
    series: list[DashboardV2TrendSeries] = Field(default_factory=list)
