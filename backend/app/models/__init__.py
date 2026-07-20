"""SQLAlchemy models."""

from backend.app.models.admin import (
    AiModel,
    AiProvider,
    ApiKey,
    ApplicationSetting,
    AuditLog,
    ErrorLog,
    SystemParameter,
)
from backend.app.models.alert import Alert
from backend.app.models.auth import Permission, Role, User, role_permissions, user_roles
from backend.app.models.bing_webmaster_tools import (
    BingWebmasterConnection,
    BingWebmasterCrawlStat,
    BingWebmasterImportRun,
    BingWebmasterMetric,
    BingWebmasterSite,
    BingWebmasterSitemap,
)
from backend.app.models.crawls import CrawlPage, CrawlSession
from backend.app.models.entities import Competitor, Entity, Keyword, ProjectTask, Report, Url, Website
from backend.app.models.geo_analysis import GeoAnalysis, GeoProviderResult, GeoRecommendation
from backend.app.models.google_analytics import (
    GoogleAnalyticsDimension,
    GoogleAnalyticsImport,
    GoogleAnalyticsMetric,
    GoogleAnalyticsProperty,
)
from backend.app.models.google_search_console import (
    GoogleSearchConsoleImport,
    GoogleSearchConsoleIndexCoverage,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleProperty,
    GoogleSearchConsoleSitemap,
)
from backend.app.models.monitoring_event import MonitoringEvent
from backend.app.models.processing_job import ProcessingJob
from backend.app.models.processing_job_log import ProcessingJobLog
from backend.app.models.processing_worker import ProcessingWorker
from backend.app.models.recommendation import Recommendation
from backend.app.models.seo_analysis import SeoAnalysis, SeoAnalysisIssue, SeoPageAnalysis
from backend.app.models.sync_schedule import SyncSchedule
from backend.app.models.user_invitation import UserInvitation

__all__ = [
    "AiModel",
    "AiProvider",
    "ApiKey",
    "ApplicationSetting",
    "Alert",
    "AuditLog",
    "BingWebmasterConnection",
    "BingWebmasterCrawlStat",
    "BingWebmasterImportRun",
    "BingWebmasterMetric",
    "BingWebmasterSite",
    "BingWebmasterSitemap",
    "Competitor",
    "CrawlPage",
    "CrawlSession",
    "Entity",
    "ErrorLog",
    "GeoAnalysis",
    "GeoProviderResult",
    "GeoRecommendation",
    "GoogleAnalyticsDimension",
    "GoogleAnalyticsImport",
    "GoogleAnalyticsMetric",
    "GoogleAnalyticsProperty",
    "GoogleSearchConsoleImport",
    "GoogleSearchConsoleIndexCoverage",
    "GoogleSearchConsolePerformance",
    "GoogleSearchConsoleProperty",
    "GoogleSearchConsoleSitemap",
    "Keyword",
    "MonitoringEvent",
    "Permission",
    "ProcessingJob",
    "ProcessingJobLog",
    "ProcessingWorker",
    "ProjectTask",
    "Recommendation",
    "Report",
    "Role",
    "SeoAnalysis",
    "SeoAnalysisIssue",
    "SeoPageAnalysis",
    "SyncSchedule",
    "SystemParameter",
    "Url",
    "User",
    "UserInvitation",
    "Website",
    "role_permissions",
    "user_roles",
]
