"""Schémas Pydantic pour Keyword."""

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class KeywordCreate(BaseModel):
    entity_id: int | None = None
    term: str = Field(min_length=1, max_length=255)
    intent: str | None = Field(default=None, max_length=100)
    priority: str | None = Field(default=None, max_length=50)


class KeywordUpdate(BaseModel):
    entity_id: int | None = None
    term: str | None = Field(default=None, min_length=1, max_length=255)
    intent: str | None = Field(default=None, max_length=100)
    priority: str | None = Field(default=None, max_length=50)


class KeywordRead(TimestampRead):
    id: int
    entity_id: int | None
    term: str
    intent: str | None
    priority: str | None


KeywordList = PaginatedResponse[KeywordRead]
