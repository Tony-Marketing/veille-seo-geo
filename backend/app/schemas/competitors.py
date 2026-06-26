"""Schémas Pydantic pour Competitor."""

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class CompetitorCreate(BaseModel):
    entity_id: int | None = None
    name: str = Field(min_length=2, max_length=150)
    website_url: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class CompetitorUpdate(BaseModel):
    entity_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=150)
    website_url: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class CompetitorRead(TimestampRead):
    id: int
    entity_id: int | None
    name: str
    website_url: str | None
    is_active: bool


CompetitorList = PaginatedResponse[CompetitorRead]
