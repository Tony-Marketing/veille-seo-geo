"""Repository for Google Analytics 4 data."""

from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import (
    GoogleAnalyticsDimension,
    GoogleAnalyticsImport,
    GoogleAnalyticsMetric,
    GoogleAnalyticsProperty,
)
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class GoogleAnalyticsRepository(BaseRepository[GoogleAnalyticsProperty]):
    """Encapsulate SQLAlchemy persistence for Google Analytics."""

    search_fields = ("property_id", "property_name", "account_name", "measurement_id")

    def __init__(self, db: Session) -> None:
        super().__init__(db, GoogleAnalyticsProperty)

    def get_property(self, property_pk: int) -> GoogleAnalyticsProperty | None:
        """Return a Google Analytics property by primary key."""

        return self.db.get(GoogleAnalyticsProperty, property_pk)

    def get_property_by_property_id(self, property_id: str) -> GoogleAnalyticsProperty | None:
        """Return a property by its Google Analytics identifier."""

        statement = select(GoogleAnalyticsProperty).where(GoogleAnalyticsProperty.property_id == property_id)
        return self.db.scalar(statement)

    def list_properties(self, params: PaginationParams) -> tuple[list[GoogleAnalyticsProperty], int]:
        """Return paginated properties ordered by recent creation."""

        statement = select(GoogleAnalyticsProperty)
        count_statement = select(func.count()).select_from(GoogleAnalyticsProperty)
        filters = self._search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        if params.sort and hasattr(GoogleAnalyticsProperty, params.sort):
            sort_column = getattr(GoogleAnalyticsProperty, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(GoogleAnalyticsProperty.id.desc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def create_import(self, data: dict[str, Any]) -> GoogleAnalyticsImport:
        """Persist a new import log."""

        item = GoogleAnalyticsImport(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_import(self, item: GoogleAnalyticsImport, data: dict[str, Any]) -> GoogleAnalyticsImport:
        """Update an import log."""

        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_import(self, import_id: int) -> GoogleAnalyticsImport | None:
        """Return an import log by primary key."""

        return self.db.get(GoogleAnalyticsImport, import_id)

    def list_imports(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> tuple[list[GoogleAnalyticsImport], int]:
        """Return paginated import logs."""

        statement = select(GoogleAnalyticsImport)
        count_statement = select(func.count()).select_from(GoogleAnalyticsImport)
        if property_id is not None:
            statement = statement.where(GoogleAnalyticsImport.property_id == property_id)
            count_statement = count_statement.where(GoogleAnalyticsImport.property_id == property_id)
        statement = self._order_and_page(statement, params, GoogleAnalyticsImport)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def upsert_metric(self, data: dict[str, Any]) -> GoogleAnalyticsMetric:
        """Create or update one idempotent metric row and its dimensions."""

        item = self._get_metric_by_dimensions(
            property_id=data["property_id"],
            metric_date=data["date"],
            source=data.get("source"),
            medium=data.get("medium"),
            campaign=data.get("campaign"),
            device_category=data.get("device_category"),
            country=data.get("country"),
        )
        if item is None:
            item = GoogleAnalyticsMetric(**data)
            self.db.add(item)
            self.db.flush()
            item.dimension = GoogleAnalyticsDimension(
                metric_id=item.id,
                source=data.get("source"),
                medium=data.get("medium"),
                campaign=data.get("campaign"),
                device_category=data.get("device_category"),
                country=data.get("country"),
            )
        else:
            for key, value in data.items():
                setattr(item, key, value)
            if item.dimension is None:
                item.dimension = GoogleAnalyticsDimension(metric_id=item.id)
            item.dimension.source = data.get("source")
            item.dimension.medium = data.get("medium")
            item.dimension.campaign = data.get("campaign")
            item.dimension.device_category = data.get("device_category")
            item.dimension.country = data.get("country")
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_property(self, item: GoogleAnalyticsProperty) -> None:
        """Delete a Google Analytics property."""

        self.delete(item)

    def _get_metric_by_dimensions(
        self,
        *,
        property_id: int,
        metric_date: date,
        source: str | None,
        medium: str | None,
        campaign: str | None,
        device_category: str | None,
        country: str | None,
    ) -> GoogleAnalyticsMetric | None:
        statement = select(GoogleAnalyticsMetric).where(
            GoogleAnalyticsMetric.property_id == property_id,
            GoogleAnalyticsMetric.date == metric_date,
            GoogleAnalyticsMetric.source == source,
            GoogleAnalyticsMetric.medium == medium,
            GoogleAnalyticsMetric.campaign == campaign,
            GoogleAnalyticsMetric.device_category == device_category,
            GoogleAnalyticsMetric.country == country,
        )
        return self.db.scalar(statement)

    def _order_and_page(self, statement: Any, params: PaginationParams, model: type[Any]) -> Any:
        if params.sort and hasattr(model, params.sort):
            sort_column = getattr(model, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(model.id.desc())
        return statement.offset(params.offset).limit(params.page_size)
