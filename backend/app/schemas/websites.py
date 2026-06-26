"""Schémas Pydantic pour Website."""

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class WebsiteCreate(BaseModel):
    entity_id: int | None = None
    name: str = Field(min_length=2, max_length=150)
    url: str = Field(min_length=8, max_length=255)
    cms: str | None = Field(default=None, max_length=50)
    is_active: bool = True


class WebsiteUpdate(BaseModel):
    entity_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=150)
    url: str | None = Field(default=None, min_length=8, max_length=255)
    cms: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class WebsiteRead(TimestampRead):
    id: int
    entity_id: int | None
    name: str
    url: str
    cms: str | None
    is_active: bool


WebsiteList = PaginatedResponse[WebsiteRead]
