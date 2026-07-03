"""Business service for SEO analyses."""

from datetime import UTC, datetime
from math import ceil

from fastapi import HTTPException, status

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


class SeoAnalysisService:
    """Manage SEO analysis lifecycle without running the SEO engine."""

    def __init__(self, repository: SeoAnalysisRepository, crawl_repository: CrawlRepository) -> None:
        self.repository = repository
        self.crawl_repository = crawl_repository

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

    def delete(self, analysis_id: int) -> None:
        """Delete one SEO analysis."""

        analysis = self.repository.get(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse SEO introuvable.")
        self.repository.delete(analysis)

