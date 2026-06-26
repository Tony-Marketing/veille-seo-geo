"""FastAPI application entrypoint."""

from fastapi import FastAPI

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Plateforme interne de pilotage SEO, GEO et administration.",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.include_router(api_router)


@app.get("/api/v1/health", tags=["Santé"], summary="Santé API", description="Vérifie que l'API répond.")
def health() -> dict[str, str]:
    """Return basic API health."""

    return {"status": "ok"}
