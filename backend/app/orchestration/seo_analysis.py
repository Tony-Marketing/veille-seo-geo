"""SEO analysis processing handler."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.orchestration.base import HandlerResult, int_payload
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.seo_analysis import SeoAnalysisRepository
from backend.app.services.seo_analysis import SeoAnalysisService


class SeoAnalysisProcessingHandler:
    """Run a SEO analysis through the existing SEO analysis service."""

    def run(self, payload: dict[str, object], db: Session) -> HandlerResult:
        """Execute the SEO analysis processing job."""

        try:
            result = SeoAnalysisService(SeoAnalysisRepository(db), CrawlRepository(db)).run(
                int_payload(payload, "target_id"),
            )
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
            result.status.value == "COMPLETED",
            "Analyse SEO terminee." if result.status.value == "COMPLETED" else "Analyse SEO terminee avec erreur.",
            {"analysis_id": result.id, "status": result.status.value, "issues_total": result.issues_total},
            retryable=result.status.value == "FAILED",
        )
