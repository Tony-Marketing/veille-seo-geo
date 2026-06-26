"""Repository ProjectTask."""

from sqlalchemy.orm import Session

from backend.app.models import ProjectTask
from backend.app.repositories.base import BaseRepository


class ProjectTaskRepository(BaseRepository[ProjectTask]):
    """Repository for project tasks."""

    search_fields = ("title", "description", "status", "priority")

    def __init__(self, db: Session) -> None:
        super().__init__(db, ProjectTask)
