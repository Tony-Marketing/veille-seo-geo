"""Routes SEO Analysis."""

from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.seo_analysis import SeoAnalysisRepository
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.schemas.seo_analysis import SeoAnalysisCreate, SeoAnalysisList, SeoAnalysisRead
from backend.app.services.seo_analysis import SeoAnalysisService

router = APIRouter(prefix="/seo-analysis", tags=["SEO Analysis"])


def get_service(db: Session = Depends(get_db)) -> SeoAnalysisService:
    """Build the SEO Analysis service from the request database session."""

    return SeoAnalysisService(SeoAnalysisRepository(db), CrawlRepository(db))


@router.get(
    "",
    response_model=SeoAnalysisList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister Analyses SEO",
    description="Retourne les analyses SEO paginees.",
)
def list_seo_analyses(
    params: PaginationParams = Depends(pagination_params),
    service: SeoAnalysisService = Depends(get_service),
) -> Any:
    """Return paginated SEO analyses."""

    return service.list(params)


@router.post(
    "",
    response_model=SeoAnalysisRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Creer Analyse SEO",
    description="Cree une analyse SEO en attente pour un crawl.",
)
def create_seo_analysis(payload: SeoAnalysisCreate, service: SeoAnalysisService = Depends(get_service)) -> Any:
    """Create a pending SEO analysis."""

    return service.create(payload)


@router.get(
    "/{analysis_id}",
    response_model=SeoAnalysisRead,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Consulter Analyse SEO",
    description="Retourne une analyse SEO par identifiant.",
)
def get_seo_analysis(analysis_id: int, service: SeoAnalysisService = Depends(get_service)) -> Any:
    """Return one SEO analysis."""

    return service.get(analysis_id)


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Supprimer Analyse SEO",
    description="Supprime une analyse SEO existante.",
)
def delete_seo_analysis(analysis_id: int, service: SeoAnalysisService = Depends(get_service)) -> Response:
    """Delete one SEO analysis."""

    service.delete(analysis_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

