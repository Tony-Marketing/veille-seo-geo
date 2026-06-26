"""Repository Keyword."""

from sqlalchemy.orm import Session

from backend.app.models import Keyword
from backend.app.repositories.base import BaseRepository


class KeywordRepository(BaseRepository[Keyword]):
    """Repository for keywords."""

    search_fields = ("term", "intent", "priority")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Keyword)
