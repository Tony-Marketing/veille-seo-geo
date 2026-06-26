"""Routes Concurrents."""

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.repositories.competitors import CompetitorRepository
from backend.app.schemas.competitors import CompetitorCreate, CompetitorList, CompetitorRead, CompetitorUpdate
from backend.app.services.competitors import CompetitorService

router = create_crud_router(
    prefix="/competitors",
    tags=["Concurrents"],
    repository_class=CompetitorRepository,
    service_class=CompetitorService,
    create_schema=CompetitorCreate,
    update_schema=CompetitorUpdate,
    read_schema=CompetitorRead,
    list_schema=CompetitorList,
)
