"""Routes for Dashboard V2."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.dashboard_v2 import DashboardV2Repository
from backend.app.schemas.dashboard_v2 import (
    DashboardV2Filters,
    DashboardV2Granularity,
    DashboardV2HealthStatus,
    DashboardV2OverviewResponse,
    DashboardV2Period,
    DashboardV2RecommendationList,
    DashboardV2RecommendationSeverity,
    DashboardV2Source,
    DashboardV2TrendMetric,
    DashboardV2TrendsResponse,
    DashboardV2WebsiteList,
)
from backend.app.schemas.pagination import Order, PaginationParams, pagination_params
from backend.app.services.dashboard_v2 import DashboardV2Service

router = APIRouter(prefix="/dashboard-v2", tags=["Dashboard V2"])


def get_service(db: Session = Depends(get_db)) -> DashboardV2Service:
    """Build the Dashboard V2 service from the request database session."""

    return DashboardV2Service(DashboardV2Repository(db))


def dashboard_v2_filters(
    website_id: int | None = Query(default=None, gt=0),
    entity_id: int | None = Query(default=None, gt=0),
    is_active: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    period: DashboardV2Period = Query(default=DashboardV2Period.LAST_30_DAYS),
    compare_to_previous: bool = Query(default=True),
    source: list[DashboardV2Source] | None = Query(default=None),
    health_status: DashboardV2HealthStatus | None = Query(default=None),
    search: str | None = Query(default=None, max_length=255),
    sort: str | None = Query(default=None, max_length=80),
    order: Order = Query(default="asc"),
) -> DashboardV2Filters:
    """Build Dashboard V2 filters from query parameters."""

    return DashboardV2Filters(
        website_id=website_id,
        entity_id=entity_id,
        is_active=is_active,
        date_from=date_from,
        date_to=date_to,
        period=period,
        compare_to_previous=compare_to_previous,
        source=source or [],
        health_status=health_status,
        search=search,
        sort=sort,
        order=order,
    )


@router.get(
    "/overview",
    response_model=DashboardV2OverviewResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Synthese Dashboard V2",
    description="Retourne la synthese executive multi-sites depuis les donnees deja persistees.",
)
def get_dashboard_v2_overview(
    filters: DashboardV2Filters = Depends(dashboard_v2_filters),
    service: DashboardV2Service = Depends(get_service),
) -> Any:
    """Return Dashboard V2 overview."""

    return service.overview(filters)


@router.get(
    "/trends",
    response_model=DashboardV2TrendsResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Tendances Dashboard V2",
    description="Retourne les series temporelles whitelistees du Dashboard V2.",
)
def get_dashboard_v2_trends(
    filters: DashboardV2Filters = Depends(dashboard_v2_filters),
    granularity: DashboardV2Granularity = Query(default=DashboardV2Granularity.DAY),
    metrics: list[DashboardV2TrendMetric] | None = Query(default=None),
    service: DashboardV2Service = Depends(get_service),
) -> Any:
    """Return Dashboard V2 trend series."""

    return service.trends(filters=filters, granularity=granularity, metrics=metrics)


@router.get(
    "/websites",
    response_model=DashboardV2WebsiteList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Sites Dashboard V2",
    description="Retourne la vue executive paginee des sites.",
)
def list_dashboard_v2_websites(
    params: PaginationParams = Depends(pagination_params),
    filters: DashboardV2Filters = Depends(dashboard_v2_filters),
    service: DashboardV2Service = Depends(get_service),
) -> Any:
    """Return paginated Dashboard V2 website summaries."""

    return service.websites(params, filters=filters)


@router.get(
    "/recommendations",
    response_model=DashboardV2RecommendationList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Recommandations Dashboard V2",
    description="Retourne les recommandations deterministes non persistees du Dashboard V2.",
)
def list_dashboard_v2_recommendations(
    params: PaginationParams = Depends(pagination_params),
    filters: DashboardV2Filters = Depends(dashboard_v2_filters),
    severity: DashboardV2RecommendationSeverity | None = Query(default=None),
    priority: int | None = Query(default=None, ge=1, le=5),
    service: DashboardV2Service = Depends(get_service),
) -> Any:
    """Return paginated Dashboard V2 deterministic recommendations."""

    return service.recommendations(params, filters=filters, severity=severity, priority=priority)
