"""Repository Competitor."""

from sqlalchemy.orm import Session

from backend.app.models import Competitor
from backend.app.repositories.base import BaseRepository


class CompetitorRepository(BaseRepository[Competitor]):
    """Repository for competitors."""

    search_fields = ("name", "website_url")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Competitor)
