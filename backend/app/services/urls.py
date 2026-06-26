"""Service Url."""

from backend.app.models import Url
from backend.app.repositories.urls import UrlRepository
from backend.app.schemas.urls import UrlRead
from backend.app.services.base import CrudService


class UrlService(CrudService[Url, UrlRead]):
    """Business service for URLs."""

    def __init__(self, repository: UrlRepository) -> None:
        super().__init__(repository, UrlRead)
