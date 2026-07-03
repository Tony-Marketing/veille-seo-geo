"""Tests for the crawler engine."""

from backend.app.crawler.engine import CRAWL_STATUS_CANCELLED, CRAWL_STATUS_COMPLETED, CrawlerEngine
from backend.app.crawler.fetcher import FetchResult


class FakeFetcher:
    """Deterministic fetcher for engine tests."""

    def __init__(self) -> None:
        self.urls: list[str] = []

    def fetch(self, url: str) -> FetchResult:
        self.urls.append(url)
        if url == "https://example.com/":
            return FetchResult(
                requested_url=url,
                final_url=url,
                status_code=200,
                content_type="text/html",
                text="""
                    <a href="/a">A</a>
                    <a href="/a#fragment">Duplicate</a>
                    <a href="https://external.example.com/">External</a>
                """,
                response_time_ms=10,
            )
        return FetchResult(
            requested_url=url,
            final_url=url,
            status_code=200,
            content_type="text/html",
            text="<html></html>",
            response_time_ms=5,
        )


def test_engine_discovers_internal_links_and_removes_duplicates() -> None:
    """The engine crawls internal links once and ignores external links."""

    fetcher = FakeFetcher()
    pages = []
    engine = CrawlerEngine(fetcher=fetcher)  # type: ignore[arg-type]

    result = engine.run(
        "https://example.com",
        max_depth=1,
        max_pages=10,
        on_page_result=lambda page, _: pages.append(page),
    )

    assert result.status == CRAWL_STATUS_COMPLETED
    assert result.discovered_count == 2
    assert result.processed_count == 2
    assert fetcher.urls == ["https://example.com/", "https://example.com/a"]
    assert [page.normalized_url for page in pages] == ["https://example.com/", "https://example.com/a"]
    assert pages[0].raw_html is not None


def test_engine_respects_max_pages() -> None:
    """The engine stops after the configured page limit."""

    result = CrawlerEngine(fetcher=FakeFetcher()).run("https://example.com", max_depth=1, max_pages=1)  # type: ignore[arg-type]

    assert result.status == CRAWL_STATUS_COMPLETED
    assert result.processed_count == 1
    assert result.discovered_count == 1
    assert result.pending_count == 0


def test_engine_can_be_cancelled() -> None:
    """A stop callback cancels the crawl before the next fetch."""

    result = CrawlerEngine(fetcher=FakeFetcher()).run(  # type: ignore[arg-type]
        "https://example.com",
        stop_requested=lambda: True,
    )

    assert result.status == CRAWL_STATUS_CANCELLED
    assert result.processed_count == 0
