"""Business service for GEO analyses."""

from __future__ import annotations

from datetime import UTC, datetime
from math import ceil
from typing import Any

from fastapi import HTTPException, status

from backend.app.models import CrawlPage, SeoAnalysisIssue, SeoPageAnalysis
from backend.app.repositories.geo_analysis import GeoAnalysisRepository
from backend.app.schemas.geo_analysis import GeoAnalysisCreate, GeoAnalysisList, GeoAnalysisRead, GeoAnalysisStatus
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.geo.engine import GeoAnalysisEngine, GeoPageWorkItem
from backend.app.services.geo.provider import PROVIDER_STATUS_COMPLETED


class GeoAnalysisService:
    """Manage GEO analysis lifecycle and persistence."""

    def __init__(
        self,
        repository: GeoAnalysisRepository,
        *,
        engine: GeoAnalysisEngine | None = None,
    ) -> None:
        self.repository = repository
        self.engine = engine or GeoAnalysisEngine()

    def list(self, params: PaginationParams) -> GeoAnalysisList:
        """Return paginated GEO analyses."""

        items, total = self.repository.list(params)
        return GeoAnalysisList(
            items=[GeoAnalysisRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get(self, analysis_id: int) -> GeoAnalysisRead:
        """Return one GEO analysis with provider results and recommendations."""

        analysis = self.repository.get_with_details(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse GEO introuvable.")
        return GeoAnalysisRead.model_validate(analysis)

    def create(self, payload: GeoAnalysisCreate) -> GeoAnalysisRead:
        """Create a pending GEO analysis linked to an existing SEO analysis."""

        seo_analysis = self.repository.get_seo_analysis(payload.seo_analysis_id)
        if seo_analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse SEO introuvable.")
        if seo_analysis.status != "COMPLETED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="L'analyse SEO doit etre terminee avant de creer une analyse GEO.",
            )

        providers = self._providers(payload.providers)
        analysis = self.repository.create(
            {
                "seo_analysis_id": seo_analysis.id,
                "crawl_session_id": seo_analysis.crawl_session_id,
                "status": GeoAnalysisStatus.PENDING,
                "progress_percent": 0,
                "geo_score": None,
                "llm_score": None,
                "global_score": None,
                "providers_requested": providers,
                "pages_total": self.repository.count_seo_pages(seo_analysis.id),
                "pages_analyzed": 0,
                "provider_results_count": 0,
                "recommendations_count": 0,
                "summary": None,
                "error_message": None,
                "started_at": None,
                "completed_at": None,
            },
        )
        return self.get(analysis.id)

    def run(self, analysis_id: int) -> GeoAnalysisRead:
        """Run GEO analysis from persisted crawl HTML and SEO results."""

        analysis = self.repository.get(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse GEO introuvable.")

        self.repository.clear_results(analysis.id)
        started = self.repository.update(
            analysis,
            {
                "status": GeoAnalysisStatus.RUNNING,
                "progress_percent": 0,
                "geo_score": None,
                "llm_score": None,
                "global_score": None,
                "provider_results_count": 0,
                "recommendations_count": 0,
                "summary": None,
                "error_message": None,
                "started_at": datetime.now(UTC),
                "completed_at": None,
            },
        )

        work_items = self._work_items(started.seo_analysis_id)
        try:
            engine_result = self.engine.run(work_items, list(started.providers_requested))
            calculated_results = []
            recommendations_count = 0
            completed_provider_results = 0
            for execution in engine_result.executions:
                provider_result = self.repository.create_provider_result(
                    {
                        "geo_analysis_id": started.id,
                        "crawl_page_id": execution.crawl_page_id,
                        "provider_name": execution.response.provider_name,
                        "model_name": execution.response.model_name,
                        "status": execution.response.status,
                        "prompt": execution.prompt,
                        "raw_response": execution.response.raw_response,
                        "normalized_response": execution.response.normalized_response,
                        "error_message": execution.response.error_message,
                        "duration_ms": execution.response.duration_ms,
                    },
                )
                if execution.response.status == PROVIDER_STATUS_COMPLETED:
                    completed_provider_results += 1
                calculated_results.append(execution.calculated)
                for recommendation in execution.calculated.recommendations:
                    self.repository.create_recommendation(
                        {
                            "geo_analysis_id": started.id,
                            "provider_result_id": provider_result.id,
                            "crawl_page_id": execution.crawl_page_id,
                            "recommendation_type": recommendation.recommendation_type,
                            "severity": recommendation.severity,
                            "priority": recommendation.priority,
                            "title": recommendation.title,
                            "description": recommendation.description,
                            "source": recommendation.source,
                            "impact_score": recommendation.impact_score,
                        },
                    )
                    recommendations_count += 1

            scores = self.engine.score_calculator.aggregate(calculated_results)
            final_status = self._final_status(
                total_provider_results=len(engine_result.executions),
                completed_provider_results=completed_provider_results,
            )
            self.repository.update(
                started,
                {
                    "status": final_status,
                    "progress_percent": 100,
                    "geo_score": scores.geo_score,
                    "llm_score": scores.llm_score,
                    "global_score": scores.global_score,
                    "pages_total": len(work_items),
                    "pages_analyzed": len({execution.crawl_page_id for execution in engine_result.executions}),
                    "provider_results_count": len(engine_result.executions),
                    "recommendations_count": recommendations_count,
                    "summary": scores.summary,
                    "completed_at": datetime.now(UTC),
                },
            )
        except Exception as exc:  # noqa: BLE001
            self.repository.update(
                started,
                {
                    "status": GeoAnalysisStatus.FAILED,
                    "error_message": str(exc),
                    "completed_at": datetime.now(UTC),
                },
            )
        return self.get(started.id)

    def delete(self, analysis_id: int) -> None:
        """Delete one GEO analysis."""

        analysis = self.repository.get(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse GEO introuvable.")
        self.repository.delete(analysis)

    def _work_items(self, seo_analysis_id: int) -> list[GeoPageWorkItem]:
        work_items: list[GeoPageWorkItem] = []
        for page, seo_page in self.repository.list_pages_for_seo_analysis(seo_analysis_id):
            issues = self.repository.list_issues_for_page(seo_analysis_id, page.id)
            work_items.append(
                GeoPageWorkItem(
                    crawl_page_id=page.id,
                    page=self._page_data(page),
                    raw_html=page.raw_html,
                    seo_page_analysis=self._seo_page_data(seo_page),
                    seo_issues=[self._issue_data(issue) for issue in issues],
                    seo_score=seo_page.score if seo_page else None,
                ),
            )
        return work_items

    def _providers(self, providers: list[str]) -> list[str]:
        normalized = []
        for provider in providers:
            value = provider.strip().lower()
            if value and value not in normalized:
                normalized.append(value)
        if not normalized:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Aucun provider GEO valide.")
        return normalized

    def _final_status(self, *, total_provider_results: int, completed_provider_results: int) -> GeoAnalysisStatus:
        if total_provider_results == 0:
            return GeoAnalysisStatus.COMPLETED
        if completed_provider_results == total_provider_results:
            return GeoAnalysisStatus.COMPLETED
        return GeoAnalysisStatus.PARTIAL

    def _page_data(self, page: CrawlPage) -> dict[str, Any]:
        return {
            "id": page.id,
            "url": page.url,
            "normalized_url": page.normalized_url,
            "final_url": page.final_url,
            "final_normalized_url": page.final_normalized_url,
            "status_code": page.status_code,
            "content_type": page.content_type,
            "response_time_ms": page.response_time_ms,
            "is_redirect": page.is_redirect,
            "redirect_count": page.redirect_count,
        }

    def _seo_page_data(self, seo_page: SeoPageAnalysis | None) -> dict[str, Any] | None:
        if seo_page is None:
            return None
        return {
            "id": seo_page.id,
            "status": seo_page.status,
            "score": seo_page.score,
            "issues_count": seo_page.issues_count,
        }

    def _issue_data(self, issue: SeoAnalysisIssue) -> dict[str, Any]:
        return {
            "family": issue.family,
            "criterion": issue.criterion,
            "severity": issue.severity,
            "code": issue.code,
            "message": issue.message,
            "details": issue.details,
        }
