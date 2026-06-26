"""Fabrique de routers CRUD."""

from typing import Any

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.pagination import PaginationParams, pagination_params


def create_crud_router(
    *,
    prefix: str,
    tags: list[str],
    repository_class: type,
    service_class: type,
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    list_schema: type[BaseModel],
) -> APIRouter:
    """Create a standard CRUD router for simple resources."""

    router = APIRouter(prefix=prefix, tags=tags)

    def get_service(db: Session = Depends(get_db)) -> Any:
        if isinstance(service_class, type):
            return service_class(repository_class(db))
        return service_class(db)

    @router.get(
        "",
        response_model=list_schema,
        summary=f"Lister {tags[0]}",
        description="Retourne une liste paginée avec recherche et tri.",
    )
    def list_items(
        params: PaginationParams = Depends(pagination_params),
        service: Any = Depends(get_service),
    ) -> Any:
        return service.list(params)

    @router.get(
        "/{item_id}",
        response_model=read_schema,
        summary=f"Consulter {tags[0]}",
        description="Retourne une ressource par identifiant.",
    )
    def get_item(item_id: int, service: Any = Depends(get_service)) -> Any:
        return service.get(item_id)

    @router.post(
        "",
        response_model=read_schema,
        status_code=status.HTTP_201_CREATED,
        summary=f"Créer {tags[0]}",
        description="Crée une nouvelle ressource.",
    )
    def create_item(payload: create_schema, service: Any = Depends(get_service)) -> Any:  # type: ignore[valid-type]
        return service.create(payload)

    @router.put(
        "/{item_id}",
        response_model=read_schema,
        summary=f"Modifier {tags[0]}",
        description="Met à jour une ressource existante.",
    )
    def update_item(
        item_id: int,
        payload: update_schema,  # type: ignore[valid-type]
        service: Any = Depends(get_service),
    ) -> Any:
        return service.update(item_id, payload)

    @router.delete(
        "/{item_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary=f"Supprimer {tags[0]}",
        description="Supprime une ressource existante.",
    )
    def delete_item(item_id: int, service: Any = Depends(get_service)) -> Response:
        service.delete(item_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
