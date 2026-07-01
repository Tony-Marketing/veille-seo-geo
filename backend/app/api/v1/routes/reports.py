"""Routes Rapports."""

from fastapi import Depends

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.core.security import require_permission
from backend.app.repositories.reports import ReportRepository
from backend.app.schemas.reports import ReportCreate, ReportList, ReportRead, ReportUpdate
from backend.app.services.reports import ReportService

router = create_crud_router(
    prefix="/reports",
    tags=["Rapports"],
    repository_class=ReportRepository,
    service_class=ReportService,
    create_schema=ReportCreate,
    update_schema=ReportUpdate,
    read_schema=ReportRead,
    list_schema=ReportList,
    list_dependencies=[Depends(require_permission("report.read"))],
    get_dependencies=[Depends(require_permission("report.read"))],
    create_dependencies=[Depends(require_permission("report.write"))],
    update_dependencies=[Depends(require_permission("report.write"))],
    delete_dependencies=[Depends(require_permission("report.delete"))],
)
