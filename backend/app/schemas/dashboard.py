"""Pydantic schemas for the SEO/GEO dashboard."""

from datetime import datetime

from pydantic import BaseModel, Field


class DashboardPageMetric(BaseModel):
    """Page summary used by dashboard cards."""

    crawl_page_id: int | None = None
    url: str | None = None
    score: float | None = None


class DashboardCrawlSummary(BaseModel):
    """Crawl summary displayed in the dashboard."""

    crawled_pages_count: int = 0
    failed_pages_count: int = 0
    latest_crawl_status: str | None = None
    latest_crawl_date: datetime | None = None


class DashboardSeoIssueItem(BaseModel):
    """Aggregated SEO issue displayed in the dashboard."""

    code: str
    severity: str
    family: str
    message: str
    count: int


class DashboardSeoSummary(BaseModel):
    """SEO dashboard summary."""

    average_score: float | None = None
    best_page: DashboardPageMetric | None = None
    worst_page: DashboardPageMetric | None = None
    analyzed_pages_count: int = 0
    critical_errors_count: int = 0
    warnings_count: int = 0
    information_count: int = 0
    top_issues: list[DashboardSeoIssueItem] = Field(default_factory=list)


class DashboardGeoRecommendationItem(BaseModel):
    """GEO recommendation displayed in the dashboard."""

    title: str
    recommendation_type: str
    severity: str
    priority: int
    source: str | None = None
    crawl_page_id: int | None = None
    url: str | None = None


class DashboardGeoSummary(BaseModel):
    """GEO dashboard summary."""

    average_score: float | None = None
    best_page: DashboardPageMetric | None = None
    worst_page: DashboardPageMetric | None = None
    analyses_count: int = 0
    top_recommendations: list[DashboardGeoRecommendationItem] = Field(default_factory=list)


class DashboardScoreDistributionBucket(BaseModel):
    """One score distribution bucket."""

    label: str
    min_score: int
    max_score: int
    count: int = 0


class DashboardPriorityPage(BaseModel):
    """Page requiring prioritized action."""

    crawl_page_id: int | None = None
    url: str | None = None
    seo_score: float | None = None
    geo_score: float | None = None
    critical_issues_count: int = 0
    recommendations_count: int = 0
    priority_score: float
    reason: str


class DashboardComparisonPage(BaseModel):
    """SEO/GEO comparison for one page."""

    crawl_page_id: int | None = None
    url: str | None = None
    seo_score: float | None = None
    geo_score: float | None = None
    gap: float | None = None
    interpretation: str


class DashboardComparisonSummary(BaseModel):
    """SEO/GEO comparison summary."""

    average_seo_score: float | None = None
    average_geo_score: float | None = None
    average_gap: float | None = None
    pages: list[DashboardComparisonPage] = Field(default_factory=list)


class DashboardFutureSourceStatus(BaseModel):
    """Placeholder for future external data sources."""

    available: bool = False
    status: str = "planned"


class DashboardFutureSources(BaseModel):
    """Future extension points for dashboard data."""

    google_search_console: DashboardFutureSourceStatus = Field(default_factory=DashboardFutureSourceStatus)
    google_analytics_4: DashboardFutureSourceStatus = Field(default_factory=DashboardFutureSourceStatus)
    reports: DashboardFutureSourceStatus = Field(default_factory=DashboardFutureSourceStatus)


class DashboardOverview(BaseModel):
    """Complete dashboard overview returned by the API."""

    crawl: DashboardCrawlSummary
    seo: DashboardSeoSummary
    geo: DashboardGeoSummary
    priority_pages: list[DashboardPriorityPage]
    comparison: DashboardComparisonSummary
    seo_score_distribution: list[DashboardScoreDistributionBucket]
    geo_score_distribution: list[DashboardScoreDistributionBucket]
    future_sources: DashboardFutureSources = Field(default_factory=DashboardFutureSources)
