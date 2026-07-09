"""Routes for the administration monitoring center."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models import User
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.monitoring import (
    MonitoringConnectorRead,
    MonitoringEventList,
    MonitoringEventType,
    MonitoringOverview,
    MonitoringSeverity,
    MonitoringSyncScheduleList,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.schemas.sync_schedules import SyncFrequency, SyncScheduleFilters, SyncScheduleStatus, SyncType
from backend.app.services.monitoring import MonitoringService
from backend.app.services.sync_schedules import SyncScheduleService

router = APIRouter(prefix="/admin/monitoring", tags=["Monitoring"])


def get_service(db: Session = Depends(get_db)) -> MonitoringService:
    """Build the monitoring service from the request database session."""

    sync_repository = SyncScheduleRepository(db)
    return MonitoringService(
        MonitoringRepository(db),
        SyncScheduleService(sync_repository),
    )


def _schedule_filters(
    sync_type: SyncType | None = Query(default=None),
    frequency: SyncFrequency | None = Query(default=None),
    schedule_status: SyncScheduleStatus | None = Query(default=None, alias="status"),
    is_active: bool | None = Query(default=None),
    website_id: int | None = Query(default=None, gt=0),
) -> SyncScheduleFilters:
    """Build read-only synchronization schedule filters."""

    return SyncScheduleFilters(
        sync_type=sync_type,
        frequency=frequency,
        status=schedule_status,
        is_active=is_active,
        website_id=website_id,
    )


@router.get(
    "/overview",
    response_model=MonitoringOverview,
    summary="Synthese du monitoring",
    description="Retourne les compteurs consolides du centre de monitoring sans declencher de traitement.",
)
def overview(
    service: MonitoringService = Depends(get_service),
    _: User = Depends(require_admin),
) -> MonitoringOverview:
    """Return global monitoring counters."""

    return service.overview()


@router.get(
    "/events",
    response_model=MonitoringEventList,
    summary="Lister les evenements de monitoring",
    description="Retourne les evenements de monitoring pagines et filtres.",
)
def list_events(
    params: PaginationParams = Depends(pagination_params),
    severity: MonitoringSeverity | None = Query(default=None),
    event_type: MonitoringEventType | None = Query(default=None),
    service: MonitoringService = Depends(get_service),
    _: User = Depends(require_admin),
) -> MonitoringEventList:
    """Return paginated monitoring events."""

    return service.list_events(params, severity=severity, event_type=event_type)


@router.get(
    "/connectors",
    response_model=list[MonitoringConnectorRead],
    summary="Etat logique des connecteurs",
    description="Retourne la sante logique des connecteurs a partir des donnees persistees.",
)
def list_connectors(
    service: MonitoringService = Depends(get_service),
    _: User = Depends(require_admin),
) -> list[MonitoringConnectorRead]:
    """Return logical connector health without external calls."""

    return service.list_connectors()


@router.get(
    "/sync-schedules",
    response_model=MonitoringSyncScheduleList,
    summary="Planifications vues par le monitoring",
    description="Retourne une vue consultative des planifications sans les modifier.",
)
def list_sync_schedules(
    params: PaginationParams = Depends(pagination_params),
    filters: SyncScheduleFilters = Depends(_schedule_filters),
    service: MonitoringService = Depends(get_service),
    _: User = Depends(require_admin),
) -> Any:
    """Return read-only synchronization schedules for monitoring."""

    return service.list_sync_schedules(params, filters=filters.model_copy(update={"search": params.search}))
