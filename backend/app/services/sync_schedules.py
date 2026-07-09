"""Business service for synchronization schedules."""

from calendar import monthrange
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from math import ceil
from typing import TypeVar

from fastapi import HTTPException, status

from backend.app.models import SyncSchedule
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.sync_schedules import (
    SyncFrequency,
    SyncScheduleCreate,
    SyncScheduleFilters,
    SyncScheduleList,
    SyncScheduleRead,
    SyncScheduleStatus,
    SyncScheduleUpdate,
)

RepositoryResult = TypeVar("RepositoryResult")


class SyncScheduleService:
    """Manage synchronization schedule configuration and computed dates."""

    def __init__(
        self,
        repository: SyncScheduleRepository,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.now_provider = now_provider or (lambda: datetime.now(UTC))

    def list_schedules(
        self,
        params: PaginationParams,
        *,
        filters: SyncScheduleFilters | None = None,
    ) -> SyncScheduleList:
        """Return paginated synchronization schedules."""

        filters = self._normalize_filters(filters or SyncScheduleFilters())
        values = self._filters_dict(filters)
        items, total = self._repository_result(self.repository.list_schedules, params, **values)
        return SyncScheduleList(
            items=[SyncScheduleRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=self._filters_dict(filters),
        )

    def create_schedule(
        self,
        payload: SyncScheduleCreate,
        *,
        user_id: int | None = None,
    ) -> SyncScheduleRead:
        """Create a synchronization schedule."""

        data = self._clean_data(payload.model_dump())
        data["status"] = self._initial_status(payload.is_active, payload.frequency).value
        data["next_run_at"] = self.calculate_next_run(
            frequency=payload.frequency,
            is_active=payload.is_active,
            last_run_at=None,
            reference_at=self._now(),
        )
        data["created_by_user_id"] = user_id
        data["updated_by_user_id"] = user_id
        item = self.repository.create_schedule(data)
        return SyncScheduleRead.model_validate(item)

    def get_schedule(self, schedule_id: int) -> SyncScheduleRead:
        """Return one synchronization schedule."""

        return SyncScheduleRead.model_validate(self._get_schedule_model(schedule_id))

    def update_schedule(
        self,
        schedule_id: int,
        payload: SyncScheduleUpdate,
        *,
        user_id: int | None = None,
    ) -> SyncScheduleRead:
        """Update a synchronization schedule and recompute its next run."""

        item = self._get_schedule_model(schedule_id)
        data = self._clean_data(payload.model_dump(exclude_unset=True))
        is_active = bool(data.get("is_active", item.is_active))
        frequency = SyncFrequency(data.get("frequency", item.frequency))
        last_run_at = data.get("last_run_at", item.last_run_at)
        data["next_run_at"] = self.calculate_next_run(
            frequency=frequency,
            is_active=is_active,
            last_run_at=last_run_at,
            reference_at=self._now(),
        )
        if "is_active" in data and not is_active:
            data["status"] = SyncScheduleStatus.DISABLED.value
        elif "is_active" in data and is_active and data.get("status") == SyncScheduleStatus.DISABLED.value:
            data["status"] = self._initial_status(True, frequency).value
        data["updated_by_user_id"] = user_id
        updated = self.repository.update_schedule(item, data)
        return SyncScheduleRead.model_validate(updated)

    def delete_schedule(self, schedule_id: int, *, user_id: int | None = None) -> None:
        """Soft-disable a synchronization schedule."""

        self.disable_schedule(schedule_id, user_id=user_id)

    def enable_schedule(self, schedule_id: int, *, user_id: int | None = None) -> SyncScheduleRead:
        """Enable a synchronization schedule."""

        item = self._get_schedule_model(schedule_id)
        frequency = SyncFrequency(item.frequency)
        data = {
            "is_active": True,
            "status": self._initial_status(True, frequency).value,
            "next_run_at": self.calculate_next_run(
                frequency=frequency,
                is_active=True,
                last_run_at=item.last_run_at,
                reference_at=self._now(),
            ),
            "updated_by_user_id": user_id,
        }
        updated = self.repository.update_schedule(item, data)
        return SyncScheduleRead.model_validate(updated)

    def disable_schedule(self, schedule_id: int, *, user_id: int | None = None) -> SyncScheduleRead:
        """Disable a synchronization schedule without deleting it."""

        item = self._get_schedule_model(schedule_id)
        updated = self.repository.disable_schedule(
            item,
            {
                "is_active": False,
                "status": SyncScheduleStatus.DISABLED.value,
                "next_run_at": None,
                "updated_by_user_id": user_id,
            },
        )
        return SyncScheduleRead.model_validate(updated)

    def recalculate_schedule(self, schedule_id: int, *, user_id: int | None = None) -> SyncScheduleRead:
        """Recalculate the next theoretical execution date."""

        item = self._get_schedule_model(schedule_id)
        data = {
            "next_run_at": self.calculate_next_run(
                frequency=SyncFrequency(item.frequency),
                is_active=item.is_active,
                last_run_at=item.last_run_at,
                reference_at=self._now(),
            ),
            "updated_by_user_id": user_id,
        }
        updated = self.repository.update_schedule(item, data)
        return SyncScheduleRead.model_validate(updated)

    def calculate_next_run(
        self,
        *,
        frequency: SyncFrequency,
        is_active: bool,
        last_run_at: datetime | None,
        reference_at: datetime,
    ) -> datetime | None:
        """Return the next theoretical execution date for a schedule."""

        if not is_active or frequency == SyncFrequency.MANUAL:
            return None
        base = last_run_at or reference_at
        if frequency == SyncFrequency.HOURLY:
            return base + timedelta(hours=1)
        if frequency == SyncFrequency.DAILY:
            return base + timedelta(days=1)
        if frequency == SyncFrequency.WEEKLY:
            return base + timedelta(weeks=1)
        if frequency == SyncFrequency.MONTHLY:
            return self._add_month(base)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Frequence de planification non supportee.",
        )

    def _get_schedule_model(self, schedule_id: int) -> SyncSchedule:
        item = self.repository.get_schedule(schedule_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planification introuvable.")
        return item

    def _initial_status(self, is_active: bool, frequency: SyncFrequency) -> SyncScheduleStatus:
        if not is_active:
            return SyncScheduleStatus.DISABLED
        if frequency == SyncFrequency.MANUAL:
            return SyncScheduleStatus.PENDING
        return SyncScheduleStatus.ACTIVE

    def _normalize_filters(self, filters: SyncScheduleFilters) -> SyncScheduleFilters:
        if filters.next_run_from is not None and filters.next_run_to is not None:
            if filters.next_run_to < filters.next_run_from:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="La date de fin doit etre superieure ou egale a la date de debut.",
                )
        return SyncScheduleFilters(
            sync_type=filters.sync_type,
            frequency=filters.frequency,
            status=filters.status,
            is_active=filters.is_active,
            website_id=filters.website_id,
            next_run_from=filters.next_run_from,
            next_run_to=filters.next_run_to,
            search=self._clean_text(filters.search),
        )

    def _filters_dict(self, filters: SyncScheduleFilters) -> dict[str, object]:
        return filters.model_dump(mode="json", exclude_none=True)

    def _clean_data(self, data: dict[str, object]) -> dict[str, object]:
        cleaned = data.copy()
        for key in ("name", "description", "target_id", "target_type", "last_run_message", "timezone"):
            if key in cleaned and isinstance(cleaned[key], str):
                cleaned[key] = self._clean_text(cleaned[key])
        for key in ("sync_type", "frequency", "status", "last_run_status"):
            value = cleaned.get(key)
            if hasattr(value, "value"):
                cleaned[key] = value.value
        return cleaned

    def _repository_result(
        self,
        repository_method: Callable[..., RepositoryResult],
        *args: object,
        **kwargs: object,
    ) -> RepositoryResult:
        try:
            return repository_method(*args, **kwargs)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    def _clean_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _now(self) -> datetime:
        value = self.now_provider()
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value

    def _add_month(self, value: datetime) -> datetime:
        month = value.month + 1
        year = value.year
        if month > 12:
            month = 1
            year += 1
        day = min(value.day, monthrange(year, month)[1])
        return value.replace(year=year, month=month, day=day)

