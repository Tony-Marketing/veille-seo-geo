"""REST routes for transverse recommendations."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.models import User
from backend.app.repositories.geo_intelligence import GeoIntelligenceRepository
from backend.app.repositories.recommendations import RecommendationRepository
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.schemas.recommendations import (
    RecommendationFilters,
    RecommendationList,
    RecommendationPriority,
    RecommendationRead,
    RecommendationSource,
    RecommendationStatus,
    RecommendationStatusUpdate,
    RecommendationSummary,
)
from backend.app.services.geo_intelligence import GeoIntelligenceService
from backend.app.services.recommendations import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def get_service(db: Session = Depends(get_db)) -> RecommendationService:
    """Build the recommendation service for one request."""

    return RecommendationService(
        RecommendationRepository(db),
        GeoIntelligenceService(GeoIntelligenceRepository(db)),
    )


def recommendation_filters(
    website_id: int | None = Query(default=None, gt=0),
    source: RecommendationSource | None = Query(default=None),
    category: str | None = Query(default=None, max_length=80),
    priority: RecommendationPriority | None = Query(default=None),
    recommendation_status: RecommendationStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, max_length=255),
) -> RecommendationFilters:
    """Build validated recommendation filters from query parameters."""

    return RecommendationFilters(
        website_id=website_id,
        source=source,
        category=category,
        priority=priority,
        status=recommendation_status,
        search=search,
    )


@router.get(
    "",
    response_model=RecommendationList,
    dependencies=[Depends(require_permission("recommendation.read"))],
    summary="Lister les recommandations",
)
def list_recommendations(
    params: PaginationParams = Depends(pagination_params),
    filters: RecommendationFilters = Depends(recommendation_filters),
    service: RecommendationService = Depends(get_service),
) -> Any:
    """Return filtered and paginated recommendations."""

    effective_filters = filters.model_copy(update={"search": params.search or filters.search})
    return service.list_recommendations(params, filters=effective_filters)


@router.get(
    "/summary",
    response_model=RecommendationSummary,
    dependencies=[Depends(require_permission("recommendation.read"))],
    summary="Synthese des recommandations",
)
def summary(
    filters: RecommendationFilters = Depends(recommendation_filters),
    service: RecommendationService = Depends(get_service),
) -> RecommendationSummary:
    """Return recommendation counters for Dashboard V2 and Desktop."""

    return service.summary(filters=filters)


@router.get(
    "/{recommendation_id}",
    response_model=RecommendationRead,
    dependencies=[Depends(require_permission("recommendation.read"))],
    summary="Consulter une recommandation",
)
def get_recommendation(
    recommendation_id: int,
    service: RecommendationService = Depends(get_service),
) -> RecommendationRead:
    """Return one persisted recommendation."""

    return service.get_recommendation(recommendation_id)


@router.patch(
    "/{recommendation_id}/status",
    response_model=RecommendationRead,
    summary="Modifier le statut d'une recommandation",
)
def update_recommendation_status(
    recommendation_id: int,
    payload: RecommendationStatusUpdate,
    service: RecommendationService = Depends(get_service),
    _: User = Depends(require_permission("recommendation.write")),
) -> RecommendationRead:
    """Apply a lifecycle transition through the business service."""

    return service.update_status(recommendation_id, payload.status)
