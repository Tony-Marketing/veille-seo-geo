"""Schémas Pydantic pour ProjectTask."""

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class ProjectTaskCreate(BaseModel):
    entity_id: int | None = None
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    status: str = Field(default="todo", max_length=50)
    priority: str | None = Field(default=None, max_length=50)


class ProjectTaskUpdate(BaseModel):
    entity_id: int | None = None
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    status: str | None = Field(default=None, max_length=50)
    priority: str | None = Field(default=None, max_length=50)


class ProjectTaskRead(TimestampRead):
    id: int
    entity_id: int | None
    title: str
    description: str | None
    status: str
    priority: str | None


ProjectTaskList = PaginatedResponse[ProjectTaskRead]
