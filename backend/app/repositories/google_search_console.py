"""Repository for Google Search Console data."""

from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import (
    GoogleSearchConsoleImport,
    GoogleSearchConsoleIndexCoverage,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleProperty,
    GoogleSearchConsoleSitemap,
)
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.google_search_console import (
    GoogleSearchConsoleImportFilters,
    GoogleSearchConsoleIndexCoverageFilters,
    GoogleSearchConsolePerformanceFilters,
    GoogleSearchConsoleSitemapFilters,
)
from backend.app.schemas.pagination import PaginationParams


class GoogleSearchConsoleRepository(BaseRepository[GoogleSearchConsoleProperty]):
    """Encapsulate persistence for Google Search Console data."""

    search_fields = ("site_url", "permission_level", "status")

    def __init__(self, db: Session) -> None:
        super().__init__(db, GoogleSearchConsoleProperty)

    def get_property_by_site_url(self, site_url: str) -> GoogleSearchConsoleProperty | None:
        """Return a property by its Google site URL."""

        return self.db.scalar(
            select(GoogleSearchConsoleProperty).where(GoogleSearchConsoleProperty.site_url == site_url),
        )

    def upsert_property(self, data: dict[str, Any]) -> tuple[GoogleSearchConsoleProperty, bool]:
        """Create or update a property by site URL."""

        existing = self.get_property_by_site_url(data["site_url"])
        if existing is None:
            return self.create(data), True
        return self.update(existing, data), False

    def list_performances(
        self,
        filters: GoogleSearchConsolePerformanceFilters,
        params: PaginationParams,
    ) -> tuple[list[GoogleSearchConsolePerformance], int]:
        """Return performance rows with filters and pagination."""

        statement = select(GoogleSearchConsolePerformance).where(
            GoogleSearchConsolePerformance.property_id == filters.property_id,
        )
        count_statement = (
            select(func.count())
            .select_from(GoogleSearchConsolePerformance)
            .where(GoogleSearchConsolePerformance.property_id == filters.property_id)
        )
        conditions = self._performance_conditions(filters)
        for condition in conditions:
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        statement = self._apply_order(
            statement,
            GoogleSearchConsolePerformance,
            params,
            default_sort=GoogleSearchConsolePerformance.date.desc(),
        )
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def find_performance(
        self,
        *,
        property_id: int,
        row_date: date,
        page: str | None,
        query: str | None,
        country: str | None,
        device: str | None,
    ) -> GoogleSearchConsolePerformance | None:
        """Return a performance row by its functional dimensions."""

        statement = select(GoogleSearchConsolePerformance).where(
            GoogleSearchConsolePerformance.property_id == property_id,
            GoogleSearchConsolePerformance.date == row_date,
            self._nullable_match(GoogleSearchConsolePerformance.page, page),
            self._nullable_match(GoogleSearchConsolePerformance.query, query),
            self._nullable_match(GoogleSearchConsolePerformance.country, country),
            self._nullable_match(GoogleSearchConsolePerformance.device, device),
        )
        return self.db.scalar(statement)

    def upsert_performance(self, data: dict[str, Any]) -> tuple[GoogleSearchConsolePerformance, bool]:
        """Create or update one performance row by dimensions."""

        existing = self.find_performance(
            property_id=data["property_id"],
            row_date=data["date"],
            page=data.get("page"),
            query=data.get("query"),
            country=data.get("country"),
            device=data.get("device"),
        )
        if existing is None:
            item = GoogleSearchConsolePerformance(**data)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item, True
        for key, value in data.items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing, False

    def list_index_coverages(
        self,
        filters: GoogleSearchConsoleIndexCoverageFilters,
        params: PaginationParams,
    ) -> tuple[list[GoogleSearchConsoleIndexCoverage], int]:
        """Return index coverage rows with filters and pagination."""

        statement = select(GoogleSearchConsoleIndexCoverage).where(
            GoogleSearchConsoleIndexCoverage.property_id == filters.property_id,
        )
        count_statement = (
            select(func.count())
            .select_from(GoogleSearchConsoleIndexCoverage)
            .where(GoogleSearchConsoleIndexCoverage.property_id == filters.property_id)
        )
        if filters.coverage_state:
            statement = statement.where(GoogleSearchConsoleIndexCoverage.coverage_state == filters.coverage_state)
            count_statement = count_statement.where(
                GoogleSearchConsoleIndexCoverage.coverage_state == filters.coverage_state,
            )
        if filters.verdict:
            statement = statement.where(GoogleSearchConsoleIndexCoverage.verdict == filters.verdict)
            count_statement = count_statement.where(GoogleSearchConsoleIndexCoverage.verdict == filters.verdict)
        statement = self._apply_order(
            statement,
            GoogleSearchConsoleIndexCoverage,
            params,
            default_sort=GoogleSearchConsoleIndexCoverage.id.asc(),
        )
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def find_index_coverage(self, property_id: int, url: str) -> GoogleSearchConsoleIndexCoverage | None:
        """Return index coverage by property and URL."""

        return self.db.scalar(
            select(GoogleSearchConsoleIndexCoverage).where(
                GoogleSearchConsoleIndexCoverage.property_id == property_id,
                GoogleSearchConsoleIndexCoverage.url == url,
            ),
        )

    def upsert_index_coverage(self, data: dict[str, Any]) -> tuple[GoogleSearchConsoleIndexCoverage, bool]:
        """Create or update one index coverage row."""

        existing = self.find_index_coverage(data["property_id"], data["url"])
        if existing is None:
            item = GoogleSearchConsoleIndexCoverage(**data)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item, True
        for key, value in data.items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing, False

    def list_sitemaps(
        self,
        filters: GoogleSearchConsoleSitemapFilters,
        params: PaginationParams,
    ) -> tuple[list[GoogleSearchConsoleSitemap], int]:
        """Return sitemaps with filters and pagination."""

        statement = select(GoogleSearchConsoleSitemap).where(
            GoogleSearchConsoleSitemap.property_id == filters.property_id,
        )
        count_statement = (
            select(func.count())
            .select_from(GoogleSearchConsoleSitemap)
            .where(GoogleSearchConsoleSitemap.property_id == filters.property_id)
        )
        if filters.status:
            statement = statement.where(GoogleSearchConsoleSitemap.status == filters.status)
            count_statement = count_statement.where(GoogleSearchConsoleSitemap.status == filters.status)
        statement = self._apply_order(
            statement,
            GoogleSearchConsoleSitemap,
            params,
            default_sort=GoogleSearchConsoleSitemap.id.asc(),
        )
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def find_sitemap(self, property_id: int, sitemap_url: str) -> GoogleSearchConsoleSitemap | None:
        """Return sitemap by property and URL."""

        return self.db.scalar(
            select(GoogleSearchConsoleSitemap).where(
                GoogleSearchConsoleSitemap.property_id == property_id,
                GoogleSearchConsoleSitemap.sitemap_url == sitemap_url,
            ),
        )

    def upsert_sitemap(self, data: dict[str, Any]) -> tuple[GoogleSearchConsoleSitemap, bool]:
        """Create or update one sitemap row."""

        existing = self.find_sitemap(data["property_id"], data["sitemap_url"])
        if existing is None:
            item = GoogleSearchConsoleSitemap(**data)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item, True
        for key, value in data.items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing, False

    def list_imports(
        self,
        filters: GoogleSearchConsoleImportFilters,
        params: PaginationParams,
    ) -> tuple[list[GoogleSearchConsoleImport], int]:
        """Return import history rows with filters and pagination."""

        statement = select(GoogleSearchConsoleImport)
        count_statement = select(func.count()).select_from(GoogleSearchConsoleImport)
        if filters.property_id is not None:
            statement = statement.where(GoogleSearchConsoleImport.property_id == filters.property_id)
            count_statement = count_statement.where(GoogleSearchConsoleImport.property_id == filters.property_id)
        if filters.import_type:
            statement = statement.where(GoogleSearchConsoleImport.import_type == filters.import_type)
            count_statement = count_statement.where(GoogleSearchConsoleImport.import_type == filters.import_type)
        if filters.status:
            statement = statement.where(GoogleSearchConsoleImport.status == filters.status)
            count_statement = count_statement.where(GoogleSearchConsoleImport.status == filters.status)
        statement = self._apply_order(
            statement,
            GoogleSearchConsoleImport,
            params,
            default_sort=GoogleSearchConsoleImport.id.desc(),
        )
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def get_import(self, import_id: int) -> GoogleSearchConsoleImport | None:
        """Return one import history row."""

        return self.db.get(GoogleSearchConsoleImport, import_id)

    def create_import(self, data: dict[str, Any]) -> GoogleSearchConsoleImport:
        """Persist one import history row."""

        item = GoogleSearchConsoleImport(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_import(self, item: GoogleSearchConsoleImport, data: dict[str, Any]) -> GoogleSearchConsoleImport:
        """Update one import history row."""

        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def _performance_conditions(self, filters: GoogleSearchConsolePerformanceFilters) -> list[Any]:
        conditions: list[Any] = []
        if filters.start_date is not None:
            conditions.append(GoogleSearchConsolePerformance.date >= filters.start_date)
        if filters.end_date is not None:
            conditions.append(GoogleSearchConsolePerformance.date <= filters.end_date)
        if filters.page:
            conditions.append(GoogleSearchConsolePerformance.page == filters.page)
        if filters.query:
            conditions.append(GoogleSearchConsolePerformance.query == filters.query)
        if filters.country:
            conditions.append(GoogleSearchConsolePerformance.country == filters.country)
        if filters.device:
            conditions.append(GoogleSearchConsolePerformance.device == filters.device)
        return conditions

    def _apply_order(self, statement: Any, model: type, params: PaginationParams, *, default_sort: Any) -> Any:
        if params.sort and hasattr(model, params.sort):
            sort_column = getattr(model, params.sort)
            return statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        return statement.order_by(default_sort)

    def _nullable_match(self, column: Any, value: Any) -> Any:
        if value is None:
            return column.is_(None)
        return column == value
