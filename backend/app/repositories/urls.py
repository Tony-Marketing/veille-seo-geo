"""Repository Url."""

from sqlalchemy.orm import Session

from backend.app.models import Url
from backend.app.repositories.base import BaseRepository


class UrlRepository(BaseRepository[Url]):
    """Repository for URLs."""

    search_fields = ("url",)

    def __init__(self, db: Session) -> None:
        super().__init__(db, Url)
