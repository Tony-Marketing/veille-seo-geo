"""Service Keyword."""

from backend.app.models import Keyword
from backend.app.repositories.keywords import KeywordRepository
from backend.app.schemas.keywords import KeywordRead
from backend.app.services.base import CrudService


class KeywordService(CrudService[Keyword, KeywordRead]):
    """Business service for keywords."""

    def __init__(self, repository: KeywordRepository) -> None:
        super().__init__(repository, KeywordRead)
