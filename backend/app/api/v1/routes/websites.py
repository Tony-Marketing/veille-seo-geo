"""Routes Sites."""

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.websites import WebsiteCreate, WebsiteList, WebsiteRead, WebsiteUpdate
from backend.app.services.websites import WebsiteService

router = create_crud_router(
    prefix="/websites",
    tags=["Sites"],
    repository_class=WebsiteRepository,
    service_class=WebsiteService,
    create_schema=WebsiteCreate,
    update_schema=WebsiteUpdate,
    read_schema=WebsiteRead,
    list_schema=WebsiteList,
)
