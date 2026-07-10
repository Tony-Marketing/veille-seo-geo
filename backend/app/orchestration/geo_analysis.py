"""GEO analysis processing handler."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.orchestration.base import HandlerResult, int_payload
from backend.app.repositories.geo_analysis import GeoAnalysisRepository
from backend.app.services.geo_analysis import GeoAnalysisService


class GeoAnalysisProcessingHandler:
    """Run a GEO analysis through the existing GEO analysis service."""

    def run(self, payload: dict[str, object], db: Session) -> HandlerResult:
        """Execute the GEO analysis processing job."""

        try:
            result = GeoAnalysisService(GeoAnalysisRepository(db)).run(int_payload(payload, "target_id"))
        except HTTPException as exc:
            return HandlerResult(
                False,
                str(exc.detail),
                {"status_code": exc.status_code},
                retryable=exc.status_code >= 500,
            )
        except ValueError as exc:
            return HandlerResult(False, str(exc), retryable=False)
        return HandlerResult(
            result.status.value in {"COMPLETED", "PARTIAL"},
            "Analyse GEO terminee." if result.status.value in {"COMPLETED", "PARTIAL"} else "Analyse GEO en erreur.",
            {
                "analysis_id": result.id,
                "status": result.status.value,
                "provider_results_count": result.provider_results_count,
            },
            retryable=result.status.value == "FAILED",
        )
