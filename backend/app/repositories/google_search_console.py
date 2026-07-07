"""Repository for Google Search Console data."""

from datetime import date, datetime
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
from backend.app.schemas.pagination import PaginationParams


class GoogleSearchConsoleRepository(BaseRepository[GoogleSearchConsoleProperty]):
    """Encapsulate SQLAlchemy persistence for Google Search Console."""

    search_fields = ("google_property_id", "property_url", "display_name")

    def __init__(self, db: Session) -> None:
        super().__init__(db, GoogleSearchConsoleProperty)

    def get_property(self, property_id: int) -> GoogleSearchConsoleProperty | None:
        """Return a Google Search Console property by primary key."""

        return self.db.get(GoogleSearchConsoleProperty, property_id)

    def get_property_by_google_id(self, google_property_id: str) -> GoogleSearchConsoleProperty | None:
        """Return a property by its Google identifier."""

        statement = select(GoogleSearchConsoleProperty).where(
            GoogleSearchConsoleProperty.google_property_id == google_property_id,
        )
        return self.db.scalar(statement)

    def list_properties(self, params: PaginationParams) -> tuple[list[GoogleSearchConsoleProperty], int]:
        """Return paginated properties ordered by recent creation."""

        statement = select(GoogleSearchConsoleProperty)
        count_statement = select(func.count()).select_from(GoogleSearchConsoleProperty)
        filters = self._search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        if params.sort and hasattr(GoogleSearchConsoleProperty, params.sort):
            sort_column = getattr(GoogleSearchConsoleProperty, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(GoogleSearchConsoleProperty.id.desc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_performances(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        page: str | None = None,
        query: str | None = None,
        country: str | None = None,
        device: str | None = None,
    ) -> tuple[list[GoogleSearchConsolePerformance], int]:
        """Return paginated performance rows."""

        statement = select(GoogleSearchConsolePerformance)
        count_statement = select(func.count()).select_from(GoogleSearchConsolePerformance)
        filters = self._performance_filters(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            query=query,
            country=country,
            device=device,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(statement, params, GoogleSearchConsolePerformance)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_index_coverages(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> tuple[list[GoogleSearchConsoleIndexCoverage], int]:
        """Return paginated index coverage rows."""

        statement = select(GoogleSearchConsoleIndexCoverage)
        count_statement = select(func.count()).select_from(GoogleSearchConsoleIndexCoverage)
        if property_id is not None:
            statement = statement.where(GoogleSearchConsoleIndexCoverage.property_id == property_id)
            count_statement = count_statement.where(GoogleSearchConsoleIndexCoverage.property_id == property_id)
        statement = self._order_and_page(statement, params, GoogleSearchConsoleIndexCoverage)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_sitemaps(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> tuple[list[GoogleSearchConsoleSitemap], int]:
        """Return paginated sitemap rows."""

        statement = select(GoogleSearchConsoleSitemap)
        count_statement = select(func.count()).select_from(GoogleSearchConsoleSitemap)
        if property_id is not None:
            statement = statement.where(GoogleSearchConsoleSitemap.property_id == property_id)
            count_statement = count_statement.where(GoogleSearchConsoleSitemap.property_id == property_id)
        statement = self._order_and_page(statement, params, GoogleSearchConsoleSitemap)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_imports(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> tuple[list[GoogleSearchConsoleImport], int]:
        """Return paginated import logs."""

        statement = select(GoogleSearchConsoleImport)
        count_statement = select(func.count()).select_from(GoogleSearchConsoleImport)
        if property_id is not None:
            statement = statement.where(GoogleSearchConsoleImport.property_id == property_id)
            count_statement = count_statement.where(GoogleSearchConsoleImport.property_id == property_id)
        statement = self._order_and_page(statement, params, GoogleSearchConsoleImport)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def get_latest_import_completed_at(
        self,
        property_id: int,
        *,
        statuses: tuple[str, ...] = (),
    ) -> datetime | None:
        """Return the latest completed import date for one property."""

        statement = select(func.max(GoogleSearchConsoleImport.completed_at)).where(
            GoogleSearchConsoleImport.property_id == property_id,
            GoogleSearchConsoleImport.completed_at.is_not(None),
        )
        if statuses:
            statement = statement.where(GoogleSearchConsoleImport.status.in_(statuses))
        return self.db.scalar(statement)

    def get_latest_import_completed_at_by_property_ids(
        self,
        property_ids: list[int],
        *,
        statuses: tuple[str, ...] = (),
    ) -> dict[int, datetime]:
        """Return latest completed import dates keyed by property id."""

        if not property_ids:
            return {}
        statement = (
            select(
                GoogleSearchConsoleImport.property_id,
                func.max(GoogleSearchConsoleImport.completed_at),
            )
            .where(
                GoogleSearchConsoleImport.property_id.in_(property_ids),
                GoogleSearchConsoleImport.completed_at.is_not(None),
            )
            .group_by(GoogleSearchConsoleImport.property_id)
        )
        if statuses:
            statement = statement.where(GoogleSearchConsoleImport.status.in_(statuses))
        return {property_id: completed_at for property_id, completed_at in self.db.execute(statement).all()}

    def list_index_coverage_statuses(
        self,
        *,
        property_id: int | None = None,
    ) -> list[tuple[str, str | None, str | None, str | None]]:
        """Return indexation status fields used by the service aggregates."""

        statement = select(
            GoogleSearchConsoleIndexCoverage.coverage_state,
            GoogleSearchConsoleIndexCoverage.verdict,
            GoogleSearchConsoleIndexCoverage.google_state,
            GoogleSearchConsoleIndexCoverage.indexing_state,
        )
        if property_id is not None:
            statement = statement.where(GoogleSearchConsoleIndexCoverage.property_id == property_id)
        return list(self.db.execute(statement).all())

    def create_import(self, data: dict[str, Any]) -> GoogleSearchConsoleImport:
        """Persist a new import log."""

        item = GoogleSearchConsoleImport(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_import(
        self,
        item: GoogleSearchConsoleImport,
        data: dict[str, Any],
    ) -> GoogleSearchConsoleImport:
        """Update an import log."""

        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def upsert_performance(self, data: dict[str, Any]) -> GoogleSearchConsolePerformance:
        """Create or update one idempotent performance row."""

        statement = select(GoogleSearchConsolePerformance).where(
            GoogleSearchConsolePerformance.property_id == data["property_id"],
            GoogleSearchConsolePerformance.date == data["date"],
            GoogleSearchConsolePerformance.query == data.get("query"),
            GoogleSearchConsolePerformance.page == data.get("page"),
            GoogleSearchConsolePerformance.country == data.get("country"),
            GoogleSearchConsolePerformance.device == data.get("device"),
            GoogleSearchConsolePerformance.search_type == data.get("search_type", "web"),
        )
        item = self.db.scalar(statement)
        return self._upsert(item, GoogleSearchConsolePerformance, data)

    def upsert_index_coverage(self, data: dict[str, Any]) -> GoogleSearchConsoleIndexCoverage:
        """Create or update one idempotent index coverage row."""

        statement = select(GoogleSearchConsoleIndexCoverage).where(
            GoogleSearchConsoleIndexCoverage.property_id == data["property_id"],
            GoogleSearchConsoleIndexCoverage.url == data["url"],
        )
        item = self.db.scalar(statement)
        return self._upsert(item, GoogleSearchConsoleIndexCoverage, data)

    def upsert_sitemap(self, data: dict[str, Any]) -> GoogleSearchConsoleSitemap:
        """Create or update one idempotent sitemap row."""

        statement = select(GoogleSearchConsoleSitemap).where(
            GoogleSearchConsoleSitemap.property_id == data["property_id"],
            GoogleSearchConsoleSitemap.sitemap_url == data["sitemap_url"],
        )
        item = self.db.scalar(statement)
        return self._upsert(item, GoogleSearchConsoleSitemap, data)

    def delete_property(self, item: GoogleSearchConsoleProperty) -> None:
        """Delete a Google Search Console property."""

        self.delete(item)

    def _upsert(self, item: Any | None, model: type[Any], data: dict[str, Any]) -> Any:
        if item is None:
            item = model(**data)
            self.db.add(item)
        else:
            for key, value in data.items():
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def _order_and_page(self, statement: Any, params: PaginationParams, model: type[Any]) -> Any:
        if params.sort and hasattr(model, params.sort):
            sort_column = getattr(model, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        elif hasattr(model, "date"):
            statement = statement.order_by(model.date.desc(), model.id.desc())
        else:
            statement = statement.order_by(model.id.desc())
        return statement.offset(params.offset).limit(params.page_size)

    def _performance_filters(
        self,
        *,
        property_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        page: str | None = None,
        query: str | None = None,
        country: str | None = None,
        device: str | None = None,
    ) -> list[Any]:
        filters = []
        if property_id is not None:
            filters.append(GoogleSearchConsolePerformance.property_id == property_id)
        if start_date is not None:
            filters.append(GoogleSearchConsolePerformance.date >= start_date)
        if end_date is not None:
            filters.append(GoogleSearchConsolePerformance.date <= end_date)
        if page is not None:
            filters.append(GoogleSearchConsolePerformance.page == page)
        if query is not None:
            filters.append(GoogleSearchConsolePerformance.query == query)
        if country is not None:
            filters.append(GoogleSearchConsolePerformance.country == country)
        if device is not None:
            filters.append(GoogleSearchConsolePerformance.device == device)
        return filters
