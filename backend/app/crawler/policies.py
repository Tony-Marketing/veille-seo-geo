"""Crawl policy rules."""

from dataclasses import dataclass

from backend.app.crawler.normalizer import UrlNormalizer


@dataclass(frozen=True)
class CrawlPolicies:
    """Configuration and rules limiting a crawl."""

    start_url: str
    max_depth: int = 2
    max_pages: int = 100
    allowed_host: str | None = None

    def __post_init__(self) -> None:
        if self.max_depth < 0:
            raise ValueError("max_depth must be greater than or equal to 0")
        if self.max_pages < 1:
            raise ValueError("max_pages must be greater than or equal to 1")

    @classmethod
    def from_start_url(
        cls,
        start_url: str,
        *,
        max_depth: int = 2,
        max_pages: int = 100,
        normalizer: UrlNormalizer | None = None,
    ) -> "CrawlPolicies":
        """Build policies using the start URL host as crawl boundary."""

        url_normalizer = normalizer or UrlNormalizer()
        normalized_start_url = url_normalizer.normalize(start_url)
        if normalized_start_url is None:
            raise ValueError("start_url must be an absolute HTTP or HTTPS URL")
        return cls(
            start_url=normalized_start_url,
            max_depth=max_depth,
            max_pages=max_pages,
            allowed_host=url_normalizer.host(normalized_start_url),
        )

    def allows(self, normalized_url: str, *, depth: int, discovered_count: int) -> bool:
        """Return whether an URL can be queued."""

        if depth > self.max_depth:
            return False
        if discovered_count >= self.max_pages:
            return False
        if self.allowed_host and UrlNormalizer().host(normalized_url) != self.allowed_host:
            return False
        return True

