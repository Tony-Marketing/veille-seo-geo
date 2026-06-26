"""Schémas et paramètres de pagination réutilisables."""

from typing import Generic, Literal, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")
Order = Literal["asc", "desc"]


class PaginationParams(BaseModel):
    """Common pagination and search parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: str | None = None
    sort: str | None = None
    order: Order = "asc"

    @property
    def offset(self) -> int:
        """Return the SQL offset for the current page."""

        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


def pagination_params(
    page: int = Query(1, ge=1, description="Numéro de page."),
    page_size: int = Query(20, ge=1, le=100, description="Nombre d'éléments par page."),
    search: str | None = Query(None, description="Recherche plein texte simple."),
    sort: str | None = Query(None, description="Colonne de tri."),
    order: Order = Query("asc", description="Ordre de tri."),
) -> PaginationParams:
    """Build pagination parameters from query arguments."""

    return PaginationParams(page=page, page_size=page_size, search=search, sort=sort, order=order)
