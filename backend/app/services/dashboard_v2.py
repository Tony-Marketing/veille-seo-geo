"""Business service for Dashboard V2."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta
from math import ceil
from typing import Any

from fastapi import HTTPException, status

from backend.app.models import Website
from backend.app.repositories.dashboard_v2 import DashboardV2Repository
from backend.app.schemas.dashboard_v2 import (
    DashboardV2AlertKpis,
    DashboardV2BingKpis,
    DashboardV2Filters,
    DashboardV2Ga4Kpis,
    DashboardV2GeoKpis,
    DashboardV2Granularity,
    DashboardV2GscKpis,
    DashboardV2HealthComponent,
    DashboardV2HealthScore,
    DashboardV2HealthStatus,
    DashboardV2MonitoringKpis,
    DashboardV2OperationsKpis,
    DashboardV2OverviewResponse,
    DashboardV2Period,
    DashboardV2Recommendation,
    DashboardV2RecommendationList,
    DashboardV2RecommendationSeverity,
    DashboardV2ResolvedPeriod,
    DashboardV2SeoKpis,
    DashboardV2Source,
    DashboardV2SourceAvailability,
    DashboardV2TrendMetric,
    DashboardV2TrendPoint,
    DashboardV2TrendSeries,
    DashboardV2TrendsResponse,
    DashboardV2WebsiteList,
    DashboardV2WebsiteSummary,
    DashboardV2WorkerKpis,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.recommendations import (
    RecommendationFilters,
    RecommendationPriority,
    RecommendationRead,
)
from backend.app.services.recommendations import RecommendationService

SEO_WEIGHT = 0.35
GEO_WEIGHT = 0.20
SEARCH_WEIGHT = 0.15
TRAFFIC_WEIGHT = 0.10
TECHNICAL_WEIGHT = 0.10
OPERATIONS_WEIGHT = 0.10

WEBSITE_SORT_FIELDS = {
    "name",
    "health_score",
    "seo_score",
    "geo_score",
    "gsc_clicks",
    "ga4_sessions",
    "bing_clicks",
    "active_alerts",
    "last_activity_at",
}
RECOMMENDATION_SORT_FIELDS = {"priority", "severity", "source", "created_at", "website_name"}


class DashboardV2Service:
    """Aggregate Dashboard V2 data and consume transverse recommendations."""

    def __init__(
        self,
        repository: DashboardV2Repository,
        recommendation_service: RecommendationService,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.recommendation_service = recommendation_service
        self.now_provider = now_provider or (lambda: datetime.now(UTC))

    def overview(self, filters: DashboardV2Filters | None = None) -> DashboardV2OverviewResponse:
        """Return the executive Dashboard V2 overview."""

        filters = self._normalize_filters(filters or DashboardV2Filters())
        period = self._resolve_period(filters)
        previous_period = self._previous_period(period) if filters.compare_to_previous else None
        websites = self.repository.list_all_websites(
            website_id=filters.website_id,
            entity_id=filters.entity_id,
            is_active=filters.is_active,
            search=filters.search,
        )
        raw = self._raw_data(websites, period)
        previous_raw = self._raw_data(websites, previous_period) if previous_period is not None else None

        website_summaries = self._website_summaries(websites, raw, filters)
        top_recommendations = self._engine_recommendations(websites=websites, filters=filters)[:10]
        global_health = self._global_health(raw, previous_raw)
        partial_data = self._partial_data(raw)
        return DashboardV2OverviewResponse(
            generated_at=self._now(),
            filters=self._filters_dict(filters),
            period=period,
            previous_period=previous_period,
            sources=self._sources(raw),
            global_health=global_health,
            seo=self._seo_kpis(self._sum_dicts(raw["seo"].values())),
            geo=self._geo_kpis(self._sum_dicts(raw["geo"].values())),
            gsc=self._gsc_kpis(self._sum_dicts(raw["gsc"].values())),
            ga4=self._ga4_kpis(self._sum_dicts(raw["ga4"].values())),
            bing=self._bing_kpis(self._sum_dicts(raw["bing"].values())),
            technical=global_health.components[4],
            operations=self._operations_kpis(raw["operations"]),
            monitoring=self._monitoring_kpis(raw["monitoring"]),
            alerts=self._alert_kpis(raw["alerts"]),
            workers=self._worker_kpis(raw["operations"].get("workers", []), raw["operations"]),
            top_websites=website_summaries[:10],
            top_recommendations=top_recommendations,
            partial_data=partial_data,
        )

    def trends(
        self,
        *,
        filters: DashboardV2Filters | None = None,
        granularity: DashboardV2Granularity = DashboardV2Granularity.DAY,
        metrics: list[DashboardV2TrendMetric] | None = None,
    ) -> DashboardV2TrendsResponse:
        """Return trend series for whitelisted metrics."""

        filters = self._normalize_filters(filters or DashboardV2Filters())
        period = self._resolve_period(filters)
        websites = self.repository.list_all_websites(
            website_id=filters.website_id,
            entity_id=filters.entity_id,
            is_active=filters.is_active,
            search=filters.search,
        )
        website_ids = [website.id for website in websites]
        selected_metrics = metrics or [
            DashboardV2TrendMetric.SEO_SCORE,
            DashboardV2TrendMetric.GEO_SCORE,
            DashboardV2TrendMetric.GSC_CLICKS,
            DashboardV2TrendMetric.GA4_SESSIONS,
            DashboardV2TrendMetric.BING_CLICKS,
        ]
        start = self._datetime_start(period.date_from)
        end = self._datetime_end(period.date_to)
        series = []
        for metric in selected_metrics:
            rows = self.repository.trend_rows(
                metric.value,
                start=start,
                end=end,
                start_date=period.date_from,
                end_date=period.date_to,
                website_ids=website_ids,
            )
            series.append(
                DashboardV2TrendSeries(
                    metric=metric,
                    label=self._trend_label(metric),
                    source=self._metric_source(metric),
                    points=self._trend_points(rows, granularity),
                ),
            )
        return DashboardV2TrendsResponse(
            generated_at=self._now(),
            filters=self._filters_dict(filters),
            granularity=granularity,
            series=series,
        )

    def websites(
        self,
        params: PaginationParams,
        *,
        filters: DashboardV2Filters | None = None,
    ) -> DashboardV2WebsiteList:
        """Return paginated multi-site dashboard summaries."""

        filters = self._normalize_filters(filters or DashboardV2Filters())
        self._validate_website_sort(params.sort)
        period = self._resolve_period(filters)
        websites = self.repository.list_all_websites(
            website_id=filters.website_id,
            entity_id=filters.entity_id,
            is_active=filters.is_active,
            search=filters.search,
        )
        raw = self._raw_data(websites, period)
        items = self._website_summaries(websites, raw, filters)
        items = self._sort_websites(items, params.sort, params.order)
        total = len(items)
        paginated = items[params.offset : params.offset + params.page_size]
        return DashboardV2WebsiteList(
            items=paginated,
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=self._filters_dict(filters),
        )

    def recommendations(
        self,
        params: PaginationParams,
        *,
        filters: DashboardV2Filters | None = None,
        severity: DashboardV2RecommendationSeverity | None = None,
        priority: int | None = None,
    ) -> DashboardV2RecommendationList:
        """Return paginated recommendations produced by RecommendationService."""

        filters = self._normalize_filters(filters or DashboardV2Filters())
        self._validate_recommendation_sort(params.sort)
        websites = self.repository.list_all_websites(
            website_id=filters.website_id,
            entity_id=filters.entity_id,
            is_active=filters.is_active,
            search=filters.search,
        )
        items = self._engine_recommendations(websites=websites, filters=filters)
        if severity is not None:
            items = [item for item in items if item.severity == severity]
        if priority is not None:
            items = [item for item in items if item.priority == priority]
        items = self._sort_recommendations(items, params.sort, params.order)
        total = len(items)
        paginated = items[params.offset : params.offset + params.page_size]
        values = self._filters_dict(filters)
        if severity is not None:
            values["severity"] = severity.value
        if priority is not None:
            values["priority"] = priority
        return DashboardV2RecommendationList(
            items=paginated,
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=values,
        )

    def _raw_data(self, websites: list[Website], period: DashboardV2ResolvedPeriod | None) -> dict[str, Any]:
        website_ids = [website.id for website in websites]
        if period is None:
            return self._empty_raw()
        start = self._datetime_start(period.date_from)
        end = self._datetime_end(period.date_to)
        now = self._now()
        return {
            "period": period,
            "crawl": self.repository.crawl_aggregates(website_ids, start=start, end=end),
            "seo": self.repository.seo_aggregates(website_ids, start=start, end=end),
            "geo": self.repository.geo_aggregates(website_ids, start=start, end=end),
            "gsc": self.repository.gsc_aggregates(website_ids, start_date=period.date_from, end_date=period.date_to),
            "ga4": self.repository.ga4_aggregates(website_ids, start_date=period.date_from, end_date=period.date_to),
            "bing": self.repository.bing_aggregates(website_ids, start_date=period.date_from, end_date=period.date_to),
            "monitoring": self.repository.monitoring_aggregates(start=start, end=end),
            "alerts": self.repository.alert_aggregates(start=start, end=end),
            "operations": self.repository.operations_aggregates(start=start, end=end, now=now),
            "active_alerts_by_website": self.repository.active_alert_counts_by_website(website_ids),
            "jobs_by_website": self.repository.failed_or_blocked_jobs_by_website(website_ids, now=now),
        }

    def _empty_raw(self) -> dict[str, Any]:
        return {
            "period": None,
            "crawl": {},
            "seo": {},
            "geo": {},
            "gsc": {},
            "ga4": {},
            "bing": {},
            "monitoring": {},
            "alerts": {},
            "operations": {"workers": []},
            "active_alerts_by_website": {},
            "jobs_by_website": {},
        }

    def _website_summaries(
        self,
        websites: list[Website],
        raw: dict[str, Any],
        filters: DashboardV2Filters,
    ) -> list[DashboardV2WebsiteSummary]:
        summaries = []
        for website in websites:
            website_id = website.id
            seo = raw["seo"].get(website_id, {})
            geo = raw["geo"].get(website_id, {})
            gsc = raw["gsc"].get(website_id, {})
            ga4 = raw["ga4"].get(website_id, {})
            bing = raw["bing"].get(website_id, {})
            crawl = raw["crawl"].get(website_id, {})
            active_alerts = int(raw["active_alerts_by_website"].get(website_id, 0))
            failed_jobs = int(raw["jobs_by_website"].get(website_id, 0))
            health = self._site_health(
                seo=seo,
                geo=geo,
                gsc=gsc,
                ga4=ga4,
                bing=bing,
                crawl=crawl,
                active_alerts=active_alerts,
                failed_jobs=failed_jobs,
            )
            summary = DashboardV2WebsiteSummary(
                website_id=website_id,
                name=website.name,
                url=website.url,
                is_active=website.is_active,
                health_score=health.score,
                health_status=health.status,
                seo_score=self._seo_health(seo),
                geo_score=self._geo_health(geo),
                gsc_clicks=int(gsc.get("clicks") or 0),
                gsc_impressions=int(gsc.get("impressions") or 0),
                ga4_sessions=int(ga4.get("sessions") or 0),
                bing_clicks=int(bing.get("clicks") or 0),
                bing_impressions=int(bing.get("impressions") or 0),
                active_alerts=active_alerts,
                failed_or_blocked_jobs=failed_jobs,
                last_activity_at=self._latest(
                    seo.get("latest_analysis_at"),
                    geo.get("latest_analysis_at"),
                    gsc.get("latest_import_at"),
                    ga4.get("latest_import_at"),
                    bing.get("latest_import_at"),
                    crawl.get("latest_at"),
                ),
                available_sources=health.available_components,
                missing_sources=health.missing_components,
            )
            if filters.health_status is None or summary.health_status == filters.health_status:
                summaries.append(summary)
        return self._sort_websites(summaries, None, "asc")

    def _site_health(
        self,
        *,
        seo: dict[str, Any],
        geo: dict[str, Any],
        gsc: dict[str, Any],
        ga4: dict[str, Any],
        bing: dict[str, Any],
        crawl: dict[str, Any],
        active_alerts: int,
        failed_jobs: int,
    ) -> DashboardV2HealthScore:
        components = [
            self._component("seo", self._seo_health(seo)),
            self._component("geo", self._geo_health(geo)),
            self._component("search_visibility", self._search_visibility_health(gsc, bing)),
            self._component("traffic", self._traffic_health(ga4, None)),
            self._component("technical", self._technical_health(crawl, gsc, bing)),
            self._component(
                "operations",
                self._operations_health(
                    {
                        "critical_alerts": active_alerts,
                        "warning_alerts": 0,
                        "period_failed_jobs": failed_jobs,
                        "blocked_jobs": failed_jobs,
                        "pending_jobs": 0,
                        "workers": [],
                    },
                    {},
                ),
            ),
        ]
        weighted = [
            (components[0], SEO_WEIGHT),
            (components[1], GEO_WEIGHT),
            (components[2], SEARCH_WEIGHT),
            (components[3], TRAFFIC_WEIGHT),
            (components[4], TECHNICAL_WEIGHT),
            (components[5], OPERATIONS_WEIGHT),
        ]
        return self._weighted_health(weighted)

    def _global_health(self, raw: dict[str, Any], previous_raw: dict[str, Any] | None) -> DashboardV2HealthScore:
        seo = self._sum_dicts(raw["seo"].values())
        geo = self._sum_dicts(raw["geo"].values())
        gsc = self._sum_dicts(raw["gsc"].values())
        ga4 = self._sum_dicts(raw["ga4"].values())
        bing = self._sum_dicts(raw["bing"].values())
        crawl = self._sum_dicts(raw["crawl"].values())
        previous_ga4 = self._sum_dicts(previous_raw["ga4"].values()) if previous_raw is not None else None
        components = [
            self._component("seo", self._seo_health(seo)),
            self._component("geo", self._geo_health(geo)),
            self._component("search_visibility", self._search_visibility_health(gsc, bing)),
            self._component("traffic", self._traffic_health(ga4, previous_ga4)),
            self._component("technical", self._technical_health(crawl, gsc, bing)),
            self._component("operations", self._operations_health(raw["operations"], raw["alerts"])),
        ]
        weighted = [
            (components[0], SEO_WEIGHT),
            (components[1], GEO_WEIGHT),
            (components[2], SEARCH_WEIGHT),
            (components[3], TRAFFIC_WEIGHT),
            (components[4], TECHNICAL_WEIGHT),
            (components[5], OPERATIONS_WEIGHT),
        ]
        return self._weighted_health(weighted)

    def _seo_health(self, seo: dict[str, Any]) -> float | None:
        score = self._number(seo.get("average_page_score"))
        if score is None:
            score = self._number(seo.get("global_score"))
        if score is None:
            return None
        penalty = min(int(seo.get("critical_issues") or 0) * 3 + int(seo.get("warning_issues") or 0), 30)
        return self._clamp(score - penalty)

    def _geo_health(self, geo: dict[str, Any]) -> float | None:
        score = self._number(geo.get("geo_score")) or self._number(geo.get("global_score"))
        if score is None:
            return None
        penalty = min(int(geo.get("priority_recommendations") or 0) * 3, 25)
        return self._clamp(score - penalty)

    def _search_visibility_health(self, gsc: dict[str, Any], bing: dict[str, Any]) -> float | None:
        scores = []
        for source in (gsc, bing):
            impressions = int(source.get("impressions") or 0)
            if impressions <= 0:
                continue
            ctr = int(source.get("clicks") or 0) / impressions
            position = self._safe_ratio(float(source.get("position_weight") or 0.0), impressions)
            score = self._ctr_score(ctr)
            if position <= 10:
                score += 10
            elif position > 30:
                score -= 15
            scores.append((self._clamp(score), impressions))
        if not scores:
            return None
        total_impressions = sum(weight for _score, weight in scores)
        return round(sum(score * weight for score, weight in scores) / total_impressions, 2)

    def _traffic_health(self, ga4: dict[str, Any], previous_ga4: dict[str, Any] | None) -> float | None:
        sessions = int(ga4.get("sessions") or 0)
        if sessions <= 0:
            return None
        score = 70.0
        previous_sessions = int((previous_ga4 or {}).get("sessions") or 0)
        if previous_sessions > 0:
            delta = (sessions - previous_sessions) / previous_sessions
            if delta > 0:
                score += 10
            elif delta < -0.2:
                score -= 15
        engagement_rate = self._safe_ratio(float(ga4.get("engagement_weight") or 0.0), sessions)
        if engagement_rate >= 0.6:
            score += 10
        elif engagement_rate < 0.3:
            score -= 10
        if float(ga4.get("conversions") or 0.0) > 0:
            score += 10
        return self._clamp(score)

    def _technical_health(self, crawl: dict[str, Any], gsc: dict[str, Any], bing: dict[str, Any]) -> float | None:
        has_data = any((crawl, gsc, bing))
        if not has_data:
            return None
        score = 100.0
        crawl_pages = int(crawl.get("crawl_pages") or crawl.get("pages_crawled") or 0)
        if crawl_pages > 0:
            score -= min((int(crawl.get("pages_failed") or 0) / crawl_pages) * 100, 25)
            score -= min((int(crawl.get("http_error_pages") or 0) / crawl_pages) * 100, 20)
        score -= min(int(gsc.get("index_errors") or 0) * 3, 20)
        score -= min(int(bing.get("crawl_errors") or 0) * 2, 20)
        score -= min((int(gsc.get("sitemap_errors") or 0) + int(bing.get("sitemap_errors") or 0)) * 2, 10)
        return self._clamp(score)

    def _operations_health(self, operations: dict[str, Any], alerts: dict[str, Any]) -> float | None:
        has_data = bool(
            operations.get("total_jobs")
            or alerts.get("total")
            or operations.get("workers")
            or operations.get("critical_alerts")
            or operations.get("warning_alerts")
            or operations.get("period_failed_jobs")
            or operations.get("blocked_jobs")
        )
        if not has_data:
            return None
        score = 100.0
        score -= min(int(alerts.get("critical") or operations.get("critical_alerts") or 0) * 10, 40)
        score -= min(int(alerts.get("warning") or operations.get("warning_alerts") or 0) * 4, 20)
        score -= min(int(operations.get("period_failed_jobs") or 0) * 3, 20)
        score -= min(int(operations.get("blocked_jobs") or 0) * 10, 30)
        workers = operations.get("workers") if isinstance(operations.get("workers"), list) else []
        if not workers and int(operations.get("pending_jobs") or 0) > 0:
            score -= 20
        return self._clamp(score)

    def _component(self, name: str, score: float | None) -> DashboardV2HealthComponent:
        return DashboardV2HealthComponent(
            name=name,
            score=score,
            status=self._health_status(score),
            available=score is not None,
        )

    def _weighted_health(self, weighted: list[tuple[DashboardV2HealthComponent, float]]) -> DashboardV2HealthScore:
        available = [
            (component, weight)
            for component, weight in weighted
            if component.available and component.score is not None
        ]
        if not available:
            return DashboardV2HealthScore(
                components=[component for component, _weight in weighted],
                missing_components=[component.name for component, _weight in weighted],
            )
        weight_sum = sum(weight for _component, weight in available)
        score = round(sum(float(component.score) * weight for component, weight in available) / weight_sum, 2)
        return DashboardV2HealthScore(
            score=score,
            status=self._health_status(score),
            components=[component for component, _weight in weighted],
            available_components=[component.name for component, _weight in weighted if component.available],
            missing_components=[component.name for component, _weight in weighted if not component.available],
        )

    def _seo_kpis(self, raw: dict[str, Any]) -> DashboardV2SeoKpis:
        pages_total = int(raw.get("pages_total") or 0)
        pages_analyzed = int(raw.get("pages_analyzed") or 0)
        return DashboardV2SeoKpis(
            analyses_count=int(raw.get("analyses_count") or 0),
            completed_analyses=int(raw.get("completed_analyses") or 0),
            failed_analyses=int(raw.get("failed_analyses") or 0),
            average_score=self._number(raw.get("average_page_score")),
            global_score=self._number(raw.get("global_score")),
            pages_total=pages_total,
            pages_analyzed=pages_analyzed,
            coverage_rate=self._safe_ratio(pages_analyzed, pages_total) if pages_total else None,
            issues_total=int(raw.get("issues_total") or 0),
            critical_issues=int(raw.get("critical_issues") or 0),
            warning_issues=int(raw.get("warning_issues") or 0),
            latest_analysis_at=raw.get("latest_analysis_at")
            if isinstance(raw.get("latest_analysis_at"), datetime)
            else None,
        )

    def _geo_kpis(self, raw: dict[str, Any]) -> DashboardV2GeoKpis:
        pages_total = int(raw.get("pages_total") or 0)
        pages_analyzed = int(raw.get("pages_analyzed") or 0)
        return DashboardV2GeoKpis(
            analyses_count=int(raw.get("analyses_count") or 0),
            completed_analyses=int(raw.get("completed_analyses") or 0),
            partial_analyses=int(raw.get("partial_analyses") or 0),
            failed_analyses=int(raw.get("failed_analyses") or 0),
            geo_score=self._number(raw.get("geo_score")),
            llm_score=self._number(raw.get("llm_score")),
            global_score=self._number(raw.get("global_score")),
            pages_total=pages_total,
            pages_analyzed=pages_analyzed,
            coverage_rate=self._safe_ratio(pages_analyzed, pages_total) if pages_total else None,
            provider_results_count=int(raw.get("provider_results_count") or 0),
            provider_failed_count=int(raw.get("provider_failed_count") or 0),
            recommendations_count=int(raw.get("recommendations_count") or 0),
            priority_recommendations=int(raw.get("priority_recommendations") or 0),
            latest_analysis_at=raw.get("latest_analysis_at")
            if isinstance(raw.get("latest_analysis_at"), datetime)
            else None,
        )

    def _gsc_kpis(self, raw: dict[str, Any]) -> DashboardV2GscKpis:
        impressions = int(raw.get("impressions") or 0)
        clicks = int(raw.get("clicks") or 0)
        return DashboardV2GscKpis(
            properties_count=int(raw.get("properties_count") or 0),
            active_properties=int(raw.get("active_properties") or 0),
            clicks=clicks,
            impressions=impressions,
            ctr=self._safe_ratio(clicks, impressions) if impressions else None,
            position=self._safe_ratio(float(raw.get("position_weight") or 0.0), impressions) if impressions else None,
            valid_pages=int(raw.get("valid_pages") or 0),
            excluded_pages=int(raw.get("excluded_pages") or 0),
            index_errors=int(raw.get("index_errors") or 0),
            index_warnings=int(raw.get("index_warnings") or 0),
            sitemap_errors=int(raw.get("sitemap_errors") or 0),
            sitemap_warnings=int(raw.get("sitemap_warnings") or 0),
            failed_imports=int(raw.get("failed_imports") or 0),
            latest_import_at=raw.get("latest_import_at") if isinstance(raw.get("latest_import_at"), datetime) else None,
        )

    def _ga4_kpis(self, raw: dict[str, Any]) -> DashboardV2Ga4Kpis:
        sessions = int(raw.get("sessions") or 0)
        return DashboardV2Ga4Kpis(
            properties_count=int(raw.get("properties_count") or 0),
            active_properties=int(raw.get("active_properties") or 0),
            sessions=sessions,
            users=int(raw.get("users") or 0),
            new_users=int(raw.get("new_users") or 0),
            engaged_sessions=int(raw.get("engaged_sessions") or 0),
            screen_page_views=int(raw.get("screen_page_views") or 0),
            average_session_duration=self._safe_ratio(float(raw.get("duration_weight") or 0.0), sessions)
            if sessions
            else None,
            engagement_rate=self._safe_ratio(float(raw.get("engagement_weight") or 0.0), sessions)
            if sessions
            else None,
            conversions=float(raw.get("conversions") or 0.0),
            total_revenue=float(raw.get("total_revenue") or 0.0),
            failed_imports=int(raw.get("failed_imports") or 0),
            latest_import_at=raw.get("latest_import_at") if isinstance(raw.get("latest_import_at"), datetime) else None,
        )

    def _bing_kpis(self, raw: dict[str, Any]) -> DashboardV2BingKpis:
        impressions = int(raw.get("impressions") or 0)
        clicks = int(raw.get("clicks") or 0)
        return DashboardV2BingKpis(
            connections_count=int(raw.get("connections_count") or 0),
            active_connections=int(raw.get("active_connections") or 0),
            sites_count=int(raw.get("sites_count") or 0),
            verified_sites=int(raw.get("verified_sites") or 0),
            clicks=clicks,
            impressions=impressions,
            ctr=self._safe_ratio(clicks, impressions) if impressions else None,
            position=self._safe_ratio(float(raw.get("position_weight") or 0.0), impressions) if impressions else None,
            crawl_errors=int(raw.get("crawl_errors") or 0),
            sitemap_errors=int(raw.get("sitemap_errors") or 0),
            sitemap_warnings=int(raw.get("sitemap_warnings") or 0),
            failed_imports=int(raw.get("failed_imports") or 0),
            latest_import_at=raw.get("latest_import_at") if isinstance(raw.get("latest_import_at"), datetime) else None,
        )

    def _monitoring_kpis(self, raw: dict[str, Any]) -> DashboardV2MonitoringKpis:
        return DashboardV2MonitoringKpis(**{key: raw.get(key, {}) for key in DashboardV2MonitoringKpis.model_fields})

    def _alert_kpis(self, raw: dict[str, Any]) -> DashboardV2AlertKpis:
        return DashboardV2AlertKpis(**{key: raw.get(key, 0) for key in DashboardV2AlertKpis.model_fields})

    def _operations_kpis(self, raw: dict[str, Any]) -> DashboardV2OperationsKpis:
        workers = self._worker_kpis(raw.get("workers", []), raw)
        values = {key: raw.get(key, 0) for key in DashboardV2OperationsKpis.model_fields if key != "workers"}
        values["workers"] = workers
        return DashboardV2OperationsKpis(**values)

    def _worker_kpis(self, workers: list[dict[str, Any]], operations: dict[str, Any]) -> DashboardV2WorkerKpis:
        active_workers = [worker for worker in workers if worker.get("status") != "STOPPED"]
        stopped_workers = [worker for worker in workers if worker.get("status") == "STOPPED"]
        if not workers and int(operations.get("pending_jobs") or 0) + int(operations.get("running_jobs") or 0) > 0:
            worker_status = "attention"
        elif not workers:
            worker_status = "not_configured"
        elif active_workers:
            worker_status = "operational"
        else:
            worker_status = "stopped"
        return DashboardV2WorkerKpis(
            total_workers=len(workers),
            active_workers=len(active_workers),
            stopped_workers=len(stopped_workers),
            status=worker_status,
            last_heartbeat_at=self._latest(*(worker.get("last_heartbeat_at") for worker in workers)),
        )

    def _engine_recommendations(
        self,
        *,
        websites: list[Website],
        filters: DashboardV2Filters,
    ) -> list[DashboardV2Recommendation]:
        """Load RecommendationService results and adapt the historical Dashboard contract."""

        restrict_websites = any(
            value is not None
            for value in (filters.website_id, filters.entity_id, filters.is_active, filters.search)
        )
        website_ids = [website.id for website in websites] if restrict_websites else None
        engine_items: list[RecommendationRead] = []
        page = 1
        while True:
            result = self.recommendation_service.list_recommendations(
                PaginationParams(page=page, page_size=100),
                filters=RecommendationFilters(),
                website_ids=website_ids,
                synchronize=page == 1,
            )
            engine_items.extend(result.items)
            if page >= result.pages:
                break
            page += 1

        enabled_sources = {source.value for source in filters.source}
        items = [
            self._dashboard_recommendation(item)
            for item in engine_items
            if item.status.value in {"OPEN", "ACKNOWLEDGED"}
        ]
        if enabled_sources:
            items = [item for item in items if item.source.value in enabled_sources]
        return self._sort_recommendations(items, None, "asc")

    def _dashboard_recommendation(self, item: RecommendationRead) -> DashboardV2Recommendation:
        source_map = {
            "SEO": (DashboardV2Source.SEO, "SEO Analysis"),
            "GEO": (DashboardV2Source.GEO, "GEO Analysis"),
            "MONITORING": (DashboardV2Source.MONITORING, "Monitoring"),
            "ALERTS": (DashboardV2Source.ALERTS, "Alertes"),
            "GSC": (DashboardV2Source.GSC, "Google Search Console"),
            "GA4": (DashboardV2Source.GA4, "Google Analytics 4"),
            "BING": (DashboardV2Source.BING, "Bing Webmaster Tools"),
        }
        priority_map = {
            RecommendationPriority.CRITICAL: 1,
            RecommendationPriority.HIGH: 2,
            RecommendationPriority.MEDIUM: 3,
            RecommendationPriority.LOW: 4,
        }
        severity_map = {
            RecommendationPriority.CRITICAL: DashboardV2RecommendationSeverity.CRITICAL,
            RecommendationPriority.HIGH: DashboardV2RecommendationSeverity.WARNING,
            RecommendationPriority.MEDIUM: DashboardV2RecommendationSeverity.INFO,
            RecommendationPriority.LOW: DashboardV2RecommendationSeverity.INFO,
        }
        source, target = source_map[item.source.value]
        metadata = item.metadata or {}
        rule_code = str(metadata.get("rule_code") or item.category)
        type_map = {
            "SEO": "seo_critical",
            "GEO": "geo_priority",
            "ALERTS": "active_alert",
            "GSC": "gsc_low_ctr",
            "GA4": "ga4_low_engagement",
            "BING": "bing_crawl_errors" if rule_code == "bing_crawl_error" else rule_code,
        }
        return DashboardV2Recommendation(
            type=type_map.get(item.source.value, rule_code),
            severity=severity_map[item.priority],
            priority=priority_map[item.priority],
            title=item.title,
            message=item.description,
            source=source,
            website_id=item.website_id,
            source_id=item.source_id,
            navigation_target=target,
            created_at=item.created_at,
            website_name=item.website_name,
        )

    def _sources(self, raw: dict[str, Any]) -> list[DashboardV2SourceAvailability]:
        source_map = {
            DashboardV2Source.SEO: raw["seo"],
            DashboardV2Source.GEO: raw["geo"],
            DashboardV2Source.GSC: raw["gsc"],
            DashboardV2Source.GA4: raw["ga4"],
            DashboardV2Source.BING: raw["bing"],
            DashboardV2Source.CRAWL: raw["crawl"],
            DashboardV2Source.MONITORING: raw["monitoring"],
            DashboardV2Source.ALERTS: raw["alerts"],
            DashboardV2Source.ORCHESTRATION: raw["operations"],
        }
        return [
            DashboardV2SourceAvailability(
                source=source,
                available=bool(data),
                status="available" if data else "unavailable",
            )
            for source, data in source_map.items()
        ]

    def _partial_data(self, raw: dict[str, Any]) -> list[str]:
        missing = []
        for availability in self._sources(raw):
            if not availability.available:
                missing.append(availability.source.value)
        return missing

    def _resolve_period(self, filters: DashboardV2Filters) -> DashboardV2ResolvedPeriod:
        today = self._now().date()
        if filters.period == DashboardV2Period.LAST_7_DAYS:
            return DashboardV2ResolvedPeriod(date_from=today - timedelta(days=6), date_to=today, period=filters.period)
        if filters.period == DashboardV2Period.LAST_30_DAYS:
            return DashboardV2ResolvedPeriod(date_from=today - timedelta(days=29), date_to=today, period=filters.period)
        if filters.period == DashboardV2Period.LAST_90_DAYS:
            return DashboardV2ResolvedPeriod(date_from=today - timedelta(days=89), date_to=today, period=filters.period)
        if filters.date_from is None or filters.date_to is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="date_from et date_to sont requis avec period=custom.",
            )
        if filters.date_to < filters.date_from:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="La date de fin doit etre superieure ou egale a la date de debut.",
            )
        return DashboardV2ResolvedPeriod(date_from=filters.date_from, date_to=filters.date_to, period=filters.period)

    def _previous_period(self, period: DashboardV2ResolvedPeriod) -> DashboardV2ResolvedPeriod:
        duration = period.date_to - period.date_from
        previous_to = period.date_from - timedelta(days=1)
        previous_from = previous_to - duration
        return DashboardV2ResolvedPeriod(date_from=previous_from, date_to=previous_to, period=period.period)

    def _normalize_filters(self, filters: DashboardV2Filters) -> DashboardV2Filters:
        return DashboardV2Filters(
            website_id=filters.website_id,
            entity_id=filters.entity_id,
            is_active=filters.is_active,
            date_from=filters.date_from,
            date_to=filters.date_to,
            period=filters.period,
            compare_to_previous=filters.compare_to_previous,
            source=filters.source,
            health_status=filters.health_status,
            search=self._clean(filters.search),
            sort=self._clean(filters.sort),
            order=filters.order,
        )

    def _filters_dict(self, filters: DashboardV2Filters) -> dict[str, Any]:
        return filters.model_dump(mode="json", exclude_none=True)

    def _validate_website_sort(self, sort: str | None) -> None:
        if sort is not None and sort not in WEBSITE_SORT_FIELDS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Champ de tri Dashboard V2 non autorise: {sort}.",
            )

    def _validate_recommendation_sort(self, sort: str | None) -> None:
        if sort is not None and sort not in RECOMMENDATION_SORT_FIELDS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Champ de tri recommandation non autorise: {sort}.",
            )

    def _sort_websites(
        self,
        items: list[DashboardV2WebsiteSummary],
        sort: str | None,
        order: str,
    ) -> list[DashboardV2WebsiteSummary]:
        reverse = order == "desc"
        if sort is None:
            return sorted(
                items,
                key=lambda item: (
                    self._health_rank(item.health_status),
                    -item.active_alerts,
                    self._none_datetime(item.last_activity_at),
                    item.name.lower(),
                ),
            )
        return sorted(items, key=lambda item: self._sort_value(item, sort), reverse=reverse)

    def _sort_recommendations(
        self,
        items: list[DashboardV2Recommendation],
        sort: str | None,
        order: str,
    ) -> list[DashboardV2Recommendation]:
        reverse = order == "desc"
        if sort is None:
            return sorted(items, key=lambda item: (item.priority, self._severity_rank(item.severity), item.title))
        return sorted(items, key=lambda item: self._sort_value(item, sort), reverse=reverse)

    def _trend_points(
        self,
        rows: list[tuple[date, float]],
        granularity: DashboardV2Granularity,
    ) -> list[DashboardV2TrendPoint]:
        grouped: dict[date, list[float]] = defaultdict(list)
        for row_date, value in rows:
            grouped[self._bucket_date(row_date, granularity)].append(value)
        return [
            DashboardV2TrendPoint(date=point_date, value=round(sum(values), 2))
            for point_date, values in sorted(grouped.items())
        ]

    def _bucket_date(self, value: date, granularity: DashboardV2Granularity) -> date:
        if granularity == DashboardV2Granularity.WEEK:
            return value - timedelta(days=value.weekday())
        if granularity == DashboardV2Granularity.MONTH:
            return value.replace(day=1)
        return value

    def _trend_label(self, metric: DashboardV2TrendMetric) -> str:
        return metric.value.replace("_", " ").title()

    def _metric_source(self, metric: DashboardV2TrendMetric) -> DashboardV2Source:
        if metric.value.startswith("seo"):
            return DashboardV2Source.SEO
        if metric.value.startswith("geo"):
            return DashboardV2Source.GEO
        if metric.value.startswith("gsc"):
            return DashboardV2Source.GSC
        if metric.value.startswith("ga4"):
            return DashboardV2Source.GA4
        if metric.value.startswith("bing"):
            return DashboardV2Source.BING
        if metric.value.startswith("alerts"):
            return DashboardV2Source.ALERTS
        return DashboardV2Source.ORCHESTRATION

    def _sum_dicts(self, values: Any) -> dict[str, Any]:
        result: dict[str, Any] = {}
        latest_by_key: dict[str, datetime] = {}
        numeric_counts: dict[str, int] = {}
        for value in values:
            if not isinstance(value, dict):
                continue
            for key, item in value.items():
                if isinstance(item, int | float):
                    result[key] = result.get(key, 0) + item
                    numeric_counts[key] = numeric_counts.get(key, 0) + 1
                elif isinstance(item, datetime):
                    latest_by_key[key] = max(latest_by_key.get(key, item), item)
        for key, value in latest_by_key.items():
            result[key] = value
        for key in ("global_score", "average_page_score", "geo_score", "llm_score"):
            if key in result and numeric_counts.get(key, 0) > 0:
                result[key] = round(float(result[key]) / numeric_counts[key], 2)
        return result

    def _health_status(self, score: float | None) -> DashboardV2HealthStatus:
        if score is None:
            return DashboardV2HealthStatus.UNAVAILABLE
        if score <= 49:
            return DashboardV2HealthStatus.CRITICAL
        if score <= 69:
            return DashboardV2HealthStatus.WARNING
        if score <= 84:
            return DashboardV2HealthStatus.GOOD
        return DashboardV2HealthStatus.EXCELLENT

    def _health_rank(self, value: DashboardV2HealthStatus) -> int:
        order = {
            DashboardV2HealthStatus.CRITICAL: 0,
            DashboardV2HealthStatus.WARNING: 1,
            DashboardV2HealthStatus.GOOD: 2,
            DashboardV2HealthStatus.EXCELLENT: 3,
            DashboardV2HealthStatus.UNAVAILABLE: 4,
        }
        return order[value]

    def _severity_rank(self, value: DashboardV2RecommendationSeverity) -> int:
        order = {
            DashboardV2RecommendationSeverity.CRITICAL: 0,
            DashboardV2RecommendationSeverity.WARNING: 1,
            DashboardV2RecommendationSeverity.INFO: 2,
        }
        return order[value]

    def _sort_value(self, item: Any, field_name: str) -> Any:
        value = getattr(item, field_name)
        if isinstance(value, datetime):
            return value
        if value is None:
            return ""
        if isinstance(value, str):
            return value.lower()
        if hasattr(value, "value"):
            return value.value
        return value

    def _ctr_score(self, ctr: float) -> float:
        if ctr >= 0.05:
            return 100.0
        if ctr >= 0.02:
            return 60.0 + ((ctr - 0.02) / 0.03 * 40.0)
        return 40.0

    def _safe_ratio(self, numerator: float, denominator: float) -> float:
        if denominator <= 0:
            return 0.0
        return numerator / denominator

    def _number(self, value: Any) -> float | None:
        if isinstance(value, int | float):
            return float(value)
        return None

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(value, 100.0)), 2)

    def _latest(self, *values: Any) -> datetime | None:
        dates = [value for value in values if isinstance(value, datetime)]
        return max(dates) if dates else None

    def _none_datetime(self, value: datetime | None) -> datetime:
        return value or datetime.min.replace(tzinfo=UTC)

    def _clean(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _datetime_start(self, value: date) -> datetime:
        return datetime.combine(value, time.min, tzinfo=UTC)

    def _datetime_end(self, value: date) -> datetime:
        return datetime.combine(value, time.max, tzinfo=UTC)

    def _now(self) -> datetime:
        value = self.now_provider()
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
