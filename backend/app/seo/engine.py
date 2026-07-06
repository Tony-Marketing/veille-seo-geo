"""Deterministic SEO analysis orchestration."""

from collections.abc import Iterable

from backend.app.seo.analyzers import DEFAULT_ANALYZERS
from backend.app.seo.analyzers.types import Analyzer
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput, SeoPageResult
from backend.app.seo.parser import parse_html

PAGE_STATUS_COMPLETED = "COMPLETED"
PAGE_STATUS_FAILED = "FAILED"


class SeoAnalysisEngine:
    """Run deterministic SEO analyzers on persisted crawl HTML."""

    def __init__(self, analyzers: Iterable[Analyzer] | None = None) -> None:
        self.analyzers = tuple(analyzers or DEFAULT_ANALYZERS)

    def analyze_page(self, page: SeoPageInput, context: SeoAnalysisContext | None = None) -> SeoPageResult:
        """Analyze one persisted crawl page without network access."""

        analysis_context = context or SeoAnalysisContext()
        issues: list[SeoIssue] = []
        document = None
        if page.raw_html:
            document = parse_html(page.raw_html)
        else:
            issues.append(
                SeoIssue(
                    family="html",
                    criterion="content",
                    severity="critical",
                    code="html_missing",
                    message="Persisted HTML is missing for this crawl page.",
                ),
            )

        for analyzer in self.analyzers:
            issues.extend(analyzer.analyze(page, document, analysis_context))

        status = PAGE_STATUS_COMPLETED if document is not None else PAGE_STATUS_FAILED
        return SeoPageResult(status=status, issues=issues)
