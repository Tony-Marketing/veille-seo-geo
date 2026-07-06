"""Data structures used by the deterministic SEO engine."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SeoIssue:
    """One deterministic SEO issue produced by an analyzer."""

    family: str
    criterion: str
    severity: str
    code: str
    message: str
    details: str | None = None


@dataclass(frozen=True)
class SeoPageInput:
    """Persisted crawl page data consumed by the SEO engine."""

    id: int
    url: str
    normalized_url: str
    final_url: str | None
    final_normalized_url: str | None
    status_code: int | None
    content_type: str | None
    raw_html: str | None
    response_time_ms: int | None
    is_redirect: bool
    redirect_url: str | None
    redirect_count: int

    @property
    def effective_url(self) -> str:
        """Return the final URL when available, otherwise the requested URL."""

        return self.final_url or self.url


@dataclass(frozen=True)
class KnownCrawlPage:
    """Small lookup representation for pages known in the same crawl."""

    normalized_url: str
    status_code: int | None


@dataclass(frozen=True)
class SeoAnalysisContext:
    """Context shared by analyzers for one crawl."""

    known_pages: dict[str, KnownCrawlPage] = field(default_factory=dict)


@dataclass(frozen=True)
class SeoPageResult:
    """Complete deterministic analysis result for one page."""

    status: str
    issues: list[SeoIssue]
