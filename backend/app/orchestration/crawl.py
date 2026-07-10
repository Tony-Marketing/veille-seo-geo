"""Crawl processing handler."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.crawler.engine import CrawlerEngine
from backend.app.orchestration.base import HandlerResult, int_payload
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.crawls import CrawlStart
from backend.app.services.crawls import CrawlService


class CrawlProcessingHandler:
    """Run a crawl through the existing crawl service."""

    def run(self, payload: dict[str, object], db: Session) -> HandlerResult:
        """Execute the crawl processing job."""

        try:
            request = CrawlStart(
                max_depth=self._optional_int(payload.get("max_depth")),
                max_pages=self._optional_int(payload.get("max_pages")),
            )
            result = CrawlService(CrawlRepository(db), WebsiteRepository(db), engine=CrawlerEngine()).start(
                int_payload(payload, "target_id"),
                request,
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
            "Crawl termine." if result.status.value == "COMPLETED" else "Crawl termine avec erreur.",
            {"crawl_id": result.id, "status": result.status.value, "pages_crawled": result.pages_crawled},
            retryable=result.status.value == "FAILED",
        )

    def _optional_int(self, value: object) -> int | None:
        if value is None or value == "":
            return None
        parsed = int(value)
        return parsed if parsed > 0 else None
