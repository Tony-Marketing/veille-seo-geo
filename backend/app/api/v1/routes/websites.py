"""Routes Sites."""

from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.schemas.websites import WebsiteCreate, WebsiteList, WebsiteRead, WebsiteUpdate
from backend.app.services.websites import WebsiteService

router = APIRouter(prefix="/websites", tags=["Sites"])


def get_service(db: Session = Depends(get_db)) -> WebsiteService:
    """Build the Website service from the request database session."""

    return WebsiteService(WebsiteRepository(db))


@router.get(
    "",
    response_model=WebsiteList,
    summary="Lister Sites",
    description="Retourne une liste paginee avec recherche, tri et filtre actif.",
)
def list_websites(
    params: PaginationParams = Depends(pagination_params),
    is_active: bool | None = Query(None, description="Filtre les sites actifs ou inactifs."),
    service: WebsiteService = Depends(get_service),
) -> Any:
    """Return paginated websites."""

    return service.list(params, is_active=is_active)


@router.get(
    "/{item_id}",
    response_model=WebsiteRead,
    summary="Consulter Sites",
    description="Retourne un site par identifiant.",
)
def get_website(item_id: int, service: WebsiteService = Depends(get_service)) -> Any:
    """Return one website."""

    return service.get(item_id)


@router.post(
    "",
    response_model=WebsiteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Creer Sites",
    description="Cree un nouveau site.",
)
def create_website(payload: WebsiteCreate, service: WebsiteService = Depends(get_service)) -> Any:
    """Create a website."""

    return service.create(payload)


@router.put(
    "/{item_id}",
    response_model=WebsiteRead,
    summary="Modifier Sites",
    description="Met a jour un site existant.",
)
def update_website(
    item_id: int,
    payload: WebsiteUpdate,
    service: WebsiteService = Depends(get_service),
) -> Any:
    """Update a website."""

    return service.update(item_id, payload)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer Sites",
    description="Supprime un site existant.",
)
def delete_website(item_id: int, service: WebsiteService = Depends(get_service)) -> Response:
    """Delete a website."""

    service.delete(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
