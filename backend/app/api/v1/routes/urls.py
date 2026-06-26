"""Routes URLs."""

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.repositories.urls import UrlRepository
from backend.app.schemas.urls import UrlCreate, UrlList, UrlRead, UrlUpdate
from backend.app.services.urls import UrlService

router = create_crud_router(
    prefix="/urls",
    tags=["URLs"],
    repository_class=UrlRepository,
    service_class=UrlService,
    create_schema=UrlCreate,
    update_schema=UrlUpdate,
    read_schema=UrlRead,
    list_schema=UrlList,
)
