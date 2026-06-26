"""Routes Tâches Projet."""

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.repositories.project_tasks import ProjectTaskRepository
from backend.app.schemas.project_tasks import ProjectTaskCreate, ProjectTaskList, ProjectTaskRead, ProjectTaskUpdate
from backend.app.services.project_tasks import ProjectTaskService

router = create_crud_router(
    prefix="/project-tasks",
    tags=["Tâches Projet"],
    repository_class=ProjectTaskRepository,
    service_class=ProjectTaskService,
    create_schema=ProjectTaskCreate,
    update_schema=ProjectTaskUpdate,
    read_schema=ProjectTaskRead,
    list_schema=ProjectTaskList,
)
