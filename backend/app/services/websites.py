"""Service Website."""

from pydantic import BaseModel

from backend.app.models import Website
from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.websites import WebsiteRead
from backend.app.services.base import CrudService


class WebsiteService(CrudService[Website, WebsiteRead]):
    """Business service for websites."""

    def __init__(self, repository: WebsiteRepository) -> None:
        super().__init__(repository, WebsiteRead)

    def create(self, payload: BaseModel) -> WebsiteRead:
        self._ensure_unique("url", payload.model_dump()["url"])
        return super().create(payload)

    def update(self, item_id: int, payload: BaseModel) -> WebsiteRead:
        data = payload.model_dump(exclude_unset=True)
        if "url" in data:
            self._ensure_unique("url", data["url"], current_id=item_id)
        return super().update(item_id, payload)
