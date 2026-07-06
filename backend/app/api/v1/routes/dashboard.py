"""Routes Dashboard."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.geo_analysis import GeoAnalysisRepository
from backend.app.repositories.seo_analysis import SeoAnalysisRepository
from backend.app.schemas.dashboard import DashboardOverview
from backend.app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_service(db: Session = Depends(get_db)) -> DashboardService:
    """Build the Dashboard service from the request database session."""

    return DashboardService(CrawlRepository(db), SeoAnalysisRepository(db), GeoAnalysisRepository(db))


@router.get(
    "/overview",
    response_model=DashboardOverview,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Synthese Dashboard SEO/GEO",
    description="Retourne une synthese Dashboard a partir des donnees deja persistees.",
)
def get_dashboard_overview(
    website_id: int | None = Query(default=None, gt=0),
    crawl_id: int | None = Query(default=None, gt=0),
    seo_analysis_id: int | None = Query(default=None, gt=0),
    geo_analysis_id: int | None = Query(default=None, gt=0),
    service: DashboardService = Depends(get_service),
) -> Any:
    """Return the SEO/GEO dashboard overview."""

    return service.overview(
        website_id=website_id,
        crawl_id=crawl_id,
        seo_analysis_id=seo_analysis_id,
        geo_analysis_id=geo_analysis_id,
    )
