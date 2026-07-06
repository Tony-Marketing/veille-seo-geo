"""Shared analyzer protocol."""

from typing import Protocol

from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class Analyzer(Protocol):
    """Contract implemented by all deterministic analyzers."""

    family: str

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        """Return deterministic issues for one page."""
