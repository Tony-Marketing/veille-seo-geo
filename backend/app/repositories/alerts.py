"""Repository for alerts."""

from datetime import datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.models import Alert
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class AlertRepository(BaseRepository[Alert]):
    """Encapsulate SQLAlchemy persistence for alerts."""

    sort_fields = (
        "id",
        "source_type",
        "category",
        "severity",
        "status",
        "first_seen_at",
        "last_seen_at",
        "acknowledged_at",
        "resolved_at",
        "created_at",
        "updated_at",
    )

    def __init__(self, db: Session) -> None:
        super().__init__(db, Alert)

    def get_alert(self, alert_id: int) -> Alert | None:
        """Return one alert by primary key."""

        return self.db.get(Alert, alert_id)

    def list_alerts(
        self,
        params: PaginationParams,
        *,
        status: str | None = None,
        severity: str | None = None,
        category: str | None = None,
        source_type: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Alert], int]:
        """Return paginated alerts with optional filters."""

        statement = select(Alert)
        count_statement = select(func.count()).select_from(Alert)
        filters = self._filters(
            status=status,
            severity=severity,
            category=category,
            source_type=source_type,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(statement, params)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def create_alert(self, data: dict[str, Any]) -> Alert:
        """Persist a new alert."""

        return self.create(data)

    def update_alert(self, item: Alert, data: dict[str, Any]) -> Alert:
        """Update an alert."""

        return self.update(item, data)

    def get_active_by_deduplication_key(self, deduplication_key: str) -> Alert | None:
        """Return one active or acknowledged alert for a functional cause."""

        statement = select(Alert).where(
            Alert.deduplication_key == deduplication_key,
            Alert.status.in_(("Active", "Acknowledged")),
        )
        return self.db.scalar(statement)

    def count_alerts(self, *, status: str | None = None, severity: str | None = None) -> int:
        """Return alert count with optional filters."""

        statement = select(func.count()).select_from(Alert)
        filters = []
        if status is not None:
            filters.append(Alert.status == status)
        if severity is not None:
            filters.append(Alert.severity == severity)
        if filters:
            statement = statement.where(*filters)
        return int(self.db.scalar(statement) or 0)

    def get_last_alert_seen_at(self) -> datetime | None:
        """Return the latest alert observation date."""

        return self.db.scalar(select(func.max(Alert.last_seen_at)))

    def _order_and_page(self, statement: Any, params: PaginationParams) -> Any:
        if params.sort:
            if params.sort not in self.sort_fields or not hasattr(Alert, params.sort):
                raise ValueError(f"Champ de tri alerte non autorise: {params.sort}.")
            sort_column = getattr(Alert, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(Alert.last_seen_at.desc(), Alert.id.desc())
        return statement.offset(params.offset).limit(params.page_size)

    def _filters(
        self,
        *,
        status: str | None,
        severity: str | None,
        category: str | None,
        source_type: str | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if status is not None:
            filters.append(Alert.status == status)
        if severity is not None:
            filters.append(Alert.severity == severity)
        if category is not None:
            filters.append(Alert.category == category)
        if source_type is not None:
            filters.append(Alert.source_type == source_type)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    Alert.title.ilike(like_pattern),
                    Alert.message.ilike(like_pattern),
                    Alert.source_type.ilike(like_pattern),
                    Alert.category.ilike(like_pattern),
                ),
            )
        return filters
