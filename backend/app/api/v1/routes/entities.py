"""Routes Entités."""

from fastapi import Depends

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.core.security import require_permission
from backend.app.repositories.entities import EntityRepository
from backend.app.schemas.entities import EntityCreate, EntityList, EntityRead, EntityUpdate
from backend.app.services.entities import EntityService

router = create_crud_router(
    prefix="/entities",
    tags=["Entités"],
    repository_class=EntityRepository,
    service_class=EntityService,
    create_schema=EntityCreate,
    update_schema=EntityUpdate,
    read_schema=EntityRead,
    list_schema=EntityList,
    list_dependencies=[Depends(require_permission("entity.read"))],
    get_dependencies=[Depends(require_permission("entity.read"))],
    create_dependencies=[Depends(require_permission("entity.write"))],
    update_dependencies=[Depends(require_permission("entity.write"))],
    delete_dependencies=[Depends(require_permission("entity.delete"))],
)
