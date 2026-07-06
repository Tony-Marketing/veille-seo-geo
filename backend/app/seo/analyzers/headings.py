"""Heading analyzers."""

from backend.app.seo.analyzers.helpers import issue
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class H1Analyzer:
    """Analyze H1 tags."""

    family = "h1"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        h1_values = [heading.text for heading in document.headings if heading.level == 1]
        if not h1_values:
            return [issue(self.family, "count", "h1_missing", "H1 is missing.")]
        issues: list[SeoIssue] = []
        if len(h1_values) > 1:
            issues.append(issue(self.family, "count", "h1_multiple", "Multiple H1 tags found."))
        if any(len(value) > 90 for value in h1_values):
            issues.append(issue(self.family, "length", "h1_too_long", "At least one H1 is too long."))
        return issues


class H2Analyzer:
    """Analyze H2 tags."""

    family = "h2"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        if any(heading.level == 2 for heading in document.headings):
            return []
        return [issue(self.family, "count", "h2_missing", "No H2 tag found.", severity="minor")]


class HeadingHierarchyAnalyzer:
    """Analyze heading hierarchy gaps."""

    family = "heading_hierarchy"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        previous = 0
        issues: list[SeoIssue] = []
        for heading in document.headings:
            if previous and heading.level > previous + 1:
                issues.append(
                    issue(
                        self.family,
                        "levels",
                        "heading_level_skip",
                        "Heading hierarchy skips a level.",
                        details=f"H{previous} to H{heading.level}",
                    ),
                )
            previous = heading.level
        return issues
