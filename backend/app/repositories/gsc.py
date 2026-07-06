"""Repositories for Google Search Console data."""

from collections.abc import Iterable
from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import (
    GscCoverageSnapshot,
    GscImportRun,
    GscIndexingInspection,
    GscOAuthCredential,
    GscPerformanceDaily,
    GscProperty,
    GscSitemap,
)
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class GscOAuthCredentialRepository(BaseRepository[GscOAuthCredential]):
    """Persistence for GSC OAuth credentials."""

    search_fields = ("provider", "status")

    def __init__(self, db: Session) -> None:
        super().__init__(db, GscOAuthCredential)

    def latest(self) -> GscOAuthCredential | None:
        """Return the latest OAuth credential."""

        return self.db.scalar(select(GscOAuthCredential).order_by(GscOAuthCredential.id.desc()).limit(1))

    def count_active(self) -> int:
        """Return active OAuth credential count."""

        statement = select(func.count()).select_from(GscOAuthCredential).where(GscOAuthCredential.status == "ACTIVE")
        return int(self.db.scalar(statement) or 0)


class GscPropertyRepository(BaseRepository[GscProperty]):
    """Persistence for GSC properties."""

    search_fields = ("site_url", "property_type", "permission_level")

    def __init__(self, db: Session) -> None:
        super().__init__(db, GscProperty)

    def get_by_site_url(self, site_url: str) -> GscProperty | None:
        """Return one property by site URL."""

        return self.db.scalar(select(GscProperty).where(GscProperty.site_url == site_url))

    def upsert_property(self, data: dict[str, Any]) -> GscProperty:
        """Create or update a GSC property by site URL."""

        existing = self.get_by_site_url(str(data["site_url"]))
        if existing is None:
            return self.create(data)
        return self.update(existing, data)


class GscImportRunRepository(BaseRepository[GscImportRun]):
    """Persistence for GSC import runs."""

    search_fields = ("status", "import_type")

    def __init__(self, db: Session) -> None:
        super().__init__(db, GscImportRun)


