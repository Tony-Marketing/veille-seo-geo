"""Read-only repository for Dashboard V2 aggregation."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from backend.app.models import (
    Alert,
    BingWebmasterConnection,
    BingWebmasterCrawlStat,
    BingWebmasterImportRun,
    BingWebmasterMetric,
    BingWebmasterSite,
    BingWebmasterSitemap,
    CrawlPage,
    CrawlSession,
    GeoAnalysis,
    GeoProviderResult,
    GeoRecommendation,
    GoogleAnalyticsImport,
    GoogleAnalyticsMetric,
    GoogleAnalyticsProperty,
    GoogleSearchConsoleImport,
    GoogleSearchConsoleIndexCoverage,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleProperty,
    GoogleSearchConsoleSitemap,
    MonitoringEvent,
    ProcessingJob,
    ProcessingWorker,
    SeoAnalysis,
    SeoAnalysisIssue,
    SeoPageAnalysis,
    Website,
)
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class DashboardV2Repository(BaseRepository[Website]):
    """Read and aggregate existing persisted data for Dashboard V2."""

    website_sort_fields = ("id", "name", "url", "is_active", "created_at", "updated_at")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Website)

    def list_websites(
        self,
        params: PaginationParams,
        *,
        website_id: int | None = None,
        entity_id: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Website], int]:
        """Return filtered websites with repository-level whitelisted sort."""

        statement = select(Website)
        count_statement = select(func.count()).select_from(Website)
        filters = self._website_filters(
            website_id=website_id,
            entity_id=entity_id,
            is_active=is_active,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        if params.sort:
            if params.sort not in self.website_sort_fields or not hasattr(Website, params.sort):
                raise ValueError(f"Champ de tri Dashboard V2 non autorise: {params.sort}.")
            sort_column = getattr(Website, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(Website.name.asc(), Website.id.asc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_all_websites(
        self,
        *,
        website_id: int | None = None,
        entity_id: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> list[Website]:
        """Return filtered websites without pagination for overview aggregates."""

        statement = select(Website)
        filters = self._website_filters(website_id=website_id, entity_id=entity_id, is_active=is_active, search=search)
        if filters:
            statement = statement.where(*filters)
        statement = statement.order_by(Website.name.asc(), Website.id.asc())
        return list(self.db.scalars(statement))

    def crawl_aggregates(self, website_ids: list[int], *, start: datetime, end: datetime) -> dict[int, dict[str, Any]]:
        """Return crawl aggregates by website."""

        if not website_ids:
            return {}
        session_statement = (
            select(
                CrawlSession.website_id,
                func.count(CrawlSession.id),
                func.coalesce(func.sum(CrawlSession.pages_crawled), 0),
                func.coalesce(func.sum(CrawlSession.pages_failed), 0),
                func.max(func.coalesce(CrawlSession.finished_at, CrawlSession.started_at, CrawlSession.created_at)),
            )
            .where(
                CrawlSession.website_id.in_(website_ids),
                CrawlSession.created_at >= start,
                CrawlSession.created_at <= end,
            )
            .group_by(CrawlSession.website_id)
        )
        page_statement = (
            select(
                CrawlPage.website_id,
                func.count(CrawlPage.id),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                or_(
                                    CrawlPage.error_message.is_not(None),
                                    CrawlPage.status_code >= 400,
                                ),
                                1,
                            ),
                            else_=0,
                        ),
                    ),
                    0,
                ),
            )
            .where(
                CrawlPage.website_id.in_(website_ids),
                CrawlPage.created_at >= start,
                CrawlPage.created_at <= end,
            )
            .group_by(CrawlPage.website_id)
        )
        results: dict[int, dict[str, Any]] = {}
        for website_id, sessions, pages_crawled, pages_failed, latest_at in self.db.execute(session_statement):
            results[int(website_id)] = {
                "sessions": int(sessions or 0),
                "pages_crawled": int(pages_crawled or 0),
                "pages_failed": int(pages_failed or 0),
                "latest_at": latest_at,
                "crawl_pages": 0,
                "http_error_pages": 0,
            }
        for website_id, pages, error_pages in self.db.execute(page_statement):
            item = results.setdefault(
                int(website_id),
                {
                    "sessions": 0,
                    "pages_crawled": 0,
                    "pages_failed": 0,
                    "latest_at": None,
                    "crawl_pages": 0,
                    "http_error_pages": 0,
                },
            )
            item["crawl_pages"] = int(pages or 0)
            item["http_error_pages"] = int(error_pages or 0)
        return results

    def seo_aggregates(self, website_ids: list[int], *, start: datetime, end: datetime) -> dict[int, dict[str, Any]]:
        """Return SEO analysis aggregates by website."""

        if not website_ids:
            return {}
        statement = (
            select(
                CrawlSession.website_id,
                func.count(SeoAnalysis.id),
                self._status_count(SeoAnalysis.status, "COMPLETED"),
                self._status_count(SeoAnalysis.status, "FAILED"),
                func.avg(SeoAnalysis.global_score),
                func.coalesce(func.sum(SeoAnalysis.pages_total), 0),
                func.coalesce(func.sum(SeoAnalysis.pages_analyzed), 0),
                func.coalesce(func.sum(SeoAnalysis.issues_total), 0),
                func.max(func.coalesce(SeoAnalysis.completed_at, SeoAnalysis.started_at, SeoAnalysis.created_at)),
            )
            .join(CrawlSession, CrawlSession.id == SeoAnalysis.crawl_session_id)
            .where(
                CrawlSession.website_id.in_(website_ids),
                SeoAnalysis.created_at >= start,
                SeoAnalysis.created_at <= end,
            )
            .group_by(CrawlSession.website_id)
        )
        page_statement = (
            select(CrawlSession.website_id, func.avg(SeoPageAnalysis.score))
            .join(SeoAnalysis, SeoAnalysis.id == SeoPageAnalysis.seo_analysis_id)
            .join(CrawlSession, CrawlSession.id == SeoAnalysis.crawl_session_id)
            .where(
                CrawlSession.website_id.in_(website_ids),
                SeoPageAnalysis.score.is_not(None),
                SeoPageAnalysis.created_at >= start,
                SeoPageAnalysis.created_at <= end,
            )
            .group_by(CrawlSession.website_id)
        )
        issue_statement = (
            select(
                CrawlSession.website_id,
                func.count(SeoAnalysisIssue.id),
                func.coalesce(
                    func.sum(
                        case((func.lower(SeoAnalysisIssue.severity).in_(("critical", "major")), 1), else_=0),
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                func.lower(SeoAnalysisIssue.severity).in_(("warning", "medium", "minor")),
                                1,
                            ),
                            else_=0,
                        ),
                    ),
                    0,
                ),
            )
            .join(SeoAnalysis, SeoAnalysis.id == SeoAnalysisIssue.seo_analysis_id)
            .join(CrawlSession, CrawlSession.id == SeoAnalysis.crawl_session_id)
            .where(
                CrawlSession.website_id.in_(website_ids),
                SeoAnalysisIssue.created_at >= start,
                SeoAnalysisIssue.created_at <= end,
            )
            .group_by(CrawlSession.website_id)
        )
        results: dict[int, dict[str, Any]] = {}
        for row in self.db.execute(statement):
            website_id = int(row[0])
            results[website_id] = {
                "analyses_count": int(row[1] or 0),
                "completed_analyses": int(row[2] or 0),
                "failed_analyses": int(row[3] or 0),
                "global_score": self._float(row[4]),
                "pages_total": int(row[5] or 0),
                "pages_analyzed": int(row[6] or 0),
                "issues_total": int(row[7] or 0),
                "latest_analysis_at": row[8],
                "average_page_score": None,
                "critical_issues": 0,
                "warning_issues": 0,
            }
        for website_id, average_score in self.db.execute(page_statement):
            results.setdefault(int(website_id), {})["average_page_score"] = self._float(average_score)
        for website_id, issues_total, critical, warning in self.db.execute(issue_statement):
            item = results.setdefault(int(website_id), {})
            item["issues_total"] = int(issues_total or 0)
            item["critical_issues"] = int(critical or 0)
            item["warning_issues"] = int(warning or 0)
        return results

    def geo_aggregates(self, website_ids: list[int], *, start: datetime, end: datetime) -> dict[int, dict[str, Any]]:
        """Return GEO analysis aggregates by website."""

        if not website_ids:
            return {}
        statement = (
            select(
                CrawlSession.website_id,
                func.count(GeoAnalysis.id),
                self._status_count(GeoAnalysis.status, "COMPLETED"),
                self._status_count(GeoAnalysis.status, "PARTIAL"),
                self._status_count(GeoAnalysis.status, "FAILED"),
                func.avg(GeoAnalysis.geo_score),
                func.avg(GeoAnalysis.llm_score),
                func.avg(GeoAnalysis.global_score),
                func.coalesce(func.sum(GeoAnalysis.pages_total), 0),
                func.coalesce(func.sum(GeoAnalysis.pages_analyzed), 0),
                func.coalesce(func.sum(GeoAnalysis.provider_results_count), 0),
                func.coalesce(func.sum(GeoAnalysis.recommendations_count), 0),
                func.max(func.coalesce(GeoAnalysis.completed_at, GeoAnalysis.started_at, GeoAnalysis.created_at)),
            )
            .join(CrawlSession, CrawlSession.id == GeoAnalysis.crawl_session_id)
            .where(
                CrawlSession.website_id.in_(website_ids),
                GeoAnalysis.created_at >= start,
                GeoAnalysis.created_at <= end,
            )
            .group_by(CrawlSession.website_id)
        )
        provider_statement = (
            select(
                CrawlSession.website_id,
                self._status_count(GeoProviderResult.status, "FAILED"),
            )
            .join(GeoAnalysis, GeoAnalysis.id == GeoProviderResult.geo_analysis_id)
            .join(CrawlSession, CrawlSession.id == GeoAnalysis.crawl_session_id)
            .where(
                CrawlSession.website_id.in_(website_ids),
                GeoProviderResult.created_at >= start,
                GeoProviderResult.created_at <= end,
            )
            .group_by(CrawlSession.website_id)
        )
        recommendation_statement = (
            select(
                CrawlSession.website_id,
                func.count(GeoRecommendation.id),
                func.coalesce(func.sum(case((GeoRecommendation.priority <= 2, 1), else_=0)), 0),
            )
            .join(GeoAnalysis, GeoAnalysis.id == GeoRecommendation.geo_analysis_id)
            .join(CrawlSession, CrawlSession.id == GeoAnalysis.crawl_session_id)
            .where(
                CrawlSession.website_id.in_(website_ids),
                GeoRecommendation.created_at >= start,
                GeoRecommendation.created_at <= end,
            )
            .group_by(CrawlSession.website_id)
        )
        results: dict[int, dict[str, Any]] = {}
        for row in self.db.execute(statement):
            results[int(row[0])] = {
                "analyses_count": int(row[1] or 0),
                "completed_analyses": int(row[2] or 0),
                "partial_analyses": int(row[3] or 0),
                "failed_analyses": int(row[4] or 0),
                "geo_score": self._float(row[5]),
                "llm_score": self._float(row[6]),
                "global_score": self._float(row[7]),
                "pages_total": int(row[8] or 0),
                "pages_analyzed": int(row[9] or 0),
                "provider_results_count": int(row[10] or 0),
                "recommendations_count": int(row[11] or 0),
                "latest_analysis_at": row[12],
                "provider_failed_count": 0,
                "priority_recommendations": 0,
            }
        for website_id, failed_count in self.db.execute(provider_statement):
            results.setdefault(int(website_id), {})["provider_failed_count"] = int(failed_count or 0)
        for website_id, recommendations_count, priority_count in self.db.execute(recommendation_statement):
            item = results.setdefault(int(website_id), {})
            item["recommendations_count"] = int(recommendations_count or 0)
            item["priority_recommendations"] = int(priority_count or 0)
        return results

    def gsc_aggregates(self, website_ids: list[int], *, start_date: date, end_date: date) -> dict[int, dict[str, Any]]:
        """Return Google Search Console aggregates by website."""

        if not website_ids:
            return {}
        property_statement = (
            select(
                GoogleSearchConsoleProperty.website_id,
                func.count(GoogleSearchConsoleProperty.id),
                self._status_count(GoogleSearchConsoleProperty.is_active, True),
            )
            .where(GoogleSearchConsoleProperty.website_id.in_(website_ids))
            .group_by(GoogleSearchConsoleProperty.website_id)
        )
        performance_statement = (
            select(
                GoogleSearchConsoleProperty.website_id,
                func.coalesce(func.sum(GoogleSearchConsolePerformance.clicks), 0),
                func.coalesce(func.sum(GoogleSearchConsolePerformance.impressions), 0),
                func.coalesce(
                    func.sum(
                        GoogleSearchConsolePerformance.position
                        * GoogleSearchConsolePerformance.impressions,
                    ),
                    0.0,
                ),
            )
            .join(
                GoogleSearchConsoleProperty,
                GoogleSearchConsoleProperty.id == GoogleSearchConsolePerformance.property_id,
            )
            .where(
                GoogleSearchConsoleProperty.website_id.in_(website_ids),
                GoogleSearchConsolePerformance.date >= start_date,
                GoogleSearchConsolePerformance.date <= end_date,
            )
            .group_by(GoogleSearchConsoleProperty.website_id)
        )
        coverage_statement = (
            select(
                GoogleSearchConsoleProperty.website_id,
                func.count(GoogleSearchConsoleIndexCoverage.id),
                self._state_count(GoogleSearchConsoleIndexCoverage.coverage_state, ("ERROR", "FAIL", "FAILED")),
                self._state_count(GoogleSearchConsoleIndexCoverage.coverage_state, ("WARNING", "WARN", "PARTIAL")),
                self._state_count(
                    GoogleSearchConsoleIndexCoverage.coverage_state,
                    ("EXCLUDED", "NOT_INDEXED", "BLOCKED", "REMOVED"),
                ),
            )
            .join(
                GoogleSearchConsoleProperty,
                GoogleSearchConsoleProperty.id == GoogleSearchConsoleIndexCoverage.property_id,
            )
            .where(GoogleSearchConsoleProperty.website_id.in_(website_ids))
            .group_by(GoogleSearchConsoleProperty.website_id)
        )
        sitemap_statement = (
            select(
                GoogleSearchConsoleProperty.website_id,
                func.coalesce(func.sum(GoogleSearchConsoleSitemap.errors), 0),
                func.coalesce(func.sum(GoogleSearchConsoleSitemap.warnings), 0),
            )
            .join(GoogleSearchConsoleProperty, GoogleSearchConsoleProperty.id == GoogleSearchConsoleSitemap.property_id)
            .where(GoogleSearchConsoleProperty.website_id.in_(website_ids))
            .group_by(GoogleSearchConsoleProperty.website_id)
        )
        import_statement = (
            select(
                GoogleSearchConsoleProperty.website_id,
                self._status_count(GoogleSearchConsoleImport.status, "FAILED"),
                func.max(GoogleSearchConsoleImport.completed_at),
            )
            .join(GoogleSearchConsoleProperty, GoogleSearchConsoleProperty.id == GoogleSearchConsoleImport.property_id)
            .where(GoogleSearchConsoleProperty.website_id.in_(website_ids))
            .group_by(GoogleSearchConsoleProperty.website_id)
        )
        results: dict[int, dict[str, Any]] = {}
        for website_id, total, active in self.db.execute(property_statement):
            results[int(website_id)] = {"properties_count": int(total or 0), "active_properties": int(active or 0)}
        for website_id, clicks, impressions, position_weight in self.db.execute(performance_statement):
            item = results.setdefault(int(website_id), {})
            item["clicks"] = int(clicks or 0)
            item["impressions"] = int(impressions or 0)
            item["position_weight"] = float(position_weight or 0.0)
        for website_id, total, errors, warnings, excluded in self.db.execute(coverage_statement):
            item = results.setdefault(int(website_id), {})
            item["valid_pages"] = max(int(total or 0) - int(errors or 0) - int(warnings or 0) - int(excluded or 0), 0)
            item["index_errors"] = int(errors or 0)
            item["index_warnings"] = int(warnings or 0)
            item["excluded_pages"] = int(excluded or 0)
        for website_id, errors, warnings in self.db.execute(sitemap_statement):
            item = results.setdefault(int(website_id), {})
            item["sitemap_errors"] = int(errors or 0)
            item["sitemap_warnings"] = int(warnings or 0)
        for website_id, failed_imports, latest_at in self.db.execute(import_statement):
            item = results.setdefault(int(website_id), {})
            item["failed_imports"] = int(failed_imports or 0)
            item["latest_import_at"] = latest_at
        return results

    def ga4_aggregates(self, website_ids: list[int], *, start_date: date, end_date: date) -> dict[int, dict[str, Any]]:
        """Return Google Analytics 4 aggregates by website."""

        if not website_ids:
            return {}
        property_statement = (
            select(
                GoogleAnalyticsProperty.website_id,
                func.count(GoogleAnalyticsProperty.id),
                self._status_count(GoogleAnalyticsProperty.enabled, True),
            )
            .where(GoogleAnalyticsProperty.website_id.in_(website_ids))
            .group_by(GoogleAnalyticsProperty.website_id)
        )
        metric_statement = (
            select(
                GoogleAnalyticsProperty.website_id,
                func.coalesce(func.sum(GoogleAnalyticsMetric.sessions), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.users), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.new_users), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.engaged_sessions), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.screen_page_views), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.conversions), 0.0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.total_revenue), 0.0),
                func.coalesce(
                    func.sum(GoogleAnalyticsMetric.average_session_duration * GoogleAnalyticsMetric.sessions),
                    0.0,
                ),
                func.coalesce(func.sum(GoogleAnalyticsMetric.engagement_rate * GoogleAnalyticsMetric.sessions), 0.0),
            )
            .join(GoogleAnalyticsProperty, GoogleAnalyticsProperty.id == GoogleAnalyticsMetric.property_id)
            .where(
                GoogleAnalyticsProperty.website_id.in_(website_ids),
                GoogleAnalyticsMetric.date >= start_date,
                GoogleAnalyticsMetric.date <= end_date,
            )
            .group_by(GoogleAnalyticsProperty.website_id)
        )
        import_statement = (
            select(
                GoogleAnalyticsProperty.website_id,
                self._status_count(GoogleAnalyticsImport.status, "FAILED"),
                func.max(GoogleAnalyticsImport.finished_at),
            )
            .join(GoogleAnalyticsProperty, GoogleAnalyticsProperty.id == GoogleAnalyticsImport.property_id)
            .where(GoogleAnalyticsProperty.website_id.in_(website_ids))
            .group_by(GoogleAnalyticsProperty.website_id)
        )
        results: dict[int, dict[str, Any]] = {}
        for website_id, total, active in self.db.execute(property_statement):
            results[int(website_id)] = {"properties_count": int(total or 0), "active_properties": int(active or 0)}
        for row in self.db.execute(metric_statement):
            item = results.setdefault(int(row[0]), {})
            item.update(
                {
                    "sessions": int(row[1] or 0),
                    "users": int(row[2] or 0),
                    "new_users": int(row[3] or 0),
                    "engaged_sessions": int(row[4] or 0),
                    "screen_page_views": int(row[5] or 0),
                    "conversions": float(row[6] or 0.0),
                    "total_revenue": float(row[7] or 0.0),
                    "duration_weight": float(row[8] or 0.0),
                    "engagement_weight": float(row[9] or 0.0),
                },
            )
        for website_id, failed_imports, latest_at in self.db.execute(import_statement):
            item = results.setdefault(int(website_id), {})
            item["failed_imports"] = int(failed_imports or 0)
            item["latest_import_at"] = latest_at
        return results

    def bing_aggregates(self, website_ids: list[int], *, start_date: date, end_date: date) -> dict[int, dict[str, Any]]:
        """Return Bing Webmaster Tools aggregates by website."""

        if not website_ids:
            return {}
        connection_statement = (
            select(
                BingWebmasterConnection.website_id,
                func.count(BingWebmasterConnection.id),
                self._status_count(BingWebmasterConnection.is_active, True),
                func.max(BingWebmasterConnection.last_sync_at),
            )
            .where(BingWebmasterConnection.website_id.in_(website_ids))
            .group_by(BingWebmasterConnection.website_id)
        )
        site_statement = (
            select(
                BingWebmasterSite.website_id,
                func.count(BingWebmasterSite.id),
                self._status_count(BingWebmasterSite.is_verified, True),
            )
            .where(BingWebmasterSite.website_id.in_(website_ids))
            .group_by(BingWebmasterSite.website_id)
        )
        metric_statement = (
            select(
                BingWebmasterSite.website_id,
                func.coalesce(func.sum(BingWebmasterMetric.clicks), 0),
                func.coalesce(func.sum(BingWebmasterMetric.impressions), 0),
                func.coalesce(func.sum(BingWebmasterMetric.average_position * BingWebmasterMetric.impressions), 0.0),
            )
            .join(BingWebmasterSite, BingWebmasterSite.id == BingWebmasterMetric.bing_site_id)
            .where(
                BingWebmasterSite.website_id.in_(website_ids),
                BingWebmasterMetric.date >= start_date,
                BingWebmasterMetric.date <= end_date,
            )
            .group_by(BingWebmasterSite.website_id)
        )
        crawl_statement = (
            select(
                BingWebmasterSite.website_id,
                func.count(BingWebmasterCrawlStat.id),
                self._state_count(BingWebmasterCrawlStat.severity, ("critical", "error", "high")),
            )
            .join(BingWebmasterSite, BingWebmasterSite.id == BingWebmasterCrawlStat.bing_site_id)
            .where(
                BingWebmasterSite.website_id.in_(website_ids),
                BingWebmasterCrawlStat.date >= start_date,
                BingWebmasterCrawlStat.date <= end_date,
            )
            .group_by(BingWebmasterSite.website_id)
        )
        sitemap_statement = (
            select(
                BingWebmasterSite.website_id,
                func.coalesce(func.sum(BingWebmasterSitemap.error_count), 0),
                func.coalesce(func.sum(BingWebmasterSitemap.warning_count), 0),
            )
            .join(BingWebmasterSite, BingWebmasterSite.id == BingWebmasterSitemap.bing_site_id)
            .where(BingWebmasterSite.website_id.in_(website_ids))
            .group_by(BingWebmasterSite.website_id)
        )
        import_statement = (
            select(
                BingWebmasterConnection.website_id,
                self._status_count(BingWebmasterImportRun.status, "FAILED"),
                func.max(BingWebmasterImportRun.finished_at),
            )
            .join(BingWebmasterConnection, BingWebmasterConnection.id == BingWebmasterImportRun.connection_id)
            .where(BingWebmasterConnection.website_id.in_(website_ids))
            .group_by(BingWebmasterConnection.website_id)
        )
        results: dict[int, dict[str, Any]] = {}
        for website_id, total, active, latest_at in self.db.execute(connection_statement):
            results[int(website_id)] = {
                "connections_count": int(total or 0),
                "active_connections": int(active or 0),
                "latest_import_at": latest_at,
            }
        for website_id, total, verified in self.db.execute(site_statement):
            item = results.setdefault(int(website_id), {})
            item["sites_count"] = int(total or 0)
            item["verified_sites"] = int(verified or 0)
        for website_id, clicks, impressions, position_weight in self.db.execute(metric_statement):
            item = results.setdefault(int(website_id), {})
            item["clicks"] = int(clicks or 0)
            item["impressions"] = int(impressions or 0)
            item["position_weight"] = float(position_weight or 0.0)
        for website_id, crawl_rows, crawl_errors in self.db.execute(crawl_statement):
            item = results.setdefault(int(website_id), {})
            item["crawl_rows"] = int(crawl_rows or 0)
            item["crawl_errors"] = int(crawl_errors or 0)
        for website_id, errors, warnings in self.db.execute(sitemap_statement):
            item = results.setdefault(int(website_id), {})
            item["sitemap_errors"] = int(errors or 0)
            item["sitemap_warnings"] = int(warnings or 0)
        for website_id, failed_imports, latest_at in self.db.execute(import_statement):
            item = results.setdefault(int(website_id), {})
            item["failed_imports"] = int(failed_imports or 0)
            if latest_at is not None:
                item["latest_import_at"] = latest_at
        return results

    def monitoring_aggregates(self, *, start: datetime, end: datetime) -> dict[str, Any]:
        """Return monitoring counters."""

        total = int(self.db.scalar(select(func.count()).select_from(MonitoringEvent)) or 0)
        period_filters = (MonitoringEvent.created_at >= start, MonitoringEvent.created_at <= end)
        period_events = int(
            self.db.scalar(select(func.count()).select_from(MonitoringEvent).where(*period_filters)) or 0,
        )
        by_severity = {
            str(severity): int(count or 0)
            for severity, count in self.db.execute(
                select(MonitoringEvent.severity, func.count(MonitoringEvent.id))
                .where(*period_filters)
                .group_by(MonitoringEvent.severity),
            )
        }
        by_source = {
            str(source): int(count or 0)
            for source, count in self.db.execute(
                select(MonitoringEvent.source, func.count(MonitoringEvent.id))
                .where(*period_filters)
                .group_by(MonitoringEvent.source),
            )
        }
        by_type = {
            str(event_type): int(count or 0)
            for event_type, count in self.db.execute(
                select(MonitoringEvent.event_type, func.count(MonitoringEvent.id))
                .where(*period_filters)
                .group_by(MonitoringEvent.event_type),
            )
        }
        last_event_at = self.db.scalar(select(func.max(MonitoringEvent.created_at)))
        return {
            "total_events": total,
            "period_events": period_events,
            "warning_events": by_severity.get("warning", 0),
            "error_events": by_severity.get("error", 0),
            "critical_events": by_severity.get("critical", 0),
            "by_source": by_source,
            "by_type": by_type,
            "last_event_at": last_event_at,
        }

    def alert_aggregates(self, *, start: datetime, end: datetime) -> dict[str, Any]:
        """Return alert counters."""

        period_filters = (Alert.last_seen_at >= start, Alert.last_seen_at <= end)
        by_status = {
            str(status): int(count or 0)
            for status, count in self.db.execute(select(Alert.status, func.count(Alert.id)).group_by(Alert.status))
        }
        by_severity = {
            str(severity): int(count or 0)
            for severity, count in self.db.execute(
                select(Alert.severity, func.count(Alert.id)).where(*period_filters).group_by(Alert.severity),
            )
        }
        return {
            "total": int(self.db.scalar(select(func.count()).select_from(Alert)) or 0),
            "active": by_status.get("Active", 0),
            "acknowledged": by_status.get("Acknowledged", 0),
            "resolved": by_status.get("Resolved", 0),
            "info": by_severity.get("Info", 0),
            "warning": by_severity.get("Warning", 0),
            "critical": by_severity.get("Critical", 0),
            "last_alert_at": self.db.scalar(select(func.max(Alert.last_seen_at))),
        }

    def active_alert_counts_by_website(self, website_ids: list[int]) -> dict[int, int]:
        """Return active alert counts keyed by metadata website id when available."""

        if not website_ids:
            return {}
        counts = dict.fromkeys(website_ids, 0)
        statement = select(Alert.metadata_).where(Alert.status.in_(("Active", "Acknowledged")))
        for metadata in self.db.scalars(statement):
            if not isinstance(metadata, dict):
                continue
            website_id = self._int_or_none(metadata.get("website_id"))
            if website_id in counts:
                counts[website_id] += 1
        return counts

    def operations_aggregates(self, *, start: datetime, end: datetime, now: datetime) -> dict[str, Any]:
        """Return job and worker counters."""

        by_status = {
            str(status): int(count or 0)
            for status, count in self.db.execute(
                select(ProcessingJob.status, func.count()).group_by(ProcessingJob.status),
            )
        }
        blocked = int(
            self.db.scalar(
                select(func.count())
                .select_from(ProcessingJob)
                .where(
                    ProcessingJob.status.in_(("RESERVED", "RUNNING")),
                    ProcessingJob.lock_expires_at.is_not(None),
                    ProcessingJob.lock_expires_at < now,
                ),
            )
            or 0,
        )
        period_failed = int(
            self.db.scalar(
                select(func.count())
                .select_from(ProcessingJob)
                .where(
                    ProcessingJob.status == "FAILED",
                    ProcessingJob.created_at >= start,
                    ProcessingJob.created_at <= end,
                ),
            )
            or 0,
        )
        workers = self.list_workers()
        return {
            "pending_jobs": by_status.get("PENDING", 0),
            "reserved_jobs": by_status.get("RESERVED", 0),
            "running_jobs": by_status.get("RUNNING", 0),
            "retry_scheduled_jobs": by_status.get("RETRY_SCHEDULED", 0),
            "succeeded_jobs": by_status.get("SUCCEEDED", 0),
            "failed_jobs": by_status.get("FAILED", 0),
            "cancelled_jobs": by_status.get("CANCELLED", 0),
            "blocked_jobs": blocked,
            "period_failed_jobs": period_failed,
            "total_jobs": sum(by_status.values()),
            "last_activity_at": self.db.scalar(select(func.max(ProcessingJob.updated_at))),
            "workers": workers,
        }

    def failed_or_blocked_jobs_by_website(self, website_ids: list[int], *, now: datetime) -> dict[int, int]:
        """Return failed or blocked jobs keyed by payload website id when available."""

        counts = dict.fromkeys(website_ids, 0)
        if not website_ids:
            return counts
        statement = select(ProcessingJob.payload, ProcessingJob.status, ProcessingJob.lock_expires_at).where(
            ProcessingJob.status.in_(("FAILED", "RESERVED", "RUNNING")),
        )
        for payload, job_status, lock_expires_at in self.db.execute(statement):
            if not isinstance(payload, dict):
                continue
            website_id = self._int_or_none(payload.get("website_id"))
            if website_id not in counts:
                continue
            if job_status == "FAILED" or (lock_expires_at is not None and lock_expires_at < now):
                counts[website_id] += 1
        return counts

    def list_workers(self) -> list[dict[str, Any]]:
        """Return worker rows as simple dictionaries."""

        statement = select(ProcessingWorker).order_by(ProcessingWorker.last_heartbeat_at.desc())
        return [
            {
                "worker_id": worker.worker_id,
                "status": worker.status,
                "last_heartbeat_at": worker.last_heartbeat_at,
                "current_job_id": worker.current_job_id,
                "version": worker.version,
            }
            for worker in self.db.scalars(statement)
        ]

    def trend_rows(
        self,
        metric: str,
        *,
        start: datetime,
        end: datetime,
        start_date: date,
        end_date: date,
        website_ids: list[int],
    ) -> list[tuple[date, float]]:
        """Return simple day-level trend rows for one whitelisted metric."""

        if not website_ids:
            return []
        if metric == "seo_score":
            statement = (
                select(func.date(SeoPageAnalysis.created_at), func.avg(SeoPageAnalysis.score))
                .join(SeoAnalysis, SeoAnalysis.id == SeoPageAnalysis.seo_analysis_id)
                .join(CrawlSession, CrawlSession.id == SeoAnalysis.crawl_session_id)
                .where(
                    CrawlSession.website_id.in_(website_ids),
                    SeoPageAnalysis.score.is_not(None),
                    SeoPageAnalysis.created_at >= start,
                    SeoPageAnalysis.created_at <= end,
                )
                .group_by(func.date(SeoPageAnalysis.created_at))
            )
        elif metric == "geo_score":
            statement = (
                select(func.date(GeoAnalysis.created_at), func.avg(GeoAnalysis.geo_score))
                .join(CrawlSession, CrawlSession.id == GeoAnalysis.crawl_session_id)
                .where(
                    CrawlSession.website_id.in_(website_ids),
                    GeoAnalysis.geo_score.is_not(None),
                    GeoAnalysis.created_at >= start,
                    GeoAnalysis.created_at <= end,
                )
                .group_by(func.date(GeoAnalysis.created_at))
            )
        elif metric in {"gsc_clicks", "gsc_impressions"}:
            column = GoogleSearchConsolePerformance.clicks
            if metric == "gsc_impressions":
                column = GoogleSearchConsolePerformance.impressions
            statement = (
                select(GoogleSearchConsolePerformance.date, func.coalesce(func.sum(column), 0))
                .join(
                    GoogleSearchConsoleProperty,
                    GoogleSearchConsoleProperty.id == GoogleSearchConsolePerformance.property_id,
                )
                .where(
                    GoogleSearchConsoleProperty.website_id.in_(website_ids),
                    GoogleSearchConsolePerformance.date >= start_date,
                    GoogleSearchConsolePerformance.date <= end_date,
                )
                .group_by(GoogleSearchConsolePerformance.date)
            )
        elif metric in {"ga4_sessions", "ga4_users"}:
            column = GoogleAnalyticsMetric.sessions if metric == "ga4_sessions" else GoogleAnalyticsMetric.users
            statement = (
                select(GoogleAnalyticsMetric.date, func.coalesce(func.sum(column), 0))
                .join(GoogleAnalyticsProperty, GoogleAnalyticsProperty.id == GoogleAnalyticsMetric.property_id)
                .where(
                    GoogleAnalyticsProperty.website_id.in_(website_ids),
                    GoogleAnalyticsMetric.date >= start_date,
                    GoogleAnalyticsMetric.date <= end_date,
                )
                .group_by(GoogleAnalyticsMetric.date)
            )
        elif metric in {"bing_clicks", "bing_impressions"}:
            column = BingWebmasterMetric.clicks if metric == "bing_clicks" else BingWebmasterMetric.impressions
            statement = (
                select(BingWebmasterMetric.date, func.coalesce(func.sum(column), 0))
                .join(BingWebmasterSite, BingWebmasterSite.id == BingWebmasterMetric.bing_site_id)
                .where(
                    BingWebmasterSite.website_id.in_(website_ids),
                    BingWebmasterMetric.date >= start_date,
                    BingWebmasterMetric.date <= end_date,
                )
                .group_by(BingWebmasterMetric.date)
            )
        elif metric == "alerts_active":
            statement = (
                select(func.date(Alert.last_seen_at), func.count(Alert.id))
                .where(
                    Alert.status.in_(("Active", "Acknowledged")),
                    Alert.last_seen_at >= start,
                    Alert.last_seen_at <= end,
                )
                .group_by(func.date(Alert.last_seen_at))
            )
        elif metric == "jobs_failed":
            statement = (
                select(func.date(ProcessingJob.created_at), func.count(ProcessingJob.id))
                .where(
                    ProcessingJob.status == "FAILED",
                    ProcessingJob.created_at >= start,
                    ProcessingJob.created_at <= end,
                )
                .group_by(func.date(ProcessingJob.created_at))
            )
        else:
            statement = (
                select(func.date(ProcessingJob.created_at), func.count(ProcessingJob.id))
                .where(
                    ProcessingJob.status.in_(("RESERVED", "RUNNING")),
                    ProcessingJob.lock_expires_at.is_not(None),
                    ProcessingJob.lock_expires_at < end,
                    ProcessingJob.created_at >= start,
                    ProcessingJob.created_at <= end,
                )
                .group_by(func.date(ProcessingJob.created_at))
            )
        return [(self._date(row[0]), float(row[1] or 0.0)) for row in self.db.execute(statement).all()]

    def _website_filters(
        self,
        *,
        website_id: int | None,
        entity_id: int | None,
        is_active: bool | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if website_id is not None:
            filters.append(Website.id == website_id)
        if entity_id is not None:
            filters.append(Website.entity_id == entity_id)
        if is_active is not None:
            filters.append(Website.is_active.is_(is_active))
        if search:
            like_pattern = f"%{search}%"
            filters.append(or_(Website.name.ilike(like_pattern), Website.url.ilike(like_pattern)))
        return filters

    def _status_count(self, column: Any, value: Any) -> Any:
        return func.coalesce(func.sum(case((column == value, 1), else_=0)), 0)

    def _state_count(self, column: Any, values: Iterable[str]) -> Any:
        normalized = tuple(value.lower() for value in values)
        return func.coalesce(func.sum(case((func.lower(column).in_(normalized), 1), else_=0)), 0)

    def _float(self, value: Any) -> float | None:
        if value is None:
            return None
        return float(value)

    def _int_or_none(self, value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    def _date(self, value: Any) -> date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return date.fromisoformat(value[:10])
        return datetime.combine(date.today(), time.min).date()
