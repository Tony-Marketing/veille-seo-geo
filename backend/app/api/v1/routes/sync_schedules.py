"""Routes for synchronization schedules."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models import User
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.schemas.sync_schedules import (
    SyncFrequency,
    SyncScheduleCreate,
    SyncScheduleFilters,
    SyncScheduleList,
    SyncScheduleRead,
    SyncScheduleStatus,
    SyncScheduleUpdate,
    SyncType,
)
from backend.app.services.sync_schedules import SyncScheduleService

router = APIRouter(prefix="/sync-schedules", tags=["Planifications synchronisations"])


def get_service(db: Session = Depends(get_db)) -> SyncScheduleService:
    """Build the synchronization schedule service."""

    return SyncScheduleService(SyncScheduleRepository(db))


def _schedule_filters(
    sync_type: SyncType | None = Query(default=None),
    frequency: SyncFrequency | None = Query(default=None),
    schedule_status: SyncScheduleStatus | None = Query(default=None, alias="status"),
    is_active: bool | None = Query(default=None),
    website_id: int | None = Query(default=None, gt=0),
    next_run_from: datetime | None = Query(default=None),
    next_run_to: datetime | None = Query(default=None),
) -> SyncScheduleFilters:
    """Build synchronization schedule filters from query parameters."""

    return SyncScheduleFilters(
        sync_type=sync_type,
        frequency=frequency,
        status=schedule_status,
        is_active=is_active,
        website_id=website_id,
        next_run_from=next_run_from,
        next_run_to=next_run_to,
    )


@router.get(
    "",
    response_model=SyncScheduleList,
    summary="Lister les planifications de synchronisation",
    description="Retourne les planifications paginees avec filtres administrateur.",
)
def list_schedules(
    params: PaginationParams = Depends(pagination_params),
    filters: SyncScheduleFilters = Depends(_schedule_filters),
    service: SyncScheduleService = Depends(get_service),
    _: User = Depends(require_admin),
) -> Any:
    """Return paginated synchronization schedules."""

    return service.list_schedules(params, filters=filters.model_copy(update={"search": params.search}))


@router.post(
    "",
    response_model=SyncScheduleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Creer une planification de synchronisation",
    description="Cree une planification sans declencher de synchronisation reelle.",
)
def create_schedule(
    payload: SyncScheduleCreate,
    service: SyncScheduleService = Depends(get_service),
    current_user: User = Depends(require_admin),
) -> Any:
    """Create a synchronization schedule."""

    return service.create_schedule(payload, user_id=current_user.id)


@router.get(
    "/{schedule_id}",
    response_model=SyncScheduleRead,
    summary="Consulter une planification de synchronisation",
    description="Retourne le detail d'une planification.",
)
def get_schedule(
    schedule_id: int,
    service: SyncScheduleService = Depends(get_service),
    _: User = Depends(require_admin),
) -> Any:
    """Return one synchronization schedule."""

    return service.get_schedule(schedule_id)


@router.patch(
    "/{schedule_id}",
    response_model=SyncScheduleRead,
    summary="Modifier une planification de synchronisation",
    description="Met a jour une planification et recalcule sa prochaine execution theorique.",
)
def update_schedule(
    schedule_id: int,
    payload: SyncScheduleUpdate,
    service: SyncScheduleService = Depends(get_service),
    current_user: User = Depends(require_admin),
) -> Any:
    """Update one synchronization schedule."""

    return service.update_schedule(schedule_id, payload, user_id=current_user.id)


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactiver une planification de synchronisation",
    description="Desactive logiquement une planification sans supprimer sa configuration.",
)
def delete_schedule(
    schedule_id: int,
    service: SyncScheduleService = Depends(get_service),
    current_user: User = Depends(require_admin),
) -> Response:
    """Soft-disable one synchronization schedule."""

    service.delete_schedule(schedule_id, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{schedule_id}/enable",
    response_model=SyncScheduleRead,
    summary="Activer une planification",
    description="Active une planification et recalcule sa prochaine execution theorique.",
)
def enable_schedule(
    schedule_id: int,
    service: SyncScheduleService = Depends(get_service),
    current_user: User = Depends(require_admin),
) -> Any:
    """Enable one synchronization schedule."""

    return service.enable_schedule(schedule_id, user_id=current_user.id)


@router.post(
    "/{schedule_id}/disable",
    response_model=SyncScheduleRead,
    summary="Desactiver une planification",
    description="Desactive une planification sans suppression physique.",
)
def disable_schedule(
    schedule_id: int,
    service: SyncScheduleService = Depends(get_service),
    current_user: User = Depends(require_admin),
) -> Any:
    """Disable one synchronization schedule."""

    return service.disable_schedule(schedule_id, user_id=current_user.id)


@router.post(
    "/{schedule_id}/recalculate",
    response_model=SyncScheduleRead,
    summary="Recalculer la prochaine execution",
    description="Recalcule la prochaine execution theorique sans declencher de synchronisation.",
)
def recalculate_schedule(
    schedule_id: int,
    service: SyncScheduleService = Depends(get_service),
    current_user: User = Depends(require_admin),
) -> Any:
    """Recalculate one synchronization schedule next run."""

    return service.recalculate_schedule(schedule_id, user_id=current_user.id)

