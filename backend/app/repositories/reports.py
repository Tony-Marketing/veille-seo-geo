"""Repository Report."""

from sqlalchemy.orm import Session

from backend.app.models import Report
from backend.app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    """Repository for reports."""

    search_fields = ("title", "report_type", "status")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Report)
