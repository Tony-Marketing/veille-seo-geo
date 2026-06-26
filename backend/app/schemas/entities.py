"""Schémas Pydantic pour Entity."""

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class EntityCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None
    is_active: bool = True


class EntityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    is_active: bool | None = None


class EntityRead(TimestampRead):
    id: int
    name: str
    description: str | None
    is_active: bool


EntityList = PaginatedResponse[EntityRead]
