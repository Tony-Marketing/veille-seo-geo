"""Schémas Pydantic pour Url."""

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class UrlCreate(BaseModel):
    website_id: int | None = None
    url: str = Field(min_length=8, max_length=500)
    status_code: int | None = Field(default=None, ge=100, le=599)
    is_indexable: bool = True


class UrlUpdate(BaseModel):
    website_id: int | None = None
    url: str | None = Field(default=None, min_length=8, max_length=500)
    status_code: int | None = Field(default=None, ge=100, le=599)
    is_indexable: bool | None = None


class UrlRead(TimestampRead):
    id: int
    website_id: int | None
    url: str
    status_code: int | None
    is_indexable: bool


UrlList = PaginatedResponse[UrlRead]
