"""Business service for the SEO/GEO dashboard."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from backend.app.models import CrawlPage, CrawlSession, GeoAnalysis, GeoProviderResult, GeoRecommendation, SeoAnalysis
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.geo_analysis import GeoAnalysisRepository
from backend.app.repositories.seo_analysis import SeoAnalysisRepository
from backend.app.schemas.dashboard import (
    DashboardComparisonPage,
    DashboardComparisonSummary,
    DashboardCrawlSummary,
    DashboardGeoRecommendationItem,
    DashboardGeoSummary,
    DashboardOverview,
    DashboardPageMetric,
    DashboardPriorityPage,
    DashboardScoreDistributionBucket,
    DashboardSeoIssueItem,
    DashboardSeoSummary,
)

CRITICAL_SEVERITIES = {"critical", "major"}
WARNING_SEVERITIES = {"medium", "minor", "warning"}
SCORE_BUCKETS = (
    ("Faible", 0, 49),
    ("Moyen", 50, 74),
    ("Bon", 75, 89),
    ("Excellent", 90, 100),
)


class DashboardService:
    """Aggregate persisted crawl, SEO and GEO data for dashboard restitution."""

    def __init__(
        self,
        crawl_repository: CrawlRepository,
        seo_repository: SeoAnalysisRepository,
        geo_repository: GeoAnalysisRepository,
    ) -> None:
        self.crawl_repository = crawl_repository
        self.seo_repository = seo_repository
        self.geo_repository = geo_repository

    def overview(
        self,
        *,
        website_id: int | None = None,
        crawl_id: int | None = None,
        seo_analysis_id: int | None = None,
        geo_analysis_id: int | None = None,
    ) -> DashboardOverview:
        """Return one SEO/GEO dashboard overview from persisted data only."""

        crawl = self._resolve_crawl(website_id=website_id, crawl_id=crawl_id)
        seo_analysis = self._resolve_seo_analysis(seo_analysis_id, crawl)
        if crawl is None and seo_analysis is not None:
            crawl = self.crawl_repository.get(seo_analysis.crawl_session_id)
        geo_analysis = self._resolve_geo_analysis(geo_analysis_id, crawl, seo_analysis)
        if crawl is None and geo_analysis is not None:
            crawl = self.crawl_repository.get(geo_analysis.crawl_session_id)
        if seo_analysis is None and geo_analysis is not None:
            seo_analysis = self.seo_repository.get(geo_analysis.seo_analysis_id)

        seo_pages = self._seo_pages(seo_analysis)
        seo_issues = self.seo_repository.list_issues_for_analysis(seo_analysis.id) if seo_analysis else []
        geo_results = self._geo_results(geo_analysis)
        geo_recommendations = self._geo_recommendations(geo_analysis)

        seo_scores = {page.id: score for page, score in seo_pages if score is not None}
        geo_scores = self._geo_scores_by_page(geo_results)

        return DashboardOverview(
            crawl=self._crawl_summary(crawl),
            seo=self._seo_summary(seo_pages, seo_issues),
            geo=self._geo_summary(geo_analysis, geo_results, geo_recommendations),
            priority_pages=self._priority_pages(seo_pages, seo_issues, geo_scores, geo_recommendations),
            comparison=self._comparison(seo_pages, geo_scores),
            seo_score_distribution=self._distribution(seo_scores.values()),
            geo_score_distribution=self._distribution(
                geo_scores.values() if geo_scores else [geo_analysis.geo_score if geo_analysis else None],
            ),
        )

    def _resolve_crawl(self, *, website_id: int | None, crawl_id: int | None) -> CrawlSession | None:
        if crawl_id is not None:
            return self.crawl_repository.get(crawl_id)
        return self.crawl_repository.get_latest(website_id)

    def _resolve_seo_analysis(self, analysis_id: int | None, crawl: CrawlSession | None) -> SeoAnalysis | None:
        if analysis_id is not None:
            return self.seo_repository.get(analysis_id)
        return self.seo_repository.get_latest_completed(crawl.id if crawl else None)

    def _resolve_geo_analysis(
        self,
        analysis_id: int | None,
        crawl: CrawlSession | None,
        seo_analysis: SeoAnalysis | None,
    ) -> GeoAnalysis | None:
        if analysis_id is not None:
            return self.geo_repository.get(analysis_id)
        return self.geo_repository.get_latest_completed_or_partial(
            crawl_session_id=crawl.id if crawl else None,
            seo_analysis_id=seo_analysis.id if seo_analysis else None,
        )

    def _crawl_summary(self, crawl: CrawlSession | None) -> DashboardCrawlSummary:
        if crawl is None:
            return DashboardCrawlSummary()
        return DashboardCrawlSummary(
            crawled_pages_count=self.crawl_repository.count_pages_for_session(crawl.id),
            failed_pages_count=self.crawl_repository.count_failed_pages_for_session(crawl.id),
            latest_crawl_status=crawl.status,
            latest_crawl_date=crawl.finished_at or crawl.started_at or crawl.created_at,
        )

    def _seo_pages(self, seo_analysis: SeoAnalysis | None) -> list[tuple[CrawlPage, float | None]]:
        if seo_analysis is None:
            return []
        return [
            (page, self._float_or_none(page_analysis.score))
            for page_analysis, page in self.seo_repository.list_page_analyses_with_pages(seo_analysis.id)
        ]

    def _seo_summary(self, pages: list[tuple[CrawlPage, float | None]], issues: list[object]) -> DashboardSeoSummary:
        scores = [(page, score) for page, score in pages if score is not None]
        severities = Counter(str(getattr(issue, "severity", "") or "").lower() for issue in issues)
        return DashboardSeoSummary(
            average_score=self._average([score for _, score in scores]),
            best_page=self._page_metric(max(scores, key=lambda item: item[1]) if scores else None),
            worst_page=self._page_metric(min(scores, key=lambda item: item[1]) if scores else None),
            analyzed_pages_count=len(pages),
            critical_errors_count=sum(severities[severity] for severity in CRITICAL_SEVERITIES),
            warnings_count=sum(severities[severity] for severity in WARNING_SEVERITIES),
            information_count=sum(
                count
                for severity, count in severities.items()
                if severity not in CRITICAL_SEVERITIES and severity not in WARNING_SEVERITIES
            ),
            top_issues=self._top_seo_issues(issues),
        )

    def _geo_results(self, geo_analysis: GeoAnalysis | None) -> list[tuple[GeoProviderResult, CrawlPage | None]]:
        if geo_analysis is None:
            return []
        return self.geo_repository.list_provider_results_with_pages(geo_analysis.id)

    def _geo_recommendations(
        self,
        geo_analysis: GeoAnalysis | None,
    ) -> list[tuple[GeoRecommendation, CrawlPage | None]]:
        if geo_analysis is None:
            return []
        return self.geo_repository.list_recommendations_with_pages(geo_analysis.id)

    def _geo_summary(
        self,
        geo_analysis: GeoAnalysis | None,
        results: list[tuple[GeoProviderResult, CrawlPage | None]],
        recommendations: list[tuple[GeoRecommendation, CrawlPage | None]],
    ) -> DashboardGeoSummary:
        scores_by_page = self._geo_scores_by_page(results)
        page_lookup = {page.id: page for _, page in results if page is not None}
        page_scores = [
            (page_lookup.get(page_id), score)
            for page_id, score in scores_by_page.items()
            if page_lookup.get(page_id) is not None
        ]
        return DashboardGeoSummary(
            average_score=self._average(scores_by_page.values())
            if scores_by_page
            else self._float_or_none(geo_analysis.geo_score if geo_analysis else None),
            best_page=self._page_metric(max(page_scores, key=lambda item: item[1]) if page_scores else None),
            worst_page=self._page_metric(min(page_scores, key=lambda item: item[1]) if page_scores else None),
            analyses_count=1 if geo_analysis is not None else 0,
            top_recommendations=self._top_geo_recommendations(recommendations),
        )

    def _geo_scores_by_page(
        self,
        results: list[tuple[GeoProviderResult, CrawlPage | None]],
    ) -> dict[int, float]:
        page_scores: dict[int, list[float]] = defaultdict(list)
        for result, page in results:
            if page is None:
                continue
            score = self._geo_score_from_response(result.normalized_response)
            if score is not None:
                page_scores[page.id].append(score)
        return {page_id: round(mean(values), 2) for page_id, values in page_scores.items() if values}

    def _priority_pages(
        self,
        seo_pages: list[tuple[CrawlPage, float | None]],
        seo_issues: list[object],
        geo_scores: dict[int, float],
        geo_recommendations: list[tuple[GeoRecommendation, CrawlPage | None]],
    ) -> list[DashboardPriorityPage]:
        critical_by_page: Counter[int] = Counter()
        for issue in seo_issues:
            severity = str(getattr(issue, "severity", "") or "").lower()
            page_id = getattr(issue, "crawl_page_id", None)
            if page_id is not None and severity in CRITICAL_SEVERITIES:
                critical_by_page[int(page_id)] += 1

        recommendations_by_page: Counter[int] = Counter()
        for recommendation, page in geo_recommendations:
            if page is not None and recommendation.priority <= 2:
                recommendations_by_page[page.id] += 1

        page_lookup = {page.id: page for page, _ in seo_pages}
        page_ids = set(page_lookup) | set(geo_scores) | set(critical_by_page) | set(recommendations_by_page)
        priority_pages: list[DashboardPriorityPage] = []
        for page_id in page_ids:
            page = page_lookup.get(page_id)
            seo_score = next((score for current_page, score in seo_pages if current_page.id == page_id), None)
            geo_score = geo_scores.get(page_id)
            critical_count = critical_by_page[page_id]
            recommendation_count = recommendations_by_page[page_id]
            priority_score = self._priority_score(seo_score, geo_score, critical_count, recommendation_count)
            if priority_score <= 0:
                continue
            priority_pages.append(
                DashboardPriorityPage(
                    crawl_page_id=page_id if page_id else None,
                    url=page.url if page is not None else None,
                    seo_score=seo_score,
                    geo_score=geo_score,
                    critical_issues_count=critical_count,
                    recommendations_count=recommendation_count,
                    priority_score=priority_score,
                    reason=self._priority_reason(seo_score, geo_score, critical_count, recommendation_count),
                ),
            )
        return sorted(priority_pages, key=lambda item: item.priority_score, reverse=True)[:10]

    def _comparison(
        self,
        seo_pages: list[tuple[CrawlPage, float | None]],
        geo_scores: dict[int, float],
    ) -> DashboardComparisonSummary:
        seo_scores = {page.id: score for page, score in seo_pages if score is not None}
        common_page_ids = set(seo_scores) & set(geo_scores)
        pages: list[DashboardComparisonPage] = []
        for page, seo_score in seo_pages:
            if seo_score is None or page.id not in common_page_ids:
                continue
            geo_score = geo_scores[page.id]
            gap = round(seo_score - geo_score, 2)
            pages.append(
                DashboardComparisonPage(
                    crawl_page_id=page.id,
                    url=page.url,
                    seo_score=seo_score,
                    geo_score=geo_score,
                    gap=gap,
                    interpretation=self._comparison_interpretation(seo_score, geo_score),
                ),
            )
        gaps = [page.gap for page in pages if page.gap is not None]
        return DashboardComparisonSummary(
            average_seo_score=self._average(seo_scores.values()),
            average_geo_score=self._average(geo_scores.values()),
            average_gap=self._average(gaps),
            pages=sorted(pages, key=lambda item: abs(item.gap or 0), reverse=True)[:10],
        )

    def _top_seo_issues(self, issues: list[object]) -> list[DashboardSeoIssueItem]:
        grouped: dict[tuple[str, str, str, str], int] = Counter()
        for issue in issues:
            key = (
                str(getattr(issue, "code", "") or ""),
                str(getattr(issue, "severity", "") or ""),
                str(getattr(issue, "family", "") or ""),
                str(getattr(issue, "message", "") or ""),
            )
            grouped[key] += 1
        items = [
            DashboardSeoIssueItem(code=code, severity=severity, family=family, message=message, count=count)
            for (code, severity, family, message), count in grouped.items()
        ]
        return sorted(items, key=lambda item: item.count, reverse=True)[:10]

    def _top_geo_recommendations(
        self,
        recommendations: list[tuple[GeoRecommendation, CrawlPage | None]],
    ) -> list[DashboardGeoRecommendationItem]:
        items = [
            DashboardGeoRecommendationItem(
                title=recommendation.title,
                recommendation_type=recommendation.recommendation_type,
                severity=recommendation.severity,
                priority=recommendation.priority,
                source=recommendation.source,
                crawl_page_id=page.id if page is not None else recommendation.crawl_page_id,
                url=page.url if page is not None else None,
            )
            for recommendation, page in recommendations
        ]
        return sorted(items, key=lambda item: (item.priority, item.severity))[:10]

    def _distribution(self, scores: Any) -> list[DashboardScoreDistributionBucket]:
        buckets = [
            DashboardScoreDistributionBucket(label=label, min_score=min_score, max_score=max_score, count=0)
            for label, min_score, max_score in SCORE_BUCKETS
        ]
        for raw_score in scores:
            score = self._float_or_none(raw_score)
            if score is None:
                continue
            for bucket in buckets:
                if bucket.min_score <= score <= bucket.max_score:
                    bucket.count += 1
                    break
        return buckets

    def _page_metric(self, item: tuple[CrawlPage | None, float] | None) -> DashboardPageMetric | None:
        if item is None:
            return None
        page, score = item
        return DashboardPageMetric(
            crawl_page_id=page.id if page is not None else None,
            url=page.url if page is not None else None,
            score=score,
        )

    def _geo_score_from_response(self, response: dict[str, Any] | None) -> float | None:
        if not isinstance(response, dict):
            return None
        direct_score = self._float_or_none(response.get("geo_score"))
        if direct_score is not None:
            return direct_score
        signals = response.get("geo_signals")
        if not isinstance(signals, dict):
            return None
        values = [float(value) for value in signals.values() if isinstance(value, int | float)]
        return round(mean(values), 2) if values else None

    def _priority_score(
        self,
        seo_score: float | None,
        geo_score: float | None,
        critical_count: int,
        recommendation_count: int,
    ) -> float:
        score = 0.0
        if seo_score is not None:
            score += max(0.0, 100.0 - seo_score) * 0.4
        if geo_score is not None:
            score += max(0.0, 100.0 - geo_score) * 0.4
        score += critical_count * 10
        score += recommendation_count * 5
        return round(score, 2)

    def _priority_reason(
        self,
        seo_score: float | None,
        geo_score: float | None,
        critical_count: int,
        recommendation_count: int,
    ) -> str:
        reasons = []
        if seo_score is not None and seo_score < 70:
            reasons.append("score SEO faible")
        if geo_score is not None and geo_score < 70:
            reasons.append("score GEO faible")
        if critical_count:
            reasons.append(f"{critical_count} probleme(s) critique(s)")
        if recommendation_count:
            reasons.append(f"{recommendation_count} recommandation(s) prioritaire(s)")
        return ", ".join(reasons) if reasons else "page a surveiller"

    def _comparison_interpretation(self, seo_score: float, geo_score: float) -> str:
        if seo_score >= 75 and geo_score < 70:
            return "SEO solide, GEO a renforcer"
        if seo_score < 70 and geo_score >= 75:
            return "GEO correct, SEO technique a corriger"
        if seo_score < 70 and geo_score < 70:
            return "SEO et GEO prioritaires"
        return "SEO et GEO alignes"

    def _average(self, values: Any) -> float | None:
        numeric_values = [float(value) for value in values if value is not None]
        if not numeric_values:
            return None
        return round(mean(numeric_values), 2)

    def _float_or_none(self, value: Any) -> float | None:
        if isinstance(value, int | float):
            return float(value)
        return None
