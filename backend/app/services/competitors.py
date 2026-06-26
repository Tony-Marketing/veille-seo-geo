"""Service Competitor."""

from backend.app.models import Competitor
from backend.app.repositories.competitors import CompetitorRepository
from backend.app.schemas.competitors import CompetitorRead
from backend.app.services.base import CrudService


class CompetitorService(CrudService[Competitor, CompetitorRead]):
    """Business service for competitors."""

    def __init__(self, repository: CompetitorRepository) -> None:
        super().__init__(repository, CompetitorRead)
