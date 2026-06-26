"""Repository générique CRUD."""

from typing import Any, Generic, TypeVar

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.core.database import Base
from backend.app.schemas.pagination import PaginationParams

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Encapsulate SQLAlchemy persistence operations."""

    search_fields: tuple[str, ...] = ()

    def __init__(self, db: Session, model: type[ModelT]) -> None:
        self.db = db
        self.model = model

    def list(self, params: PaginationParams) -> tuple[list[ModelT], int]:
        """Return a paginated list of models."""

        statement = select(self.model)
        count_statement = select(func.count()).select_from(self.model)
        filters = self._search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        if params.sort and hasattr(self.model, params.sort):
            sort_column = getattr(self.model, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def get(self, model_id: int) -> ModelT | None:
        """Return a model by primary key."""

        return self.db.get(self.model, model_id)

    def get_by_field(self, field_name: str, value: Any) -> ModelT | None:
        """Return one model matching a field value."""

        field = getattr(self.model, field_name)
        return self.db.scalar(select(self.model).where(field == value))

    def create(self, data: dict[str, Any]) -> ModelT:
        """Persist a new model."""

        item = self.model(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: ModelT, data: dict[str, Any]) -> ModelT:
        """Update a model."""

        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: ModelT) -> None:
        """Delete a model."""

        self.db.delete(item)
        self.db.commit()

    def count(self) -> int:
        """Return total model count."""

        return int(self.db.scalar(select(func.count()).select_from(self.model)) or 0)

    def _search_filters(self, search: str | None) -> Any | None:
        if not search or not self.search_fields:
            return None
        criteria = []
        for field_name in self.search_fields:
            if hasattr(self.model, field_name):
                criteria.append(getattr(self.model, field_name).ilike(f"%{search}%"))
        return or_(*criteria) if criteria else None
