"""Service Website."""

from math import ceil

from pydantic import BaseModel

from backend.app.models import Website
from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.pagination import PaginatedResponse, PaginationParams
from backend.app.schemas.websites import WebsiteRead
from backend.app.services.base import CrudService


class WebsiteService(CrudService[Website, WebsiteRead]):
    """Business service for websites."""

    def __init__(self, repository: WebsiteRepository) -> None:
        super().__init__(repository, WebsiteRead)

    def list(self, params: PaginationParams, is_active: bool | None = None) -> PaginatedResponse[WebsiteRead]:
        """Return paginated websites with optional active status filtering."""

        items, total = self.repository.list(params, is_active=is_active)
        return PaginatedResponse[WebsiteRead](
            items=[WebsiteRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def create(self, payload: BaseModel) -> WebsiteRead:
        self._ensure_unique("url", payload.model_dump()["url"])
        return super().create(payload)

    def update(self, item_id: int, payload: BaseModel) -> WebsiteRead:
        data = payload.model_dump(exclude_unset=True)
        if "url" in data:
            self._ensure_unique("url", data["url"], current_id=item_id)
        return super().update(item_id, payload)
