"""Persistence and canonical-source reads for recommendations."""

from typing import Any

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, joinedload

from backend.app.models import (
    Alert,
    BingWebmasterCrawlStat,
    BingWebmasterSite,
    BingWebmasterSitemap,
    CrawlSession,
    GeoAnalysis,
    GeoRecommendation,
    GoogleAnalyticsMetric,
    GoogleAnalyticsProperty,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleProperty,
    MonitoringEvent,
    SeoAnalysis,
    SeoAnalysisIssue,
)
from backend.app.models.recommendation import Recommendation
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.recommendations import RecommendationFilters


class RecommendationRepository(BaseRepository[Recommendation]):
    """Centralize recommendation persistence and reads from existing sources."""

    sort_fields = {
        "id",
        "source",
        "category",
        "priority",
        "impact",
        "difficulty",
        "score",
        "status",
        "created_at",
        "updated_at",
    }

    def __init__(self, db: Session) -> None:
        super().__init__(db, Recommendation)

    def list_recommendations(
        self,
        params: PaginationParams,
        *,
        filters: RecommendationFilters,
        website_ids: list[int] | None = None,
    ) -> tuple[list[Recommendation], int]:
        """Return persisted recommendations with filters and stable pagination."""

        statement = select(Recommendation).options(joinedload(Recommendation.website))
        count_statement = select(func.count()).select_from(Recommendation)
        conditions = self._filters(filters, params.search, website_ids=website_ids)
        if conditions:
            statement = statement.where(*conditions)
            count_statement = count_statement.where(*conditions)
        statement = self._order_and_page(statement, params)
        return list(self.db.scalars(statement).unique()), int(self.db.scalar(count_statement) or 0)

    def get_recommendation(self, recommendation_id: int) -> Recommendation | None:
        """Return one recommendation and its optional Website."""

        statement = (
            select(Recommendation)
            .options(joinedload(Recommendation.website))
            .where(Recommendation.id == recommendation_id)
        )
        return self.db.scalar(statement)

    def get_by_deduplication_key(self, key: str) -> Recommendation | None:
        """Return the unique recommendation associated with one business key."""

        return self.db.scalar(select(Recommendation).where(Recommendation.deduplication_key == key))

    def add_pending(self, data: dict[str, Any]) -> Recommendation:
        """Add a recommendation without committing the current consolidation batch."""

        item = Recommendation(**data)
        self.db.add(item)
        self.db.flush()
        return item

    def update_pending(self, item: Recommendation, data: dict[str, Any]) -> Recommendation:
        """Update a recommendation without committing the current consolidation batch."""

        for key, value in data.items():
            setattr(item, key, value)
        self.db.flush()
        return item

    def commit(self) -> None:
        """Commit a consolidation or lifecycle transaction."""

        self.db.commit()

    def rollback(self) -> None:
        """Rollback a failed consolidation transaction."""

        self.db.rollback()

    def seo_issue_rows(self) -> list[dict[str, Any]]:
        """Return persisted SEO issues with their Website context."""

        statement = (
            select(CrawlSession.website_id, SeoAnalysisIssue)
            .join(SeoAnalysis, SeoAnalysis.id == SeoAnalysisIssue.seo_analysis_id)
            .join(CrawlSession, CrawlSession.id == SeoAnalysis.crawl_session_id)
            .order_by(SeoAnalysisIssue.created_at.asc(), SeoAnalysisIssue.id.asc())
        )
        return [{"website_id": row[0], "item": row[1]} for row in self.db.execute(statement)]

    def geo_recommendation_rows(self) -> list[dict[str, Any]]:
        """Return existing GEO recommendations with their Website context."""

        statement = (
            select(CrawlSession.website_id, GeoRecommendation)
            .join(GeoAnalysis, GeoAnalysis.id == GeoRecommendation.geo_analysis_id)
            .join(CrawlSession, CrawlSession.id == GeoAnalysis.crawl_session_id)
            .order_by(GeoRecommendation.created_at.asc(), GeoRecommendation.id.asc())
        )
        return [{"website_id": row[0], "item": row[1]} for row in self.db.execute(statement)]

    def monitoring_event_rows(self) -> list[dict[str, Any]]:
        """Return persisted monitoring events without calling a connector."""

        statement = select(MonitoringEvent).order_by(MonitoringEvent.created_at.asc(), MonitoringEvent.id.asc())
        return [{"item": item} for item in self.db.scalars(statement)]

    def active_alert_rows(self) -> list[dict[str, Any]]:
        """Return active and acknowledged alerts used as canonical signals."""

        statement = (
            select(Alert)
            .where(Alert.status.in_(("Active", "Acknowledged")))
            .order_by(Alert.first_seen_at.asc(), Alert.id.asc())
        )
        return [{"item": item} for item in self.db.scalars(statement)]

    def gsc_performance_rows(self) -> list[dict[str, Any]]:
        """Return persisted GSC performance rows and Website context."""

        statement = (
            select(GoogleSearchConsoleProperty.website_id, GoogleSearchConsolePerformance)
            .join(
                GoogleSearchConsoleProperty,
                GoogleSearchConsoleProperty.id == GoogleSearchConsolePerformance.property_id,
            )
            .order_by(GoogleSearchConsolePerformance.date.asc(), GoogleSearchConsolePerformance.id.asc())
        )
        return [{"website_id": row[0], "item": row[1]} for row in self.db.execute(statement)]

    def ga4_metric_rows(self) -> list[dict[str, Any]]:
        """Return persisted GA4 metric rows and Website context."""

        statement = (
            select(GoogleAnalyticsProperty.website_id, GoogleAnalyticsMetric)
            .join(GoogleAnalyticsProperty, GoogleAnalyticsProperty.id == GoogleAnalyticsMetric.property_id)
            .order_by(GoogleAnalyticsMetric.date.asc(), GoogleAnalyticsMetric.id.asc())
        )
        return [{"website_id": row[0], "item": row[1]} for row in self.db.execute(statement)]

    def bing_crawl_rows(self) -> list[dict[str, Any]]:
        """Return persisted Bing crawl rows and Website context."""

        statement = (
            select(BingWebmasterSite.website_id, BingWebmasterCrawlStat)
            .join(BingWebmasterSite, BingWebmasterSite.id == BingWebmasterCrawlStat.bing_site_id)
            .order_by(BingWebmasterCrawlStat.date.asc(), BingWebmasterCrawlStat.id.asc())
        )
        return [{"website_id": row[0], "item": row[1]} for row in self.db.execute(statement)]

    def bing_sitemap_rows(self) -> list[dict[str, Any]]:
        """Return persisted Bing sitemap rows and Website context."""

        statement = (
            select(BingWebmasterSite.website_id, BingWebmasterSitemap)
            .join(BingWebmasterSite, BingWebmasterSite.id == BingWebmasterSitemap.bing_site_id)
            .order_by(BingWebmasterSitemap.created_at.asc(), BingWebmasterSitemap.id.asc())
        )
        return [{"website_id": row[0], "item": row[1]} for row in self.db.execute(statement)]

    def grouped_counts(
        self,
        column_name: str,
        *,
        filters: RecommendationFilters,
        website_ids: list[int] | None = None,
    ) -> dict[str, int]:
        """Return grouped recommendation counters for one whitelisted column."""

        if column_name not in {"priority", "category", "status"}:
            raise ValueError(f"Champ de synthese recommandation non autorise: {column_name}.")
        column = getattr(Recommendation, column_name)
        statement = select(column, func.count()).select_from(Recommendation)
        conditions = self._filters(filters, filters.search, website_ids=website_ids)
        if conditions:
            statement = statement.where(*conditions)
        statement = statement.group_by(column)
        return {str(value): int(count) for value, count in self.db.execute(statement)}

    def _filters(
        self,
        filters: RecommendationFilters,
        search: str | None,
        *,
        website_ids: list[int] | None,
    ) -> list[Any]:
        conditions = []
        if filters.website_id is not None:
            conditions.append(Recommendation.website_id == filters.website_id)
        elif website_ids is not None:
            conditions.append(Recommendation.website_id.in_(website_ids) if website_ids else Recommendation.id < 0)
        if filters.source is not None:
            conditions.append(Recommendation.source == filters.source.value)
        if filters.category is not None:
            conditions.append(Recommendation.category == filters.category)
        if filters.priority is not None:
            conditions.append(Recommendation.priority == filters.priority.value)
        if filters.status is not None:
            conditions.append(Recommendation.status == filters.status.value)
        if search:
            pattern = f"%{search}%"
            conditions.append(
                or_(
                    Recommendation.title.ilike(pattern),
                    Recommendation.description.ilike(pattern),
                    Recommendation.category.ilike(pattern),
                    Recommendation.source.ilike(pattern),
                ),
            )
        return conditions

    def _order_and_page(self, statement: Any, params: PaginationParams) -> Any:
        if params.sort:
            if params.sort not in self.sort_fields:
                raise ValueError(f"Champ de tri recommandation non autorise: {params.sort}.")
            sort_column = self._sort_column(params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(
                Recommendation.score.desc(),
                Recommendation.created_at.desc(),
                Recommendation.id.desc(),
            )
        return statement.offset(params.offset).limit(params.page_size)

    def _sort_column(self, field_name: str) -> Any:
        if field_name == "priority":
            return case(
                (Recommendation.priority == "CRITICAL", 4),
                (Recommendation.priority == "HIGH", 3),
                (Recommendation.priority == "MEDIUM", 2),
                else_=1,
            )
        return getattr(Recommendation, field_name)
