"""Repository Entity."""

from sqlalchemy.orm import Session

from backend.app.models import Entity
from backend.app.repositories.base import BaseRepository


class EntityRepository(BaseRepository[Entity]):
    """Repository for entities."""

    search_fields = ("name", "description")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Entity)
