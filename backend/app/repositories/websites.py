"""Repository Website."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import Website
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class WebsiteRepository(BaseRepository[Website]):
    """Repository for websites."""

    search_fields = ("name", "url", "cms")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Website)

    def list(self, params: PaginationParams, is_active: bool | None = None) -> tuple[list[Website], int]:
        """Return a paginated list of websites with optional active status filtering."""

        statement = select(self.model)
        count_statement = select(func.count()).select_from(self.model)
        filters = self._search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        if is_active is not None:
            statement = statement.where(self.model.is_active.is_(is_active))
            count_statement = count_statement.where(self.model.is_active.is_(is_active))
        if params.sort and hasattr(self.model, params.sort):
            sort_column = getattr(self.model, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)
