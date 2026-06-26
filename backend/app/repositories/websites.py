"""Repository Website."""

from sqlalchemy.orm import Session

from backend.app.models import Website
from backend.app.repositories.base import BaseRepository


class WebsiteRepository(BaseRepository[Website]):
    """Repository for websites."""

    search_fields = ("name", "url", "cms")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Website)
