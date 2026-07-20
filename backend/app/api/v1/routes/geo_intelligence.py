"""REST routes for multi-provider GEO Intelligence."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.models import User
from backend.app.repositories.geo_intelligence import GeoIntelligenceRepository
from backend.app.schemas.geo_intelligence import (
    GeoProviderList,
    GeoVisibilityFilters,
    GeoVisibilityHistory,
    GeoVisibilityImportRequest,
    GeoVisibilityImportResult,
    GeoVisibilitySnapshotList,
    GeoVisibilitySummary,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.geo_intelligence import GeoIntelligenceService

router = APIRouter(prefix="/geo-intelligence", tags=["GEO Intelligence"])


def get_service(db: Session = Depends(get_db)) -> GeoIntelligenceService:
    """Build the GEO Intelligence service for one request."""

    return GeoIntelligenceService(GeoIntelligenceRepository(db))


def geo_intelligence_filters(
    website_id: int | None = Query(default=None, gt=0),
    provider: str | None = Query(default=None, max_length=80),
    entity: str | None = Query(default=None, max_length=255),
    prompt: str | None = Query(default=None, max_length=500),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    search: str | None = Query(default=None, max_length=255),
) -> GeoVisibilityFilters:
    """Build validated GEO Intelligence filters."""

    return GeoVisibilityFilters(
        website_id=website_id,
        provider=provider,
        entity=entity,
        prompt=prompt,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )


@router.get(
    "",
    response_model=GeoVisibilitySnapshotList,
    dependencies=[Depends(require_permission("geo.read"))],
    summary="Lister les captures GEO Intelligence",
)
def list_snapshots(
    params: PaginationParams = Depends(pagination_params),
    filters: GeoVisibilityFilters = Depends(geo_intelligence_filters),
    service: GeoIntelligenceService = Depends(get_service),
) -> Any:
    """Return filtered and paginated normalized observations."""

    effective_filters = filters.model_copy(update={"search": params.search or filters.search})
    return service.list_snapshots(params, filters=effective_filters)


@router.get(
    "/summary",
    response_model=GeoVisibilitySummary,
    dependencies=[Depends(require_permission("geo.read"))],
    summary="Synthese GEO Intelligence",
)
def summary(
    filters: GeoVisibilityFilters = Depends(geo_intelligence_filters),
    service: GeoIntelligenceService = Depends(get_service),
) -> GeoVisibilitySummary:
    """Return consolidated GEO Intelligence KPIs."""

    return service.summary(filters=filters)


@router.get(
    "/providers",
    response_model=GeoProviderList,
    dependencies=[Depends(require_permission("geo.read"))],
    summary="Fournisseurs GEO Intelligence",
)
def providers(service: GeoIntelligenceService = Depends(get_service)) -> GeoProviderList:
    """Return provider configuration states without contacting them."""

    return service.providers()


@router.get(
    "/history",
    response_model=GeoVisibilityHistory,
    dependencies=[Depends(require_permission("geo.read"))],
    summary="Historique GEO Intelligence",
)
def history(
    filters: GeoVisibilityFilters = Depends(geo_intelligence_filters),
    service: GeoIntelligenceService = Depends(get_service),
) -> GeoVisibilityHistory:
    """Return daily provider history."""

    return service.history(filters=filters)


@router.post(
    "/import",
    response_model=GeoVisibilityImportResult,
    status_code=status.HTTP_201_CREATED,
    summary="Importer des observations GEO Intelligence normalisees",
)
def import_observations(
    payload: GeoVisibilityImportRequest,
    service: GeoIntelligenceService = Depends(get_service),
    _: User = Depends(require_permission("geo.write")),
) -> GeoVisibilityImportResult:
    """Persist normalized observations without launching an external request."""

    return service.import_observations(payload)
