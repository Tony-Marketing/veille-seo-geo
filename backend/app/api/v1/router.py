"""API v1 router."""

from fastapi import APIRouter

from backend.app.api.v1.routes import (
    admin,
    auth,
    bing_webmaster_tools,
    competitors,
    crawls,
    dashboard,
    entities,
    geo_analysis,
    google_analytics,
    google_search_console,
    keywords,
    monitoring,
    permissions,
    project_tasks,
    reports,
    roles,
    seo_analysis,
    sync_schedules,
    urls,
    users,
    websites,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(permissions.router)
api_router.include_router(entities.router)
api_router.include_router(websites.router)
api_router.include_router(competitors.router)
api_router.include_router(crawls.router)
api_router.include_router(dashboard.router)
api_router.include_router(keywords.router)
api_router.include_router(urls.router)
api_router.include_router(reports.router)
api_router.include_router(project_tasks.router)
api_router.include_router(seo_analysis.router)
api_router.include_router(geo_analysis.router)
api_router.include_router(google_analytics.router)
api_router.include_router(google_search_console.router)
api_router.include_router(bing_webmaster_tools.router)
api_router.include_router(sync_schedules.router)
api_router.include_router(monitoring.router)
api_router.include_router(admin.router)

router = api_router
