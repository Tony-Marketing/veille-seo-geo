"""SQLAlchemy persistence for GEO Intelligence snapshots."""

from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from backend.app.models import GeoVisibilitySnapshot, Website
from backend.app.schemas.geo_intelligence import GeoVisibilityFilters, GeoVisibilityImportItem
from backend.app.schemas.pagination import PaginationParams


class GeoIntelligenceRepository:
    """Encapsulate all SQLAlchemy access for GEO Intelligence."""

    SORT_COLUMNS = {
        "id": GeoVisibilitySnapshot.id,
        "website_id": GeoVisibilitySnapshot.website_id,
        "provider": GeoVisibilitySnapshot.provider,
        "entity": GeoVisibilitySnapshot.entity,
        "visibility_score": GeoVisibilitySnapshot.visibility_score,
        "citation_count": GeoVisibilitySnapshot.citation_count,
        "source_count": GeoVisibilitySnapshot.source_count,
        "ranking": GeoVisibilitySnapshot.ranking,
        "captured_at": GeoVisibilitySnapshot.captured_at,
        "created_at": GeoVisibilitySnapshot.created_at,
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_snapshots(
        self,
        params: PaginationParams,
        *,
        filters: GeoVisibilityFilters,
    ) -> tuple[list[GeoVisibilitySnapshot], int]:
        """Return filtered snapshots with a whitelisted sort."""

        statement = self._filtered(select(GeoVisibilitySnapshot), filters)
        count_statement = self._filtered(select(func.count()).select_from(GeoVisibilitySnapshot), filters)
        sort_name = params.sort or "captured_at"
        sort_column = self.SORT_COLUMNS.get(sort_name)
        if sort_column is None:
            raise ValueError(f"Tri GEO Intelligence non autorise: {sort_name}.")
        order_by = sort_column.desc() if params.order == "desc" else sort_column.asc()
        statement = (
            statement.options(joinedload(GeoVisibilitySnapshot.website))
            .order_by(order_by, GeoVisibilitySnapshot.id.asc())
            .offset(params.offset)
            .limit(params.page_size)
        )
        return list(self.db.scalars(statement).unique()), int(self.db.scalar(count_statement) or 0)

    def all_snapshots(
        self,
        *,
        filters: GeoVisibilityFilters,
        website_ids: list[int] | None = None,
    ) -> list[GeoVisibilitySnapshot]:
        """Return filtered snapshots for service-level deterministic aggregation."""

        statement = self._filtered(select(GeoVisibilitySnapshot), filters)
        if website_ids is not None:
            statement = statement.where(GeoVisibilitySnapshot.website_id.in_(website_ids))
        statement = statement.order_by(
            GeoVisibilitySnapshot.captured_at.asc(),
            GeoVisibilitySnapshot.id.asc(),
        )
        return list(self.db.scalars(statement))

    def get_website(self, website_id: int) -> Website | None:
        """Return the Website referenced by an import item."""

        return self.db.get(Website, website_id)

    def find_exact(self, item: GeoVisibilityImportItem) -> GeoVisibilitySnapshot | None:
        """Return an exact observation already persisted."""

        return self.db.scalar(
            select(GeoVisibilitySnapshot).where(
                GeoVisibilitySnapshot.website_id == item.website_id,
                GeoVisibilitySnapshot.provider == item.provider,
                GeoVisibilitySnapshot.prompt == item.prompt,
                GeoVisibilitySnapshot.entity == item.entity,
                GeoVisibilitySnapshot.answer_hash == item.answer_hash,
                GeoVisibilitySnapshot.captured_at == item.captured_at,
            ),
        )

    def add_pending(self, item: GeoVisibilityImportItem) -> GeoVisibilitySnapshot:
        """Stage one validated observation without committing the transaction."""

        snapshot = GeoVisibilitySnapshot(**item.model_dump())
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def commit(self) -> None:
        """Commit the current unit of work."""

        self.db.commit()

    def rollback(self) -> None:
        """Rollback the current unit of work."""

        self.db.rollback()

    def refresh(self, snapshot: GeoVisibilitySnapshot) -> None:
        """Refresh a snapshot after commit."""

        self.db.refresh(snapshot)

    def _filtered(self, statement: Select[Any], filters: GeoVisibilityFilters) -> Select[Any]:
        if filters.website_id is not None:
            statement = statement.where(GeoVisibilitySnapshot.website_id == filters.website_id)
        if filters.provider:
            statement = statement.where(GeoVisibilitySnapshot.provider == filters.provider)
        if filters.entity:
            statement = statement.where(GeoVisibilitySnapshot.entity.ilike(f"%{filters.entity}%"))
        if filters.prompt:
            statement = statement.where(GeoVisibilitySnapshot.prompt.ilike(f"%{filters.prompt}%"))
        if filters.date_from is not None:
            statement = statement.where(GeoVisibilitySnapshot.captured_at >= filters.date_from)
        if filters.date_to is not None:
            statement = statement.where(GeoVisibilitySnapshot.captured_at <= filters.date_to)
        if filters.search:
            pattern = f"%{filters.search}%"
            statement = statement.where(
                or_(
                    GeoVisibilitySnapshot.provider.ilike(pattern),
                    GeoVisibilitySnapshot.entity.ilike(pattern),
                    GeoVisibilitySnapshot.prompt.ilike(pattern),
                ),
            )
        return statement
