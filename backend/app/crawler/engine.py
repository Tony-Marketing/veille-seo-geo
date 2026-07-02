"""Crawler Engine orchestration."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from backend.app.crawler.duplicate_detector import DuplicateDetector
from backend.app.crawler.extractor import LinkExtractor
from backend.app.crawler.fetcher import FetchResult, HttpFetcher
from backend.app.crawler.normalizer import UrlNormalizer
from backend.app.crawler.policies import CrawlPolicies
from backend.app.crawler.queue import CrawlQueue, CrawlQueueItem

CRAWL_STATUS_COMPLETED = "COMPLETED"
CRAWL_STATUS_CANCELLED = "CANCELLED"
CRAWL_STATUS_FAILED = "FAILED"


@dataclass(frozen=True)
class CrawlProgress:
    """Current crawl progress produced by the engine."""

    discovered_count: int
    processed_count: int
    failed_count: int
    pending_count: int
    max_depth_reached: int


@dataclass(frozen=True)
class CrawlPageResult:
    """One page discovered and fetched by the crawler engine."""

    url: str
    normalized_url: str
    final_url: str | None
    final_normalized_url: str | None
    depth: int
    status_code: int | None
    content_type: str | None
    is_redirect: bool
    redirect_url: str | None
    redirect_count: int
    response_time_ms: int | None
    error_message: str | None
    discovered_at: datetime
    visited_at: datetime
    links_found: int


@dataclass(frozen=True)
class CrawlRunResult:
    """Complete crawl run result."""

    status: str
    pages: list[CrawlPageResult] = field(default_factory=list)
    discovered_count: int = 0
    processed_count: int = 0
    failed_count: int = 0
    pending_count: int = 0
    max_depth_reached: int = 0
    error_message: str | None = None


PageResultCallback = Callable[[CrawlPageResult, CrawlProgress], None]
StopRequestedCallback = Callable[[], bool]


class CrawlerEngine:
    """Coordinate URL discovery, fetching and link extraction."""

    def __init__(
        self,
        *,
        fetcher: HttpFetcher | None = None,
        extractor: LinkExtractor | None = None,
        normalizer: UrlNormalizer | None = None,
    ) -> None:
        self.fetcher = fetcher or HttpFetcher()
        self.extractor = extractor or LinkExtractor()
        self.normalizer = normalizer or UrlNormalizer()

    def run(
        self,
        start_url: str,
        *,
        max_depth: int = 2,
        max_pages: int = 100,
        stop_requested: StopRequestedCallback | None = None,
        on_page_result: PageResultCallback | None = None,
    ) -> CrawlRunResult:
        """Run a crawl and return all engine-produced results."""

        try:
            policies = CrawlPolicies.from_start_url(
                start_url,
                max_depth=max_depth,
                max_pages=max_pages,
                normalizer=self.normalizer,
            )
            return self._run_with_policies(
                policies,
                stop_requested=stop_requested,
                on_page_result=on_page_result,
            )
        except Exception as exc:  # noqa: BLE001
            return CrawlRunResult(status=CRAWL_STATUS_FAILED, error_message=str(exc))

    def _run_with_policies(
        self,
        policies: CrawlPolicies,
        *,
        stop_requested: StopRequestedCallback | None,
        on_page_result: PageResultCallback | None,
    ) -> CrawlRunResult:
        queue = CrawlQueue()
        duplicates = DuplicateDetector()
        pages: list[CrawlPageResult] = []
        processed_count = 0
        failed_count = 0
        max_depth_reached = 0

        duplicates.add(policies.start_url)
        queue.push(CrawlQueueItem(url=policies.start_url, normalized_url=policies.start_url, depth=0))

        while queue and processed_count < policies.max_pages:
            if stop_requested is not None and stop_requested():
                return self._result(
                    CRAWL_STATUS_CANCELLED,
                    pages,
                    duplicates,
                    processed_count,
                    failed_count,
                    len(queue),
                    max_depth_reached,
                )

            item = queue.pop()
            fetched = self.fetcher.fetch(item.url)
            processed_count += 1
            if fetched.error_message is not None:
                failed_count += 1

            page_result = self._page_result(item, fetched)
            pages.append(page_result)
            max_depth_reached = max(max_depth_reached, item.depth)

            if fetched.is_html and fetched.error_message is None and item.depth < policies.max_depth:
                self._queue_links(
                    queue,
                    duplicates,
                    policies,
                    fetched,
                    current_depth=item.depth,
                )

            progress = CrawlProgress(
                discovered_count=duplicates.count(),
                processed_count=processed_count,
                failed_count=failed_count,
                pending_count=len(queue),
                max_depth_reached=max_depth_reached,
            )
            if on_page_result is not None:
                on_page_result(page_result, progress)

        return self._result(
            CRAWL_STATUS_COMPLETED,
            pages,
            duplicates,
            processed_count,
            failed_count,
            len(queue),
            max_depth_reached,
        )

    def _queue_links(
        self,
        queue: CrawlQueue,
        duplicates: DuplicateDetector,
        policies: CrawlPolicies,
        fetched: FetchResult,
        *,
        current_depth: int,
    ) -> None:
        base_url = fetched.final_url or fetched.requested_url
        for link in self.extractor.extract(fetched.text):
            normalized_url = self.normalizer.normalize(link, base_url=base_url)
            next_depth = current_depth + 1
            if normalized_url is None:
                continue
            if not policies.allows(normalized_url, depth=next_depth, discovered_count=duplicates.count()):
                continue
            if not duplicates.add(normalized_url):
                continue
            queue.push(CrawlQueueItem(url=normalized_url, normalized_url=normalized_url, depth=next_depth))

    def _page_result(self, item: CrawlQueueItem, fetched: FetchResult) -> CrawlPageResult:
        visited_at = datetime.now(UTC)
        final_normalized_url = None
        if fetched.final_url is not None:
            final_normalized_url = self.normalizer.normalize(fetched.final_url)

        links_found = len(self.extractor.extract(fetched.text)) if fetched.is_html and not fetched.error_message else 0
        return CrawlPageResult(
            url=item.url,
            normalized_url=item.normalized_url,
            final_url=fetched.final_url,
            final_normalized_url=final_normalized_url,
            depth=item.depth,
            status_code=fetched.status_code,
            content_type=fetched.content_type,
            is_redirect=fetched.is_redirect,
            redirect_url=fetched.redirect_url,
            redirect_count=fetched.redirect_count,
            response_time_ms=fetched.response_time_ms,
            error_message=fetched.error_message,
            discovered_at=visited_at,
            visited_at=visited_at,
            links_found=links_found,
        )

    def _result(
        self,
        status: str,
        pages: list[CrawlPageResult],
        duplicates: DuplicateDetector,
        processed_count: int,
        failed_count: int,
        pending_count: int,
        max_depth_reached: int,
    ) -> CrawlRunResult:
        return CrawlRunResult(
            status=status,
            pages=pages,
            discovered_count=duplicates.count(),
            processed_count=processed_count,
            failed_count=failed_count,
            pending_count=pending_count,
            max_depth_reached=max_depth_reached,
        )
