"""Schémas Pydantic pour Report."""

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class ReportCreate(BaseModel):
    entity_id: int | None = None
    title: str = Field(min_length=2, max_length=200)
    report_type: str | None = Field(default=None, max_length=80)
    status: str = Field(default="draft", max_length=50)


class ReportUpdate(BaseModel):
    entity_id: int | None = None
    title: str | None = Field(default=None, min_length=2, max_length=200)
    report_type: str | None = Field(default=None, max_length=80)
    status: str | None = Field(default=None, max_length=50)


class ReportRead(TimestampRead):
    id: int
    entity_id: int | None
    title: str
    report_type: str | None
    status: str


ReportList = PaginatedResponse[ReportRead]
