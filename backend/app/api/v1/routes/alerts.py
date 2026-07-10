"""Routes for the administration alerts center."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models import User
from backend.app.repositories.alerts import AlertRepository
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.schemas.alerts import (
    AlertFilters,
    AlertList,
    AlertRead,
    AlertRefreshResult,
    AlertSeverity,
    AlertStatus,
    AlertSummary,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.alerts import AlertService

router = APIRouter(prefix="/alerts", tags=["Alertes"])


def get_service(db: Session = Depends(get_db)) -> AlertService:
    """Build the alert service from the request database session."""

    return AlertService(AlertRepository(db), MonitoringRepository(db))


def _alert_filters(
    alert_status: AlertStatus | None = Query(default=None, alias="status"),
    severity: AlertSeverity | None = Query(default=None),
    category: str | None = Query(default=None, max_length=80),
    source: str | None = Query(default=None, max_length=80),
) -> AlertFilters:
    """Build alert filters from query parameters."""

    return AlertFilters(
        status=alert_status,
        severity=severity,
        category=category,
        source_type=source,
    )


@router.get(
    "",
    response_model=AlertList,
    summary="Lister les alertes",
    description="Retourne les alertes paginees et filtrees sans declencher de traitement externe.",
)
def list_alerts(
    params: PaginationParams = Depends(pagination_params),
    filters: AlertFilters = Depends(_alert_filters),
    service: AlertService = Depends(get_service),
    _: User = Depends(require_admin),
) -> Any:
    """Return paginated alerts."""

    return service.list_alerts(params, filters=filters.model_copy(update={"search": params.search}))


@router.post(
    "/refresh-from-monitoring",
    response_model=AlertRefreshResult,
    summary="Generer les alertes depuis le monitoring",
    description="Analyse uniquement les evenements de monitoring deja persistes.",
)
def refresh_from_monitoring(
    service: AlertService = Depends(get_service),
    _: User = Depends(require_admin),
) -> AlertRefreshResult:
    """Generate or update alerts from monitoring data."""

    return service.refresh_from_monitoring()


@router.get(
    "/summary",
    response_model=AlertSummary,
    summary="Synthese des alertes",
    description="Retourne les compteurs agreges du centre d'alertes.",
)
def summary(
    service: AlertService = Depends(get_service),
    _: User = Depends(require_admin),
) -> AlertSummary:
    """Return alert summary counters."""

    return service.summary()


@router.get(
    "/{alert_id}",
    response_model=AlertRead,
    summary="Consulter une alerte",
    description="Retourne le detail d'une alerte.",
)
def get_alert(
    alert_id: int,
    service: AlertService = Depends(get_service),
    _: User = Depends(require_admin),
) -> AlertRead:
    """Return one alert."""

    return service.get_alert(alert_id)


@router.post(
    "/{alert_id}/acknowledge",
    response_model=AlertRead,
    summary="Acquitter une alerte",
    description="Marque une alerte comme prise en compte sans la resoudre.",
)
def acknowledge_alert(
    alert_id: int,
    service: AlertService = Depends(get_service),
    current_user: User = Depends(require_admin),
) -> AlertRead:
    """Acknowledge one alert."""

    return service.acknowledge_alert(alert_id, user_id=current_user.id)


@router.post(
    "/{alert_id}/resolve",
    response_model=AlertRead,
    summary="Resoudre une alerte",
    description="Marque une alerte comme resolue sans suppression physique.",
)
def resolve_alert(
    alert_id: int,
    service: AlertService = Depends(get_service),
    _: User = Depends(require_admin),
) -> AlertRead:
    """Resolve one alert."""

    return service.resolve_alert(alert_id)
