"""Repository for GEO analysis data."""

from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models import (
    CrawlPage,
    GeoAnalysis,
    GeoProviderResult,
    GeoRecommendation,
    SeoAnalysis,
    SeoAnalysisIssue,
    SeoPageAnalysis,
)
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class GeoAnalysisRepository(BaseRepository[GeoAnalysis]):
    """Encapsulate persistence for GEO analyses."""

    search_fields = ("status", "summary")

    def __init__(self, db: Session) -> None:
        super().__init__(db, GeoAnalysis)

    def get_with_details(self, analysis_id: int) -> GeoAnalysis | None:
        """Return one GEO analysis with provider results and recommendations."""

        statement = (
            select(GeoAnalysis)
            .options(selectinload(GeoAnalysis.provider_results), selectinload(GeoAnalysis.recommendations))
            .where(GeoAnalysis.id == analysis_id)
        )
        return self.db.scalar(statement)

    def get_seo_analysis(self, seo_analysis_id: int) -> SeoAnalysis | None:
        """Return the SEO analysis used as GEO source."""

        return self.db.get(SeoAnalysis, seo_analysis_id)

    def get_latest_completed_or_partial(
        self,
        *,
        crawl_session_id: int | None = None,
        seo_analysis_id: int | None = None,
    ) -> GeoAnalysis | None:
        """Return the latest usable GEO analysis."""

        statement = select(GeoAnalysis).where(GeoAnalysis.status.in_(("COMPLETED", "PARTIAL")))
        if crawl_session_id is not None:
            statement = statement.where(GeoAnalysis.crawl_session_id == crawl_session_id)
        if seo_analysis_id is not None:
            statement = statement.where(GeoAnalysis.seo_analysis_id == seo_analysis_id)
        statement = statement.order_by(GeoAnalysis.id.desc()).limit(1)
        return self.db.scalar(statement)

    def count_seo_pages(self, seo_analysis_id: int) -> int:
        """Return number of page analyses attached to one SEO analysis."""

        statement = (
            select(func.count())
            .select_from(SeoPageAnalysis)
            .where(SeoPageAnalysis.seo_analysis_id == seo_analysis_id)
        )
        return int(self.db.scalar(statement) or 0)

    def list_pages_for_seo_analysis(self, seo_analysis_id: int) -> list[tuple[CrawlPage, SeoPageAnalysis | None]]:
        """Return crawl pages with their SEO page analysis for one SEO analysis."""

        statement = (
            select(CrawlPage, SeoPageAnalysis)
            .join(SeoPageAnalysis, SeoPageAnalysis.crawl_page_id == CrawlPage.id, isouter=True)
            .where(SeoPageAnalysis.seo_analysis_id == seo_analysis_id)
            .order_by(CrawlPage.depth.asc(), CrawlPage.id.asc())
        )
        return [(row[0], row[1]) for row in self.db.execute(statement).all()]

    def list_issues_for_page(self, seo_analysis_id: int, crawl_page_id: int) -> list[SeoAnalysisIssue]:
        """Return SEO issues attached to one crawled page."""

        statement = (
            select(SeoAnalysisIssue)
            .where(
                SeoAnalysisIssue.seo_analysis_id == seo_analysis_id,
                SeoAnalysisIssue.crawl_page_id == crawl_page_id,
            )
            .order_by(SeoAnalysisIssue.severity.asc(), SeoAnalysisIssue.id.asc())
        )
        return list(self.db.scalars(statement))

    def list_provider_results_with_pages(self, analysis_id: int) -> list[tuple[GeoProviderResult, CrawlPage | None]]:
        """Return GEO provider results with their crawled pages when available."""

        statement = (
            select(GeoProviderResult, CrawlPage)
            .join(CrawlPage, CrawlPage.id == GeoProviderResult.crawl_page_id, isouter=True)
            .where(GeoProviderResult.geo_analysis_id == analysis_id)
            .order_by(GeoProviderResult.id.asc())
        )
        return [(row[0], row[1]) for row in self.db.execute(statement).all()]

    def list_recommendations_with_pages(self, analysis_id: int) -> list[tuple[GeoRecommendation, CrawlPage | None]]:
        """Return GEO recommendations with their crawled pages when available."""

        statement = (
            select(GeoRecommendation, CrawlPage)
            .join(CrawlPage, CrawlPage.id == GeoRecommendation.crawl_page_id, isouter=True)
            .where(GeoRecommendation.geo_analysis_id == analysis_id)
            .order_by(GeoRecommendation.priority.asc(), GeoRecommendation.id.asc())
        )
        return [(row[0], row[1]) for row in self.db.execute(statement).all()]

    def clear_results(self, analysis_id: int) -> None:
        """Delete provider results and recommendations attached to an analysis."""

        self.db.execute(delete(GeoRecommendation).where(GeoRecommendation.geo_analysis_id == analysis_id))
        self.db.execute(delete(GeoProviderResult).where(GeoProviderResult.geo_analysis_id == analysis_id))
        self.db.commit()

    def create_provider_result(self, data: dict[str, Any]) -> GeoProviderResult:
        """Persist one provider result."""

        item = GeoProviderResult(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_recommendation(self, data: dict[str, Any]) -> GeoRecommendation:
        """Persist one GEO recommendation."""

        item = GeoRecommendation(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self, params: PaginationParams) -> tuple[list[GeoAnalysis], int]:
        """Return paginated GEO analyses ordered by recent creation."""

        statement = select(self.model).options(
            selectinload(GeoAnalysis.provider_results),
            selectinload(GeoAnalysis.recommendations),
        )
        count_statement = select(func.count()).select_from(self.model)
        filters = self._search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        if params.sort and hasattr(self.model, params.sort):
            sort_column = getattr(self.model, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(self.model.id.desc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)
