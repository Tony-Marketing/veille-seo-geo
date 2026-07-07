"""Repository for Google Analytics 4 data."""

from datetime import date
from typing import Any

from sqlalchemy import func, or_, select
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
    property_sort_fields = (
        "id",
        "website_id",
        "property_id",
        "property_name",
        "account_name",
        "measurement_id",
        "enabled",
        "created_at",
        "updated_at",
    )
    import_sort_fields = ("id", "property_id", "status", "imported_rows", "started_at", "finished_at", "created_at")
    metric_sort_fields = (
        "id",
        "property_id",
        "import_id",
        "date",
        "source",
        "medium",
        "campaign",
        "device_category",
        "country",
        "users",
        "new_users",
        "sessions",
        "engaged_sessions",
        "screen_page_views",
        "average_session_duration",
        "engagement_rate",
        "conversions",
        "total_revenue",
        "created_at",
        "updated_at",
    )
    breakdown_fields = ("source", "medium", "campaign", "device_category", "country")

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
        statement = self._order_and_page(
            statement,
            params,
            GoogleAnalyticsProperty,
            allowed_sort_fields=self.property_sort_fields,
        )
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
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[GoogleAnalyticsImport], int]:
        """Return paginated import logs."""

        statement = select(GoogleAnalyticsImport).join(GoogleAnalyticsImport.property)
        count_statement = select(func.count(GoogleAnalyticsImport.id)).join(GoogleAnalyticsImport.property)
        filters = self._import_filters(property_id=property_id, status=status, search=search or params.search)
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(
            statement,
            params,
            GoogleAnalyticsImport,
            allowed_sort_fields=self.import_sort_fields,
        )
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_metrics(
        self,
        params: PaginationParams,
        *,
        website_id: int | None = None,
        property_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        import_id: int | None = None,
        source: str | None = None,
        medium: str | None = None,
        campaign: str | None = None,
        device_category: str | None = None,
        country: str | None = None,
        search: str | None = None,
    ) -> tuple[list[GoogleAnalyticsMetric], int]:
        """Return paginated metric rows."""

        statement = select(GoogleAnalyticsMetric).join(GoogleAnalyticsMetric.property)
        count_statement = select(func.count(GoogleAnalyticsMetric.id)).join(GoogleAnalyticsMetric.property)
        filters = self._metric_filters(
            website_id=website_id,
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            import_id=import_id,
            source=source,
            medium=medium,
            campaign=campaign,
            device_category=device_category,
            country=country,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(
            statement,
            params,
            GoogleAnalyticsMetric,
            allowed_sort_fields=self.metric_sort_fields,
            default_date_order=True,
        )
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def aggregate_metrics(
        self,
        *,
        website_id: int | None = None,
        property_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        import_id: int | None = None,
        source: str | None = None,
        medium: str | None = None,
        campaign: str | None = None,
        device_category: str | None = None,
        country: str | None = None,
        search: str | None = None,
    ) -> dict[str, float | int]:
        """Return raw aggregate values used by the service."""

        statement = select(
            func.count(GoogleAnalyticsMetric.id),
            func.coalesce(func.sum(GoogleAnalyticsMetric.sessions), 0),
            func.coalesce(func.sum(GoogleAnalyticsMetric.users), 0),
            func.coalesce(func.sum(GoogleAnalyticsMetric.new_users), 0),
            func.coalesce(func.sum(GoogleAnalyticsMetric.engaged_sessions), 0),
            func.coalesce(func.sum(GoogleAnalyticsMetric.screen_page_views), 0),
            func.coalesce(func.sum(GoogleAnalyticsMetric.conversions), 0.0),
            func.coalesce(func.sum(GoogleAnalyticsMetric.total_revenue), 0.0),
            func.coalesce(
                func.sum(GoogleAnalyticsMetric.average_session_duration * GoogleAnalyticsMetric.sessions),
                0.0,
            ),
            func.coalesce(func.sum(GoogleAnalyticsMetric.engagement_rate * GoogleAnalyticsMetric.sessions), 0.0),
        ).join(GoogleAnalyticsMetric.property)
        filters = self._metric_filters(
            website_id=website_id,
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            import_id=import_id,
            source=source,
            medium=medium,
            campaign=campaign,
            device_category=device_category,
            country=country,
            search=search,
        )
        if filters:
            statement = statement.where(*filters)
        row = self.db.execute(statement).one()
        return {
            "rows": int(row[0] or 0),
            "sessions": int(row[1] or 0),
            "users": int(row[2] or 0),
            "new_users": int(row[3] or 0),
            "engaged_sessions": int(row[4] or 0),
            "screen_page_views": int(row[5] or 0),
            "conversions": float(row[6] or 0.0),
            "total_revenue": float(row[7] or 0.0),
            "duration_weight": float(row[8] or 0.0),
            "engagement_weight": float(row[9] or 0.0),
        }

    def aggregate_metrics_by_dimension(
        self,
        dimension: str,
        *,
        website_id: int | None = None,
        property_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        import_id: int | None = None,
        source: str | None = None,
        medium: str | None = None,
        campaign: str | None = None,
        device_category: str | None = None,
        country: str | None = None,
        search: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, float | int | str | None]]:
        """Return aggregate values grouped by one whitelisted dimension."""

        if dimension not in self.breakdown_fields:
            raise ValueError(f"Tri ou dimension Google Analytics non autorise: {dimension}.")
        dimension_column = getattr(GoogleAnalyticsMetric, dimension)
        sessions_sum = func.coalesce(func.sum(GoogleAnalyticsMetric.sessions), 0)
        statement = (
            select(
                dimension_column,
                func.count(GoogleAnalyticsMetric.id),
                sessions_sum,
                func.coalesce(func.sum(GoogleAnalyticsMetric.users), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.new_users), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.engaged_sessions), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.screen_page_views), 0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.conversions), 0.0),
                func.coalesce(func.sum(GoogleAnalyticsMetric.total_revenue), 0.0),
                func.coalesce(
                    func.sum(GoogleAnalyticsMetric.average_session_duration * GoogleAnalyticsMetric.sessions),
                    0.0,
                ),
                func.coalesce(func.sum(GoogleAnalyticsMetric.engagement_rate * GoogleAnalyticsMetric.sessions), 0.0),
            )
            .join(GoogleAnalyticsMetric.property)
            .group_by(dimension_column)
            .order_by(sessions_sum.desc(), dimension_column.asc())
            .limit(limit)
        )
        filters = self._metric_filters(
            website_id=website_id,
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            import_id=import_id,
            source=source,
            medium=medium,
            campaign=campaign,
            device_category=device_category,
            country=country,
            search=search,
        )
        if filters:
            statement = statement.where(*filters)
        return [
            {
                "dimension": row[0],
                "rows": int(row[1] or 0),
                "sessions": int(row[2] or 0),
                "users": int(row[3] or 0),
                "new_users": int(row[4] or 0),
                "engaged_sessions": int(row[5] or 0),
                "screen_page_views": int(row[6] or 0),
                "conversions": float(row[7] or 0.0),
                "total_revenue": float(row[8] or 0.0),
                "duration_weight": float(row[9] or 0.0),
                "engagement_weight": float(row[10] or 0.0),
            }
            for row in self.db.execute(statement).all()
        ]

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

    def _order_and_page(
        self,
        statement: Any,
        params: PaginationParams,
        model: type[Any],
        *,
        allowed_sort_fields: tuple[str, ...],
        default_date_order: bool = False,
    ) -> Any:
        if params.sort:
            if params.sort not in allowed_sort_fields or not hasattr(model, params.sort):
                raise ValueError(f"Champ de tri Google Analytics non autorise: {params.sort}.")
            sort_column = getattr(model, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        elif default_date_order and hasattr(model, "date"):
            statement = statement.order_by(model.date.desc(), model.id.desc())
        else:
            statement = statement.order_by(model.id.desc())
        return statement.offset(params.offset).limit(params.page_size)

    def _metric_filters(
        self,
        *,
        website_id: int | None = None,
        property_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        import_id: int | None = None,
        source: str | None = None,
        medium: str | None = None,
        campaign: str | None = None,
        device_category: str | None = None,
        country: str | None = None,
        search: str | None = None,
    ) -> list[Any]:
        filters = []
        if website_id is not None:
            filters.append(GoogleAnalyticsProperty.website_id == website_id)
        if property_id is not None:
            filters.append(GoogleAnalyticsMetric.property_id == property_id)
        if date_from is not None:
            filters.append(GoogleAnalyticsMetric.date >= date_from)
        if date_to is not None:
            filters.append(GoogleAnalyticsMetric.date <= date_to)
        if import_id is not None:
            filters.append(GoogleAnalyticsMetric.import_id == import_id)
        if source is not None:
            filters.append(GoogleAnalyticsMetric.source == source)
        if medium is not None:
            filters.append(GoogleAnalyticsMetric.medium == medium)
        if campaign is not None:
            filters.append(GoogleAnalyticsMetric.campaign == campaign)
        if device_category is not None:
            filters.append(GoogleAnalyticsMetric.device_category == device_category)
        if country is not None:
            filters.append(GoogleAnalyticsMetric.country == country)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    GoogleAnalyticsMetric.source.ilike(like_pattern),
                    GoogleAnalyticsMetric.medium.ilike(like_pattern),
                    GoogleAnalyticsMetric.campaign.ilike(like_pattern),
                    GoogleAnalyticsMetric.device_category.ilike(like_pattern),
                    GoogleAnalyticsMetric.country.ilike(like_pattern),
                    GoogleAnalyticsProperty.property_id.ilike(like_pattern),
                    GoogleAnalyticsProperty.property_name.ilike(like_pattern),
                ),
            )
        return filters

    def _import_filters(
        self,
        *,
        property_id: int | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[Any]:
        filters = []
        if property_id is not None:
            filters.append(GoogleAnalyticsImport.property_id == property_id)
        if status is not None:
            filters.append(GoogleAnalyticsImport.status == status)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    GoogleAnalyticsImport.status.ilike(like_pattern),
                    GoogleAnalyticsImport.error_message.ilike(like_pattern),
                    GoogleAnalyticsProperty.property_id.ilike(like_pattern),
                    GoogleAnalyticsProperty.property_name.ilike(like_pattern),
                ),
            )
        return filters
