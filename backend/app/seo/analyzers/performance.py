"""HTML performance analyzers without Lighthouse."""

from backend.app.seo.analyzers.helpers import issue
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class HtmlPerformanceAnalyzer:
    """Analyze simple HTML performance indicators."""

    family = "html_performance"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        issues: list[SeoIssue] = []
        html_size = len(document.raw_html.encode("utf-8"))
        if html_size > 200_000:
            issues.append(
                issue(
                    self.family,
                    "html_weight",
                    "html_weight_high",
                    "HTML weight is high.",
                    severity="minor",
                    details=f"{html_size} bytes",
                ),
            )
        if document.scripts_count > 20:
            issues.append(
                issue(
                    self.family,
                    "scripts",
                    "html_many_scripts",
                    "Page contains many script tags.",
                    severity="minor",
                    details=str(document.scripts_count),
                ),
            )
        if document.css_count > 10:
            issues.append(
                issue(
                    self.family,
                    "css",
                    "html_many_css",
                    "Page contains many CSS resources.",
                    severity="minor",
                    details=str(document.css_count),
                ),
            )
        if document.iframe_count > 0:
            issues.append(
                issue(
                    self.family,
                    "iframes",
                    "html_iframes_present",
                    "Page contains iframes.",
                    severity="minor",
                    details=str(document.iframe_count),
                ),
            )
        return issues
