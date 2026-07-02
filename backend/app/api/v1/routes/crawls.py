"""Routes Crawls."""

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.crawls import CrawlCreate, CrawlList, CrawlPageList, CrawlRead, CrawlStart
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.crawls import CrawlService

router = APIRouter(prefix="/crawls", tags=["Crawls"])


def get_service(db: Session = Depends(get_db)) -> CrawlService:
    """Build the Crawl service from the request database session."""

    return CrawlService(CrawlRepository(db), WebsiteRepository(db))


@router.get(
    "",
    response_model=CrawlList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister Crawls",
    description="Retourne les sessions de crawl paginees.",
)
def list_crawls(
    params: PaginationParams = Depends(pagination_params),
    service: CrawlService = Depends(get_service),
) -> Any:
    """Return paginated crawl sessions."""

    return service.list(params)


@router.post(
    "",
    response_model=CrawlRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Creer Crawl",
    description="Cree une session de crawl en attente.",
)
def create_crawl(payload: CrawlCreate, service: CrawlService = Depends(get_service)) -> Any:
    """Create a crawl session."""

    return service.create(payload)


@router.get(
    "/{crawl_id}",
    response_model=CrawlRead,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Consulter Crawl",
    description="Retourne une session de crawl.",
)
def get_crawl(crawl_id: int, service: CrawlService = Depends(get_service)) -> Any:
    """Return one crawl session."""

    return service.get(crawl_id)


@router.post(
    "/{crawl_id}/start",
    response_model=CrawlRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Lancer Crawl",
    description="Lance l'execution d'une session de crawl.",
)
def start_crawl(
    crawl_id: int,
    payload: CrawlStart | None = None,
    service: CrawlService = Depends(get_service),
) -> Any:
    """Start a crawl session."""

    return service.start(crawl_id, payload)


@router.post(
    "/{crawl_id}/cancel",
    response_model=CrawlRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Arreter Crawl",
    description="Demande l'arret d'une session de crawl.",
)
def cancel_crawl(crawl_id: int, service: CrawlService = Depends(get_service)) -> Any:
    """Cancel a crawl session."""

    return service.cancel(crawl_id)


@router.get(
    "/{crawl_id}/pages",
    response_model=CrawlPageList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister Pages Crawlees",
    description="Retourne les pages decouvertes pendant une session de crawl.",
)
def list_crawl_pages(
    crawl_id: int,
    params: PaginationParams = Depends(pagination_params),
    service: CrawlService = Depends(get_service),
) -> Any:
    """Return paginated pages for a crawl session."""

    return service.list_pages(crawl_id, params)

