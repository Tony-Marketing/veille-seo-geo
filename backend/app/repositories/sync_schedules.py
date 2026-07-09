"""Repository for synchronization schedules."""

from datetime import datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.models import SyncSchedule
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class SyncScheduleRepository(BaseRepository[SyncSchedule]):
    """Encapsulate SQLAlchemy persistence for synchronization schedules."""

    search_fields = ("name", "description", "target_id", "target_type", "last_run_message")
    sort_fields = (
        "id",
        "name",
        "sync_type",
        "frequency",
        "status",
        "is_active",
        "website_id",
        "last_run_at",
        "last_run_status",
        "next_run_at",
        "created_at",
        "updated_at",
    )

    def __init__(self, db: Session) -> None:
        super().__init__(db, SyncSchedule)

    def get_schedule(self, schedule_id: int) -> SyncSchedule | None:
        """Return a schedule by primary key."""

        return self.db.get(SyncSchedule, schedule_id)

    def list_schedules(
        self,
        params: PaginationParams,
        *,
        sync_type: str | None = None,
        frequency: str | None = None,
        status: str | None = None,
        is_active: bool | None = None,
        website_id: int | None = None,
        next_run_from: datetime | None = None,
        next_run_to: datetime | None = None,
        search: str | None = None,
    ) -> tuple[list[SyncSchedule], int]:
        """Return paginated schedules with optional filters."""

        statement = select(SyncSchedule)
        count_statement = select(func.count()).select_from(SyncSchedule)
        filters = self._filters(
            sync_type=sync_type,
            frequency=frequency,
            status=status,
            is_active=is_active,
            website_id=website_id,
            next_run_from=next_run_from,
            next_run_to=next_run_to,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(statement, params)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def create_schedule(self, data: dict[str, Any]) -> SyncSchedule:
        """Persist a new schedule."""

        return self.create(data)

    def update_schedule(self, item: SyncSchedule, data: dict[str, Any]) -> SyncSchedule:
        """Update a schedule."""

        return self.update(item, data)

    def disable_schedule(self, item: SyncSchedule, data: dict[str, Any]) -> SyncSchedule:
        """Soft-disable a schedule without deleting it."""

        return self.update(item, data)

    def _order_and_page(self, statement: Any, params: PaginationParams) -> Any:
        if params.sort:
            if params.sort not in self.sort_fields or not hasattr(SyncSchedule, params.sort):
                raise ValueError(f"Champ de tri planification non autorise: {params.sort}.")
            sort_column = getattr(SyncSchedule, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(SyncSchedule.id.desc())
        return statement.offset(params.offset).limit(params.page_size)

    def _filters(
        self,
        *,
        sync_type: str | None,
        frequency: str | None,
        status: str | None,
        is_active: bool | None,
        website_id: int | None,
        next_run_from: datetime | None,
        next_run_to: datetime | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if sync_type is not None:
            filters.append(SyncSchedule.sync_type == sync_type)
        if frequency is not None:
            filters.append(SyncSchedule.frequency == frequency)
        if status is not None:
            filters.append(SyncSchedule.status == status)
        if is_active is not None:
            filters.append(SyncSchedule.is_active == is_active)
        if website_id is not None:
            filters.append(SyncSchedule.website_id == website_id)
        if next_run_from is not None:
            filters.append(SyncSchedule.next_run_at >= next_run_from)
        if next_run_to is not None:
            filters.append(SyncSchedule.next_run_at <= next_run_to)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    SyncSchedule.name.ilike(like_pattern),
                    SyncSchedule.description.ilike(like_pattern),
                    SyncSchedule.target_id.ilike(like_pattern),
                    SyncSchedule.target_type.ilike(like_pattern),
                    SyncSchedule.last_run_message.ilike(like_pattern),
                ),
            )
        return filters

