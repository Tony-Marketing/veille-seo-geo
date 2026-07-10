"""Routes for processing orchestration."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models import User
from backend.app.repositories.alerts import AlertRepository
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.repositories.orchestration import OrchestrationRepository
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.orchestration import (
    ProcessingJobFilters,
    ProcessingJobList,
    ProcessingJobLogList,
    ProcessingJobRead,
    ProcessingJobStatus,
    ProcessingJobType,
    ProcessingSummary,
    ProcessingWorkerRead,
    SchedulerRunResult,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.orchestration import OrchestrationService

router = APIRouter(prefix="/orchestration", tags=["Orchestration"])


def get_service(db: Session = Depends(get_db)) -> OrchestrationService:
    """Build the orchestration service."""

    return OrchestrationService(
        OrchestrationRepository(db),
        SyncScheduleRepository(db),
        MonitoringRepository(db),
        AlertRepository(db),
    )


def _job_filters(
    job_status: ProcessingJobStatus | None = Query(default=None, alias="status"),
    job_type: ProcessingJobType | None = Query(default=None),
    schedule_id: int | None = Query(default=None, gt=0),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
) -> ProcessingJobFilters:
    """Build processing job filters from query parameters."""

    return ProcessingJobFilters(
        status=job_status,
        job_type=job_type,
        schedule_id=schedule_id,
        created_from=created_from,
        created_to=created_to,
    )


@router.get(
    "/jobs",
    response_model=ProcessingJobList,
    summary="Lister les jobs d'orchestration",
    description="Retourne les traitements pagines et filtres sans declencher d'execution.",
)
def list_jobs(
    params: PaginationParams = Depends(pagination_params),
    filters: ProcessingJobFilters = Depends(_job_filters),
    service: OrchestrationService = Depends(get_service),
    _: User = Depends(require_admin),
) -> Any:
    """Return paginated processing jobs."""

    return service.list_jobs(params, filters=filters.model_copy(update={"search": params.search}))


@router.get(
    "/summary",
    response_model=ProcessingSummary,
    summary="Synthese de l'orchestrateur",
    description="Retourne les compteurs agreges de la queue de traitements.",
)
def summary(
    service: OrchestrationService = Depends(get_service),
    _: User = Depends(require_admin),
) -> ProcessingSummary:
    """Return orchestration summary."""

    return service.summary()


@router.get(
    "/workers",
    response_model=list[ProcessingWorkerRead],
    summary="Lister les workers",
    description="Retourne les heartbeats des workers connus.",
)
def list_workers(
    service: OrchestrationService = Depends(get_service),
    _: User = Depends(require_admin),
) -> list[ProcessingWorkerRead]:
    """Return known workers."""

    return service.list_workers()


@router.post(
    "/scheduler/run-once",
    response_model=SchedulerRunResult,
    summary="Executer un cycle scheduler",
    description="Cree les jobs dus sans les executer.",
)
def run_scheduler_once(
    service: OrchestrationService = Depends(get_service),
    _: User = Depends(require_admin),
) -> SchedulerRunResult:
    """Run one scheduler cycle."""

    return service.run_scheduler_once()


@router.get(
    "/jobs/{job_id}",
    response_model=ProcessingJobRead,
    summary="Consulter un job",
    description="Retourne le detail d'un traitement d'orchestration.",
)
def get_job(
    job_id: int,
    service: OrchestrationService = Depends(get_service),
    _: User = Depends(require_admin),
) -> ProcessingJobRead:
    """Return one processing job."""

    return service.get_job(job_id)


@router.get(
    "/jobs/{job_id}/logs",
    response_model=ProcessingJobLogList,
    summary="Lister les logs d'un job",
    description="Retourne les journaux controles associes a un traitement.",
)
def list_job_logs(
    job_id: int,
    params: PaginationParams = Depends(pagination_params),
    service: OrchestrationService = Depends(get_service),
    _: User = Depends(require_admin),
) -> ProcessingJobLogList:
    """Return logs for one job."""

    return service.list_job_logs(job_id, params)


@router.post(
    "/jobs/{job_id}/retry",
    response_model=ProcessingJobRead,
    summary="Relancer un job",
    description="Planifie une relance controlee d'un traitement eligible.",
)
def retry_job(
    job_id: int,
    service: OrchestrationService = Depends(get_service),
    _: User = Depends(require_admin),
) -> ProcessingJobRead:
    """Retry one processing job."""

    return service.retry_job(job_id)


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=ProcessingJobRead,
    summary="Annuler un job",
    description="Annule un traitement non terminal lorsque la transition est autorisee.",
)
def cancel_job(
    job_id: int,
    service: OrchestrationService = Depends(get_service),
    _: User = Depends(require_admin),
) -> ProcessingJobRead:
    """Cancel one processing job."""

    return service.cancel_job(job_id)
