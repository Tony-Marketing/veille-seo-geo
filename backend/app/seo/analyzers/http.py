"""HTTP metadata analyzer."""

from backend.app.seo.analyzers.helpers import issue
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class HttpAnalyzer:
    """Analyze HTTP metadata persisted by the crawler."""

    family = "http"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        """Return issues related to persisted HTTP data."""

        issues: list[SeoIssue] = []
        if page.status_code is None:
            issues.append(issue(self.family, "status_code", "http_status_missing", "HTTP status code is missing."))
        elif page.status_code >= 400:
            issues.append(
                issue(
                    self.family,
                    "status_code",
                    "http_error_status",
                    "HTTP status code indicates an error.",
                    severity="critical",
                    details=str(page.status_code),
                ),
            )
        if not page.effective_url.lower().startswith("https://"):
            issues.append(issue(self.family, "https", "http_not_https", "Page URL does not use HTTPS."))
        if page.is_redirect:
            issues.append(
                issue(
                    self.family,
                    "redirect",
                    "http_redirect",
                    "Page was reached through a redirect.",
                    severity="minor",
                    details=page.redirect_url,
                ),
            )
        if page.response_time_ms is not None and page.response_time_ms > 1000:
            issues.append(
                issue(
                    self.family,
                    "response_time",
                    "http_slow_response",
                    "Response time is high.",
                    severity="minor",
                    details=f"{page.response_time_ms} ms",
                ),
            )
        if page.content_type and "text/html" not in page.content_type.lower():
            issues.append(
                issue(
                    self.family,
                    "content_type",
                    "http_non_html_content",
                    "Content type is not HTML.",
                    severity="minor",
                    details=page.content_type,
                ),
            )
        return issues
