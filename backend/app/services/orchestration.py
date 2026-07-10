"""Business service for processing orchestration."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from math import ceil
from typing import Any

from fastapi import HTTPException, status

from backend.app.models import ProcessingJob, SyncSchedule
from backend.app.orchestration.registry import ProcessingHandlerRegistry
from backend.app.repositories.alerts import AlertRepository
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.repositories.orchestration import OrchestrationRepository
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.alerts import AlertRefreshResult
from backend.app.schemas.monitoring import MonitoringEventType, MonitoringSeverity
from backend.app.schemas.orchestration import (
    ProcessingJobFilters,
    ProcessingJobList,
    ProcessingJobLogList,
    ProcessingJobLogRead,
    ProcessingJobRead,
    ProcessingJobStatus,
    ProcessingJobType,
    ProcessingLogLevel,
    ProcessingSummary,
    ProcessingWorkerRead,
    ProcessingWorkerStatus,
    SchedulerRunResult,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.sync_schedules import SyncFrequency, SyncScheduleStatus, SyncType
from backend.app.services.alerts import AlertService
from backend.app.services.sync_schedules import SyncScheduleService

DEFAULT_LOCK_MINUTES = 15
DEFAULT_RETRY_MINUTES = 5
DEFAULT_MAX_ATTEMPTS = 3
SCHEDULER_BATCH_SIZE = 100


class OrchestrationService:
    """Coordinate scheduled jobs, workers, monitoring and alerts."""

    def __init__(
        self,
        repository: OrchestrationRepository,
        sync_schedule_repository: SyncScheduleRepository,
        monitoring_repository: MonitoringRepository,
        alert_repository: AlertRepository,
        *,
        handler_registry: ProcessingHandlerRegistry | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.sync_schedule_repository = sync_schedule_repository
        self.monitoring_repository = monitoring_repository
        self.alert_repository = alert_repository
        self.handler_registry = handler_registry or ProcessingHandlerRegistry()
        self.now_provider = now_provider or (lambda: datetime.now(UTC))

    def list_jobs(self, params: PaginationParams, *, filters: ProcessingJobFilters | None = None) -> ProcessingJobList:
        """Return paginated processing jobs."""

        filters = self._normalize_filters(filters or ProcessingJobFilters())
        values = self._filters_dict(filters)
        items, total = self._repository_result(self.repository.list_jobs, params, **values)
        return ProcessingJobList(
            items=[ProcessingJobRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=values,
        )

    def get_job(self, job_id: int) -> ProcessingJobRead:
        """Return one processing job."""

        return ProcessingJobRead.model_validate(self._get_job_model(job_id))

    def list_job_logs(self, job_id: int, params: PaginationParams) -> ProcessingJobLogList:
        """Return paginated logs for one job."""

        self._get_job_model(job_id)
        items, total = self.repository.list_logs(job_id, params)
        return ProcessingJobLogList(
            items=[ProcessingJobLogRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters={"job_id": job_id},
        )

    def summary(self) -> ProcessingSummary:
        """Return global orchestration counters."""

        now = self._now()
        return ProcessingSummary(
            pending=self.repository.count_jobs(status=ProcessingJobStatus.PENDING.value),
            reserved=self.repository.count_jobs(status=ProcessingJobStatus.RESERVED.value),
            running=self.repository.count_jobs(status=ProcessingJobStatus.RUNNING.value),
            retry_scheduled=self.repository.count_jobs(status=ProcessingJobStatus.RETRY_SCHEDULED.value),
            succeeded=self.repository.count_jobs(status=ProcessingJobStatus.SUCCEEDED.value),
            failed=self.repository.count_jobs(status=ProcessingJobStatus.FAILED.value),
            cancelled=self.repository.count_jobs(status=ProcessingJobStatus.CANCELLED.value),
            blocked=self.repository.count_blocked_jobs(now),
            total=self.repository.count_jobs(),
            last_activity_at=self.repository.get_last_activity_at(),
            active_workers=len(
                [
                    worker
                    for worker in self.repository.list_workers()
                    if worker.status != ProcessingWorkerStatus.STOPPED.value
                ],
            ),
        )

    def list_workers(self) -> list[ProcessingWorkerRead]:
        """Return known worker heartbeats."""

        return [ProcessingWorkerRead.model_validate(item) for item in self.repository.list_workers()]

    def run_scheduler_once(self) -> SchedulerRunResult:
        """Create jobs for due synchronization schedules without executing them."""

        now = self._now()
        schedules = self.repository.list_due_schedules(now, limit=SCHEDULER_BATCH_SIZE)
        created_jobs: list[ProcessingJob] = []
        skipped = 0
        errors = 0
        for schedule in schedules:
            try:
                job = self._create_job_from_schedule(schedule, now)
            except Exception as exc:  # noqa: BLE001 - converted to monitoring event below.
                errors += 1
                self._create_monitoring_event(
                    severity=MonitoringSeverity.ERROR,
                    message="Creation du job de planification impossible.",
                    details={"schedule_id": schedule.id, "error": self._safe_message(str(exc))},
                )
                continue
            if job is None:
                skipped += 1
            else:
                created_jobs.append(job)
        return SchedulerRunResult(
            scanned=len(schedules),
            created=len(created_jobs),
            skipped=skipped,
            errors=errors,
            jobs=[ProcessingJobRead.model_validate(item) for item in created_jobs],
        )

    def reserve_next_job(self, *, worker_id: str) -> ProcessingJobRead | None:
        """Reserve the next available job for a worker."""

        now = self._now()
        worker = self.repository.upsert_worker(
            worker_id=worker_id,
            status=ProcessingWorkerStatus.IDLE.value,
            last_heartbeat_at=now,
        )
        item = self.repository.reserve_next_job(
            worker_id=worker.worker_id,
            now=now,
            lock_expires_at=now + timedelta(minutes=DEFAULT_LOCK_MINUTES),
        )
        if item is None:
            return None
        self.repository.upsert_worker(
            worker_id=worker_id,
            status=ProcessingWorkerStatus.RUNNING.value,
            last_heartbeat_at=now,
            current_job_id=item.id,
        )
        self._log(item.id, ProcessingLogLevel.INFO, "reserved", "Job reserve par le worker.", {"worker_id": worker_id})
        return ProcessingJobRead.model_validate(item)

    def run_next_job(self, *, worker_id: str) -> ProcessingJobRead | None:
        """Reserve and execute one job."""

        reserved = self.reserve_next_job(worker_id=worker_id)
        if reserved is None:
            return None
        return self.run_reserved_job(reserved.id, worker_id=worker_id)

    def run_reserved_job(self, job_id: int, *, worker_id: str) -> ProcessingJobRead:
        """Execute a reserved job by id."""

        job = self._get_job_model(job_id)
        if job.status != ProcessingJobStatus.RESERVED.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Le job n'est pas reserve.")

        now = self._now()
        job = self.repository.update_job(
            job,
            {
                "status": ProcessingJobStatus.RUNNING.value,
                "started_at": now,
                "attempts": job.attempts + 1,
                "worker_id": worker_id,
                "lock_expires_at": now + timedelta(minutes=DEFAULT_LOCK_MINUTES),
            },
        )
        self._log(job.id, ProcessingLogLevel.INFO, "started", "Execution du job demarree.", {"worker_id": worker_id})

        handler = self.handler_registry.get(job.job_type)
        try:
            result = handler.run(self._payload(job), self.repository.db)
        except Exception as exc:  # noqa: BLE001 - worker must turn unexpected errors into failed jobs.
            result = self._unexpected_handler_result(exc)

        if result.success:
            updated = self._succeed_job(job, message=result.message, details=result.details)
        elif result.retryable and job.attempts < job.max_attempts:
            updated = self._schedule_retry(job, message=result.message, details=result.details)
        else:
            updated = self._fail_job(job, message=result.message, details=result.details)

        self.repository.upsert_worker(
            worker_id=worker_id,
            status=ProcessingWorkerStatus.IDLE.value,
            last_heartbeat_at=self._now(),
            current_job_id=None,
        )
        return ProcessingJobRead.model_validate(updated)

    def retry_job(self, job_id: int) -> ProcessingJobRead:
        """Schedule a failed job for a controlled retry."""

        item = self._get_job_model(job_id)
        if item.status not in {ProcessingJobStatus.FAILED.value, ProcessingJobStatus.RETRY_SCHEDULED.value}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Ce job ne peut pas etre relance.",
            )
        now = self._now()
        updated = self.repository.update_job(
            item,
            {
                "status": ProcessingJobStatus.RETRY_SCHEDULED.value,
                "available_at": now,
                "reserved_at": None,
                "started_at": None,
                "finished_at": None,
                "failed_at": None,
                "worker_id": None,
                "lock_expires_at": None,
                "message": "Relance demandee par un administrateur.",
            },
        )
        self._log(item.id, ProcessingLogLevel.INFO, "retry_requested", "Relance administrative demandee.", None)
        return ProcessingJobRead.model_validate(updated)

    def cancel_job(self, job_id: int) -> ProcessingJobRead:
        """Cancel a job that has not reached a final non-cancellable state."""

        item = self._get_job_model(job_id)
        if item.status in {
            ProcessingJobStatus.RUNNING.value,
            ProcessingJobStatus.SUCCEEDED.value,
            ProcessingJobStatus.FAILED.value,
            ProcessingJobStatus.CANCELLED.value,
        }:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Ce job ne peut pas etre annule.",
            )
        updated = self.repository.update_job(
            item,
            {
                "status": ProcessingJobStatus.CANCELLED.value,
                "finished_at": self._now(),
                "message": "Job annule par un administrateur.",
                "worker_id": None,
                "lock_expires_at": None,
            },
        )
        self._log(item.id, ProcessingLogLevel.WARNING, "cancelled", "Job annule par un administrateur.", None)
        self._create_monitoring_event(
            severity=MonitoringSeverity.WARNING,
            message="Job d'orchestration annule.",
            details={"job_id": item.id, "job_type": item.job_type},
        )
        return ProcessingJobRead.model_validate(updated)

    def _create_job_from_schedule(self, schedule: SyncSchedule, now: datetime) -> ProcessingJob | None:
        job_type = self._job_type_for_schedule(schedule)
        if job_type is None:
            self._create_monitoring_event(
                severity=MonitoringSeverity.WARNING,
                message="Type de planification non supporte par l'orchestrateur.",
                details={"schedule_id": schedule.id, "sync_type": schedule.sync_type},
            )
            return None

        scheduled_for = self._as_aware(schedule.next_run_at or now)
        idempotency_key = f"schedule:{schedule.id}:{job_type.value}:{scheduled_for.isoformat()}"
        existing = self.repository.get_job_by_idempotency_key(idempotency_key)
        if existing is not None:
            return None

        job = self.repository.create_job(
            {
                "schedule_id": schedule.id,
                "job_type": job_type.value,
                "status": ProcessingJobStatus.PENDING.value,
                "priority": 100,
                "payload": self._schedule_payload(schedule, scheduled_for),
                "idempotency_key": idempotency_key,
                "attempts": 0,
                "max_attempts": DEFAULT_MAX_ATTEMPTS,
                "available_at": now,
                "message": "Job cree depuis une planification.",
            },
        )
        next_run_at = self._next_schedule_run(schedule, scheduled_for, now)
        self.repository.update_schedule(
            schedule,
            {
                "status": SyncScheduleStatus.PENDING.value,
                "next_run_at": next_run_at,
            },
        )
        self._log(
            job.id,
            ProcessingLogLevel.INFO,
            "created",
            "Job cree par le scheduler.",
            {"schedule_id": schedule.id},
        )
        self._create_monitoring_event(
            severity=MonitoringSeverity.INFO,
            message="Job d'orchestration cree depuis une planification.",
            details={"job_id": job.id, "schedule_id": schedule.id, "job_type": job.job_type},
        )
        return job

    def _succeed_job(self, job: ProcessingJob, *, message: str, details: dict[str, Any]) -> ProcessingJob:
        now = self._now()
        monitoring_event = self._create_monitoring_event(
            severity=MonitoringSeverity.INFO,
            message=message,
            details={"job_id": job.id, "job_type": job.job_type, **self._safe_metadata(details)},
        )
        updated = self.repository.update_job(
            job,
            {
                "status": ProcessingJobStatus.SUCCEEDED.value,
                "finished_at": now,
                "message": message,
                "details": self._safe_metadata(details),
                "lock_expires_at": None,
                "monitoring_event_id": monitoring_event.id,
            },
        )
        self._update_schedule_after_execution(updated, success=True, message=message)
        self._log(job.id, ProcessingLogLevel.INFO, "succeeded", message, details)
        self._refresh_alerts()
        return updated

    def _schedule_retry(self, job: ProcessingJob, *, message: str, details: dict[str, Any]) -> ProcessingJob:
        now = self._now()
        available_at = now + timedelta(minutes=DEFAULT_RETRY_MINUTES * max(job.attempts, 1))
        updated = self.repository.update_job(
            job,
            {
                "status": ProcessingJobStatus.RETRY_SCHEDULED.value,
                "available_at": available_at,
                "failed_at": now,
                "message": message,
                "details": self._safe_metadata(details),
                "worker_id": None,
                "lock_expires_at": None,
            },
        )
        self._log(job.id, ProcessingLogLevel.WARNING, "retry_scheduled", message, details)
        self._create_monitoring_event(
            severity=MonitoringSeverity.WARNING,
            message="Retry planifie pour un job d'orchestration.",
            details={"job_id": job.id, "job_type": job.job_type, "available_at": available_at.isoformat()},
        )
        self._refresh_alerts()
        return updated

    def _fail_job(self, job: ProcessingJob, *, message: str, details: dict[str, Any]) -> ProcessingJob:
        now = self._now()
        monitoring_event = self._create_monitoring_event(
            severity=MonitoringSeverity.ERROR,
            message=message,
            details={"job_id": job.id, "job_type": job.job_type, **self._safe_metadata(details)},
        )
        updated = self.repository.update_job(
            job,
            {
                "status": ProcessingJobStatus.FAILED.value,
                "failed_at": now,
                "finished_at": now,
                "message": message,
                "details": self._safe_metadata(details),
                "worker_id": None,
                "lock_expires_at": None,
                "monitoring_event_id": monitoring_event.id,
            },
        )
        self._update_schedule_after_execution(updated, success=False, message=message)
        self._log(job.id, ProcessingLogLevel.ERROR, "failed", message, details)
        self._refresh_alerts()
        return updated

    def _update_schedule_after_execution(self, job: ProcessingJob, *, success: bool, message: str) -> None:
        if job.schedule_id is None:
            return
        schedule = self.sync_schedule_repository.get_schedule(job.schedule_id)
        if schedule is None:
            return
        self.repository.update_schedule(
            schedule,
            {
                "last_run_at": self._now(),
                "last_run_status": SyncScheduleStatus.ACTIVE.value if success else SyncScheduleStatus.ERROR.value,
                "last_run_message": self._safe_message(message),
                "status": (
                    SyncScheduleStatus.ACTIVE.value
                    if success and schedule.is_active
                    else SyncScheduleStatus.ERROR.value
                ),
            },
        )

    def _create_monitoring_event(
        self,
        *,
        severity: MonitoringSeverity,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> Any:
        return self.monitoring_repository.create_event(
            {
                "event_type": MonitoringEventType.SYNC.value,
                "severity": severity.value,
                "source": "orchestration",
                "message": self._safe_message(message),
                "details": self._safe_metadata(details or {}),
            },
        )

    def _refresh_alerts(self) -> AlertRefreshResult:
        return AlertService(
            self.alert_repository,
            self.monitoring_repository,
            now_provider=self.now_provider,
        ).refresh_from_monitoring()

    def _log(
        self,
        job_id: int,
        level: ProcessingLogLevel,
        event: str,
        message: str,
        context: dict[str, Any] | None,
    ) -> None:
        self.repository.create_log(
            {
                "job_id": job_id,
                "level": level.value,
                "event": event,
                "message": self._safe_message(message),
                "context": self._safe_metadata(context or {}),
            },
        )

    def _job_type_for_schedule(self, schedule: SyncSchedule) -> ProcessingJobType | None:
        mapping = {
            SyncType.GSC.value: ProcessingJobType.GSC,
            SyncType.GA4.value: ProcessingJobType.GA4,
            SyncType.BING.value: ProcessingJobType.BING,
            SyncType.CRAWL.value: ProcessingJobType.CRAWL,
            SyncType.SEO.value: ProcessingJobType.SEO_ANALYSIS,
            SyncType.GEO.value: ProcessingJobType.GEO_ANALYSIS,
        }
        return mapping.get(schedule.sync_type)

    def _schedule_payload(self, schedule: SyncSchedule, scheduled_for: datetime) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schedule_id": schedule.id,
            "sync_type": schedule.sync_type,
            "target_id": schedule.target_id,
            "target_type": schedule.target_type,
            "website_id": schedule.website_id,
            "scheduled_for": scheduled_for.isoformat(),
        }
        if schedule.target_id is None:
            payload["missing_target"] = True
        return payload

    def _next_schedule_run(self, schedule: SyncSchedule, scheduled_for: datetime, now: datetime) -> datetime | None:
        service = SyncScheduleService(self.sync_schedule_repository, now_provider=lambda: now)
        return service.calculate_next_run(
            frequency=SyncFrequency(schedule.frequency),
            is_active=schedule.is_active,
            last_run_at=scheduled_for,
            reference_at=now,
        )

    def _get_job_model(self, job_id: int) -> ProcessingJob:
        item = self.repository.get_job(job_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job d'orchestration introuvable.")
        return item

    def _normalize_filters(self, filters: ProcessingJobFilters) -> ProcessingJobFilters:
        if filters.created_from is not None and filters.created_to is not None:
            if filters.created_to < filters.created_from:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="La date de fin doit etre superieure ou egale a la date de debut.",
                )
        return ProcessingJobFilters(
            status=filters.status,
            job_type=filters.job_type,
            schedule_id=filters.schedule_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
            search=self._clean_text(filters.search),
        )

    def _filters_dict(self, filters: ProcessingJobFilters) -> dict[str, object]:
        return filters.model_dump(mode="json", exclude_none=True)

    def _repository_result(
        self,
        repository_method: Callable[..., Any],
        *args: object,
        **kwargs: object,
    ) -> Any:
        try:
            return repository_method(*args, **kwargs)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    def _payload(self, job: ProcessingJob) -> dict[str, Any]:
        return job.payload if isinstance(job.payload, dict) else {}

    def _unexpected_handler_result(self, exc: Exception) -> Any:
        from backend.app.orchestration.base import HandlerResult

        return HandlerResult(
            success=False,
            message="Erreur inattendue pendant l'execution du traitement.",
            details={"error": self._safe_message(str(exc))},
            retryable=True,
        )

    def _safe_metadata(self, details: dict[str, Any]) -> dict[str, Any]:
        blocked_fragments = ("password", "token", "secret", "authorization", "api_key", "apikey")
        safe: dict[str, Any] = {}
        for key, value in details.items():
            if any(fragment in str(key).lower() for fragment in blocked_fragments):
                continue
            safe[str(key)] = value
        return safe

    def _safe_message(self, value: str) -> str:
        blocked_fragments = ("password", "token", "secret", "authorization", "api_key", "apikey")
        cleaned = value.strip()[:2000]
        if any(fragment in cleaned.lower() for fragment in blocked_fragments):
            return "Message masque car il contient une donnee sensible."
        return cleaned

    def _clean_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _now(self) -> datetime:
        return self._as_aware(self.now_provider())

    def _as_aware(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
