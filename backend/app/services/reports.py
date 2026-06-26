"""Service Report."""

from backend.app.models import Report
from backend.app.repositories.reports import ReportRepository
from backend.app.schemas.reports import ReportRead
from backend.app.services.base import CrudService


class ReportService(CrudService[Report, ReportRead]):
    """Business service for reports."""

    def __init__(self, repository: ReportRepository) -> None:
        super().__init__(repository, ReportRead)