class GscDataRepository:
    """Persistence helpers for imported GSC datasets."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_performance_rows(self, rows: Iterable[dict[str, Any]]) -> int:
        """Upsert performance rows using the natural import dimensions."""

        count = 0
        for data in rows:
            existing = self.db.scalar(
                select(GscPerformanceDaily).where(
                    GscPerformanceDaily.property_id == data["property_id"],
                    GscPerformanceDaily.date == data["date"],
                    GscPerformanceDaily.page == data.get("page", ""),
                    GscPerformanceDaily.query == data.get("query", ""),
                    GscPerformanceDaily.device == data.get("device", ""),
                    GscPerformanceDaily.country == data.get("country", ""),
                    GscPerformanceDaily.search_type == data.get("search_type", "web"),
                ),
            )
            payload = {
                **data,
                "page": data.get("page", ""),
                "query": data.get("query", ""),
                "device": data.get("device", ""),
                "country": data.get("country", ""),
                "search_type": data.get("search_type", "web"),
            }
            if existing is None:
                self.db.add(GscPerformanceDaily(**payload))
            else:
                self._apply(existing, payload)
            count += 1
        self.db.commit()
        return count

    def upsert_coverage_rows(self, rows: Iterable[dict[str, Any]]) -> int:
        """Upsert coverage snapshots by property, date, category and state."""

        count = 0
        for data in rows:
            existing = self.db.scalar(
                select(GscCoverageSnapshot).where(
                    GscCoverageSnapshot.property_id == data["property_id"],
                    GscCoverageSnapshot.date == data["date"],
                    GscCoverageSnapshot.category == data["category"],
                    GscCoverageSnapshot.state == data["state"],
                ),
            )
            if existing is None:
                self.db.add(GscCoverageSnapshot(**data))
            else:
                self._apply(existing, data)
            count += 1
        self.db.commit()
        return count

    def upsert_indexing_rows(self, rows: Iterable[dict[str, Any]]) -> int:
        """Upsert indexing inspections by property, URL and inspection date."""

        count = 0
        for data in rows:
            existing = self.db.scalar(
                select(GscIndexingInspection).where(
                    GscIndexingInspection.property_id == data["property_id"],
                    GscIndexingInspection.inspected_url == data["inspected_url"],
                    GscIndexingInspection.inspected_at == data["inspected_at"],
                ),
            )
            if existing is None:
                self.db.add(GscIndexingInspection(**data))
            else:
                self._apply(existing, data)
            count += 1
        self.db.commit()
        return count

    def upsert_sitemaps(self, rows: Iterable[dict[str, Any]]) -> int:
        """Upsert sitemaps by property and sitemap URL."""

        count = 0
        for data in rows:
            existing = self.db.scalar(
                select(GscSitemap).where(
                    GscSitemap.property_id == data["property_id"],
                    GscSitemap.sitemap_url == data["sitemap_url"],
                ),
            )
            if existing is None:
                self.db.add(GscSitemap(**data))
            else:
                self._apply(existing, data)
            count += 1
        self.db.commit()
        return count

    def list_performance(
        self,
        property_id: int,
        params: PaginationParams,
        *,
        date_start: date | None = None,
        date_end: date | None = None,
    ) -> tuple[list[GscPerformanceDaily], int]:
        """Return paginated performance rows."""

        statement = select(GscPerformanceDaily).where(GscPerformanceDaily.property_id == property_id)
        count_statement = select(func.count()).select_from(GscPerformanceDaily).where(
            GscPerformanceDaily.property_id == property_id,
        )
        statement, count_statement = self._date_filters(
            statement,
            count_statement,
            GscPerformanceDaily,
            date_start,
            date_end,
        )
        statement = statement.order_by(GscPerformanceDaily.date.desc(), GscPerformanceDaily.id.desc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_coverage(self, property_id: int, params: PaginationParams) -> tuple[list[GscCoverageSnapshot], int]:
        """Return paginated coverage snapshots."""

        statement = (
            select(GscCoverageSnapshot)
            .where(GscCoverageSnapshot.property_id == property_id)
            .order_by(GscCoverageSnapshot.date.desc(), GscCoverageSnapshot.id.desc())
        )
        count_statement = select(func.count()).select_from(GscCoverageSnapshot).where(
            GscCoverageSnapshot.property_id == property_id,
        )
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_indexing(self, property_id: int, params: PaginationParams) -> tuple[list[GscIndexingInspection], int]:
        """Return paginated indexing inspections."""

        statement = (
            select(GscIndexingInspection)
            .where(GscIndexingInspection.property_id == property_id)
            .order_by(GscIndexingInspection.inspected_at.desc(), GscIndexingInspection.id.desc())
        )
        count_statement = select(func.count()).select_from(GscIndexingInspection).where(
            GscIndexingInspection.property_id == property_id,
        )
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_sitemaps(self, property_id: int, params: PaginationParams) -> tuple[list[GscSitemap], int]:
        """Return paginated sitemaps."""

        statement = (
            select(GscSitemap)
            .where(GscSitemap.property_id == property_id)
            .order_by(GscSitemap.sitemap_url.asc())
        )
        count_statement = select(func.count()).select_from(GscSitemap).where(GscSitemap.property_id == property_id)
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def _date_filters(
        self,
        statement: Any,
        count_statement: Any,
        model: Any,
        start: date | None,
        end: date | None,
    ) -> Any:
        if start is not None:
            statement = statement.where(model.date >= start)
            count_statement = count_statement.where(model.date >= start)
        if end is not None:
            statement = statement.where(model.date <= end)
            count_statement = count_statement.where(model.date <= end)
        return statement, count_statement

    def _apply(self, item: Any, data: dict[str, Any]) -> None:
        for key, value in data.items():
            setattr(item, key, value)
