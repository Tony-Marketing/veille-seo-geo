"""Service ProjectTask."""

from backend.app.models import ProjectTask
from backend.app.repositories.project_tasks import ProjectTaskRepository
from backend.app.schemas.project_tasks import ProjectTaskRead
from backend.app.services.base import CrudService


class ProjectTaskService(CrudService[ProjectTask, ProjectTaskRead]):
    """Business service for project tasks."""

    def __init__(self, repository: ProjectTaskRepository) -> None:
        super().__init__(repository, ProjectTaskRead)
