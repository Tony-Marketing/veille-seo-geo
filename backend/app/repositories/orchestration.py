"""Repository for processing orchestration."""

from datetime import datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.models import ProcessingJob, ProcessingJobLog, ProcessingWorker, SyncSchedule
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.orchestration import ProcessingJobStatus
from backend.app.schemas.pagination import PaginationParams


class OrchestrationRepository(BaseRepository[ProcessingJob]):
    """Encapsulate SQLAlchemy persistence for processing jobs."""

    sort_fields = (
        "id",
        "schedule_id",
        "job_type",
        "status",
        "priority",
        "attempts",
        "available_at",
        "reserved_at",
        "started_at",
        "finished_at",
        "failed_at",
        "created_at",
        "updated_at",
    )

    terminal_statuses = (
        ProcessingJobStatus.SUCCEEDED.value,
        ProcessingJobStatus.FAILED.value,
        ProcessingJobStatus.CANCELLED.value,
    )

    def __init__(self, db: Session) -> None:
        super().__init__(db, ProcessingJob)

    def get_job(self, job_id: int) -> ProcessingJob | None:
        """Return one processing job."""

        return self.db.get(ProcessingJob, job_id)

    def get_job_by_idempotency_key(self, idempotency_key: str) -> ProcessingJob | None:
        """Return a job matching the idempotency key."""

        return self.db.scalar(select(ProcessingJob).where(ProcessingJob.idempotency_key == idempotency_key))

    def list_jobs(
        self,
        params: PaginationParams,
        *,
        status: str | None = None,
        job_type: str | None = None,
        schedule_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
    ) -> tuple[list[ProcessingJob], int]:
        """Return paginated jobs with optional filters."""

        statement = select(ProcessingJob)
        count_statement = select(func.count()).select_from(ProcessingJob)
        filters = self._filters(
            status=status,
            job_type=job_type,
            schedule_id=schedule_id,
            created_from=created_from,
            created_to=created_to,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(statement, params)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def create_job(self, data: dict[str, Any]) -> ProcessingJob:
        """Persist a new processing job."""

        return self.create(data)

    def update_job(self, item: ProcessingJob, data: dict[str, Any]) -> ProcessingJob:
        """Update a processing job."""

        return self.update(item, data)

    def create_log(self, data: dict[str, Any]) -> ProcessingJobLog:
        """Persist a controlled job log."""

        item = ProcessingJobLog(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_logs(self, job_id: int, params: PaginationParams) -> tuple[list[ProcessingJobLog], int]:
        """Return paginated logs for one job."""

        statement = select(ProcessingJobLog).where(ProcessingJobLog.job_id == job_id)
        count_statement = select(func.count()).select_from(ProcessingJobLog).where(ProcessingJobLog.job_id == job_id)
        statement = statement.order_by(ProcessingJobLog.created_at.asc(), ProcessingJobLog.id.asc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def list_due_schedules(self, now: datetime, *, limit: int = 100) -> list[SyncSchedule]:
        """Return active schedules due for execution."""

        statement = (
            select(SyncSchedule)
            .where(
                SyncSchedule.is_active.is_(True),
                SyncSchedule.next_run_at.is_not(None),
                SyncSchedule.next_run_at <= now,
            )
            .order_by(SyncSchedule.next_run_at.asc(), SyncSchedule.id.asc())
            .limit(limit)
        )
        return list(self.db.scalars(statement))

    def update_schedule(self, item: SyncSchedule, data: dict[str, Any]) -> SyncSchedule:
        """Update a synchronization schedule from orchestration logic."""

        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def reserve_next_job(
        self,
        *,
        worker_id: str,
        now: datetime,
        lock_expires_at: datetime,
    ) -> ProcessingJob | None:
        """Reserve the next available job atomically where supported by the database."""

        statement = (
            select(ProcessingJob)
            .where(
                ProcessingJob.status.in_(
                    [ProcessingJobStatus.PENDING.value, ProcessingJobStatus.RETRY_SCHEDULED.value],
                ),
                ProcessingJob.available_at <= now,
            )
            .order_by(ProcessingJob.priority.asc(), ProcessingJob.available_at.asc(), ProcessingJob.id.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        item = self.db.scalar(statement)
        if item is None:
            return None
        item.status = ProcessingJobStatus.RESERVED.value
        item.reserved_at = now
        item.worker_id = worker_id
        item.lock_expires_at = lock_expires_at
        self.db.commit()
        self.db.refresh(item)
        return item

    def upsert_worker(
        self,
        *,
        worker_id: str,
        status: str,
        last_heartbeat_at: datetime,
        current_job_id: int | None = None,
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProcessingWorker:
        """Create or update one worker heartbeat."""

        item = self.db.scalar(select(ProcessingWorker).where(ProcessingWorker.worker_id == worker_id))
        data = {
            "status": status,
            "last_heartbeat_at": last_heartbeat_at,
            "current_job_id": current_job_id,
            "version": version,
            "metadata_": metadata,
        }
        if item is None:
            item = ProcessingWorker(worker_id=worker_id, **data)
            self.db.add(item)
        else:
            for key, value in data.items():
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_workers(self) -> list[ProcessingWorker]:
        """Return workers ordered by latest heartbeat."""

        statement = select(ProcessingWorker).order_by(ProcessingWorker.last_heartbeat_at.desc())
        return list(self.db.scalars(statement))

    def count_jobs(self, *, status: str | None = None) -> int:
        """Return job count with an optional status filter."""

        statement = select(func.count()).select_from(ProcessingJob)
        if status is not None:
            statement = statement.where(ProcessingJob.status == status)
        return int(self.db.scalar(statement) or 0)

    def count_blocked_jobs(self, now: datetime) -> int:
        """Return jobs whose reservation lock has expired."""

        statement = select(func.count()).select_from(ProcessingJob).where(
            ProcessingJob.status.in_([ProcessingJobStatus.RESERVED.value, ProcessingJobStatus.RUNNING.value]),
            ProcessingJob.lock_expires_at.is_not(None),
            ProcessingJob.lock_expires_at < now,
        )
        return int(self.db.scalar(statement) or 0)

    def get_last_activity_at(self) -> datetime | None:
        """Return the latest job update date."""

        return self.db.scalar(select(func.max(ProcessingJob.updated_at)))

    def _order_and_page(self, statement: Any, params: PaginationParams) -> Any:
        if params.sort:
            if params.sort not in self.sort_fields or not hasattr(ProcessingJob, params.sort):
                raise ValueError(f"Champ de tri orchestration non autorise: {params.sort}.")
            sort_column = getattr(ProcessingJob, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(ProcessingJob.created_at.desc(), ProcessingJob.id.desc())
        return statement.offset(params.offset).limit(params.page_size)

    def _filters(
        self,
        *,
        status: str | None,
        job_type: str | None,
        schedule_id: int | None,
        created_from: datetime | None,
        created_to: datetime | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if status is not None:
            filters.append(ProcessingJob.status == status)
        if job_type is not None:
            filters.append(ProcessingJob.job_type == job_type)
        if schedule_id is not None:
            filters.append(ProcessingJob.schedule_id == schedule_id)
        if created_from is not None:
            filters.append(ProcessingJob.created_at >= created_from)
        if created_to is not None:
            filters.append(ProcessingJob.created_at <= created_to)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    ProcessingJob.message.ilike(like_pattern),
                    ProcessingJob.idempotency_key.ilike(like_pattern),
                    ProcessingJob.job_type.ilike(like_pattern),
                ),
            )
        return filters
