"""Processing handler registry."""

from backend.app.orchestration.base import ProcessingHandler, UnsupportedProcessingHandler
from backend.app.orchestration.bing import BingWebmasterProcessingHandler
from backend.app.orchestration.crawl import CrawlProcessingHandler
from backend.app.orchestration.ga4 import GoogleAnalyticsProcessingHandler
from backend.app.orchestration.geo_analysis import GeoAnalysisProcessingHandler
from backend.app.orchestration.gsc import GoogleSearchConsoleProcessingHandler
from backend.app.orchestration.seo_analysis import SeoAnalysisProcessingHandler
from backend.app.schemas.orchestration import ProcessingJobType


class ProcessingHandlerRegistry:
    """Resolve processing handlers by job type."""

    def __init__(self) -> None:
        self._handlers: dict[str, ProcessingHandler] = {
            ProcessingJobType.GSC.value: GoogleSearchConsoleProcessingHandler(),
            ProcessingJobType.GA4.value: GoogleAnalyticsProcessingHandler(),
            ProcessingJobType.BING.value: BingWebmasterProcessingHandler(),
            ProcessingJobType.CRAWL.value: CrawlProcessingHandler(),
            ProcessingJobType.SEO_ANALYSIS.value: SeoAnalysisProcessingHandler(),
            ProcessingJobType.GEO_ANALYSIS.value: GeoAnalysisProcessingHandler(),
        }

    def get(self, job_type: str) -> ProcessingHandler:
        """Return the registered handler or a controlled unsupported handler."""

        return self._handlers.get(job_type, UnsupportedProcessingHandler(job_type))

