"""Routes Mots-clés."""

from fastapi import Depends

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.core.security import require_permission
from backend.app.repositories.keywords import KeywordRepository
from backend.app.schemas.keywords import KeywordCreate, KeywordList, KeywordRead, KeywordUpdate
from backend.app.services.keywords import KeywordService

router = create_crud_router(
    prefix="/keywords",
    tags=["Mots-clés"],
    repository_class=KeywordRepository,
    service_class=KeywordService,
    create_schema=KeywordCreate,
    update_schema=KeywordUpdate,
    read_schema=KeywordRead,
    list_schema=KeywordList,
    list_dependencies=[Depends(require_permission("keyword.read"))],
    get_dependencies=[Depends(require_permission("keyword.read"))],
    create_dependencies=[Depends(require_permission("keyword.write"))],
    update_dependencies=[Depends(require_permission("keyword.write"))],
    delete_dependencies=[Depends(require_permission("keyword.delete"))],
)
