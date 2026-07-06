"""Routes GEO Analysis."""

from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.geo_analysis import GeoAnalysisRepository
from backend.app.schemas.geo_analysis import GeoAnalysisCreate, GeoAnalysisList, GeoAnalysisRead
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.geo_analysis import GeoAnalysisService

router = APIRouter(prefix="/geo-analysis", tags=["GEO Analysis"])


def get_service(db: Session = Depends(get_db)) -> GeoAnalysisService:
    """Build the GEO Analysis service from the request database session."""

    return GeoAnalysisService(GeoAnalysisRepository(db))


@router.get(
    "",
    response_model=GeoAnalysisList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister Analyses GEO",
    description="Retourne les analyses GEO paginees.",
)
def list_geo_analyses(
    params: PaginationParams = Depends(pagination_params),
    service: GeoAnalysisService = Depends(get_service),
) -> Any:
    """Return paginated GEO analyses."""

    return service.list(params)


@router.post(
    "",
    response_model=GeoAnalysisRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Creer Analyse GEO",
    description="Cree une analyse GEO en attente pour une analyse SEO terminee.",
)
def create_geo_analysis(payload: GeoAnalysisCreate, service: GeoAnalysisService = Depends(get_service)) -> Any:
    """Create a pending GEO analysis."""

    return service.create(payload)


@router.get(
    "/{analysis_id}",
    response_model=GeoAnalysisRead,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Consulter Analyse GEO",
    description="Retourne une analyse GEO complete par identifiant.",
)
def get_geo_analysis(analysis_id: int, service: GeoAnalysisService = Depends(get_service)) -> Any:
    """Return one GEO analysis."""

    return service.get(analysis_id)


@router.post(
    "/{analysis_id}/run",
    response_model=GeoAnalysisRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Lancer Analyse GEO",
    description="Execute une analyse GEO existante.",
)
def run_geo_analysis(analysis_id: int, service: GeoAnalysisService = Depends(get_service)) -> Any:
    """Run one GEO analysis."""

    return service.run(analysis_id)


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Supprimer Analyse GEO",
    description="Supprime une analyse GEO existante.",
)
def delete_geo_analysis(analysis_id: int, service: GeoAnalysisService = Depends(get_service)) -> Response:
    """Delete one GEO analysis."""

    service.delete(analysis_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
