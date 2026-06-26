"""Services métier CRUD."""

from math import ceil
from typing import Any, Generic, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel

from backend.app.core.database import Base
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginatedResponse, PaginationParams

ModelT = TypeVar("ModelT", bound=Base)
ReadT = TypeVar("ReadT", bound=BaseModel)


class CrudService(Generic[ModelT, ReadT]):
    """Generic service containing shared business CRUD rules."""

    read_schema: type[ReadT]

    def __init__(self, repository: BaseRepository[ModelT], read_schema: type[ReadT]) -> None:
        self.repository = repository
        self.read_schema = read_schema

    def list(self, params: PaginationParams) -> PaginatedResponse[ReadT]:
        """Return paginated resources."""

        items, total = self.repository.list(params)
        return PaginatedResponse[self.read_schema](
            items=[self.read_schema.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get(self, item_id: int) -> ReadT:
        """Return one resource or raise 404."""

        item = self.repository.get(item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ressource introuvable.")
        return self.read_schema.model_validate(item)

    def create(self, payload: BaseModel) -> ReadT:
        """Create a resource."""

        item = self.repository.create(payload.model_dump(exclude_unset=True))
        return self.read_schema.model_validate(item)

    def update(self, item_id: int, payload: BaseModel) -> ReadT:
        """Update a resource."""

        item = self.repository.get(item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ressource introuvable.")
        updated = self.repository.update(item, payload.model_dump(exclude_unset=True))
        return self.read_schema.model_validate(updated)

    def delete(self, item_id: int) -> None:
        """Delete a resource."""

        item = self.repository.get(item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ressource introuvable.")
        self.repository.delete(item)

    def _ensure_unique(self, field_name: str, value: Any, current_id: int | None = None) -> None:
        existing = self.repository.get_by_field(field_name, value)
        if existing is not None and existing.id != current_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette valeur existe déjà.")
