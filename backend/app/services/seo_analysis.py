"""Business service for SEO analyses."""

from __future__ import annotations

from datetime import UTC, datetime
from math import ceil

from fastapi import HTTPException, status

from backend.app.models import CrawlPage
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.seo_analysis import SeoAnalysisRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.seo_analysis import (
    SeoAnalysisCreate,
    SeoAnalysisList,
    SeoAnalysisRead,
    SeoAnalysisStatus,
    SeoAnalysisUpdate,
)
from backend.app.seo import SeoAnalysisEngine
from backend.app.seo.models import KnownCrawlPage, SeoAnalysisContext, SeoIssue, SeoPageInput


class SeoAnalysisService:
    """Manage SEO analysis lifecycle without running the SEO engine."""

    def __init__(
        self,
        repository: SeoAnalysisRepository,
        crawl_repository: CrawlRepository,
        *,
        engine: SeoAnalysisEngine | None = None,
    ) -> None:
        self.repository = repository
        self.crawl_repository = crawl_repository
        self.engine = engine or SeoAnalysisEngine()

    def list(self, params: PaginationParams) -> SeoAnalysisList:
        """Return paginated SEO analyses."""

        items, total = self.repository.list(params)
        return SeoAnalysisList(
            items=[SeoAnalysisRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get(self, analysis_id: int) -> SeoAnalysisRead:
        """Return one SEO analysis."""

        analysis = self.repository.get(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse SEO introuvable.")
        return SeoAnalysisRead.model_validate(analysis)

    def create(self, payload: SeoAnalysisCreate) -> SeoAnalysisRead:
        """Create a pending SEO analysis linked to an existing crawl."""

        crawl = self.crawl_repository.get(payload.crawl_id)
        if crawl is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl introuvable.")

        analysis = self.repository.create(
            {
                "crawl_session_id": payload.crawl_id,
                "status": SeoAnalysisStatus.PENDING,
                "progress_percent": 0,
                "global_score": None,
                "pages_total": self.repository.count_crawl_pages(payload.crawl_id),
                "pages_analyzed": 0,
                "issues_total": 0,
                "error_message": None,
                "started_at": None,
                "completed_at": None,
            },
        )
        return SeoAnalysisRead.model_validate(analysis)

    def update_state(self, analysis_id: int, payload: SeoAnalysisUpdate) -> SeoAnalysisRead:
        """Update execution state for a SEO analysis."""

        analysis = self.repository.get(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse SEO introuvable.")

        data = payload.model_dump(exclude_unset=True)
        status_value = data.get("status")
        if status_value == SeoAnalysisStatus.RUNNING:
            data.setdefault("started_at", datetime.now(UTC))
        if status_value in {SeoAnalysisStatus.COMPLETED, SeoAnalysisStatus.FAILED}:
            data.setdefault("completed_at", datetime.now(UTC))
            if status_value == SeoAnalysisStatus.COMPLETED:
                data.setdefault("progress_percent", 100)

        updated = self.repository.update(analysis, data)
        return SeoAnalysisRead.model_validate(updated)

    def run(self, analysis_id: int) -> SeoAnalysisRead:
        """Run deterministic SEO analysis from persisted crawl data."""

        analysis = self.repository.get(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse SEO introuvable.")

        self.repository.clear_results(analysis.id)
        started = self.repository.update(
            analysis,
            {
                "status": SeoAnalysisStatus.RUNNING,
                "progress_percent": 0,
                "pages_analyzed": 0,
                "issues_total": 0,
                "error_message": None,
                "started_at": datetime.now(UTC),
                "completed_at": None,
            },
        )
        pages = self.repository.list_crawl_pages(started.crawl_session_id)
        context = self._context(pages)
        issues_total = 0

        try:
            for index, page in enumerate(pages, start=1):
                result = self.engine.analyze_page(self._page_input(page), context)
                page_analysis = self.repository.create_page_analysis(
                    {
                        "seo_analysis_id": started.id,
                        "crawl_page_id": page.id,
                        "status": result.status,
                        "score": None,
                        "issues_count": len(result.issues),
                        "error_message": None,
                        "analyzed_at": datetime.now(UTC),
                    },
                )
                for seo_issue in result.issues:
                    self.repository.create_issue(self._issue_data(started.id, page.id, page_analysis.id, seo_issue))
                issues_total += len(result.issues)
                self.repository.update(
                    started,
                    {
                        "pages_analyzed": index,
                        "issues_total": issues_total,
                        "progress_percent": int(index / len(pages) * 100) if pages else 100,
                    },
                )
        except Exception as exc:  # noqa: BLE001
            failed = self.repository.update(
                started,
                {
                    "status": SeoAnalysisStatus.FAILED,
                    "error_message": str(exc),
                    "completed_at": datetime.now(UTC),
                },
            )
            return SeoAnalysisRead.model_validate(failed)

        completed = self.repository.update(
            started,
            {
                "status": SeoAnalysisStatus.COMPLETED,
                "progress_percent": 100,
                "pages_total": len(pages),
                "pages_analyzed": len(pages),
                "issues_total": issues_total,
                "completed_at": datetime.now(UTC),
            },
        )
        return SeoAnalysisRead.model_validate(completed)

    def delete(self, analysis_id: int) -> None:
        """Delete one SEO analysis."""

        analysis = self.repository.get(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse SEO introuvable.")
        self.repository.delete(analysis)

    def _context(self, pages: list[CrawlPage]) -> SeoAnalysisContext:
        known_pages: dict[str, KnownCrawlPage] = {}
        for page in pages:
            known_pages[page.normalized_url.rstrip("/")] = KnownCrawlPage(
                normalized_url=page.normalized_url,
                status_code=page.status_code,
            )
            if page.final_normalized_url:
                known_pages[page.final_normalized_url.rstrip("/")] = KnownCrawlPage(
                    normalized_url=page.final_normalized_url,
                    status_code=page.status_code,
                )
        return SeoAnalysisContext(known_pages=known_pages)

    def _page_input(self, page: CrawlPage) -> SeoPageInput:
        return SeoPageInput(
            id=page.id,
            url=page.url,
            normalized_url=page.normalized_url,
            final_url=page.final_url,
            final_normalized_url=page.final_normalized_url,
            status_code=page.status_code,
            content_type=page.content_type,
            raw_html=page.raw_html,
            response_time_ms=page.response_time_ms,
            is_redirect=page.is_redirect,
            redirect_url=page.redirect_url,
            redirect_count=page.redirect_count,
        )

    def _issue_data(
        self,
        analysis_id: int,
        crawl_page_id: int,
        page_analysis_id: int,
        seo_issue: SeoIssue,
    ) -> dict[str, object]:
        return {
            "seo_analysis_id": analysis_id,
            "seo_page_analysis_id": page_analysis_id,
            "crawl_page_id": crawl_page_id,
            "family": seo_issue.family,
            "criterion": seo_issue.criterion,
            "severity": seo_issue.severity,
            "code": seo_issue.code,
            "message": seo_issue.message,
            "details": seo_issue.details,
        }
