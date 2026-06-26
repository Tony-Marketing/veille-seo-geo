"""Service Entity."""

from backend.app.models import Entity
from backend.app.repositories.entities import EntityRepository
from backend.app.schemas.entities import EntityRead
from backend.app.services.base import CrudService


class EntityService(CrudService[Entity, EntityRead]):
    """Business service for entities."""

    def __init__(self, repository: EntityRepository) -> None:
        super().__init__(repository, EntityRead)
