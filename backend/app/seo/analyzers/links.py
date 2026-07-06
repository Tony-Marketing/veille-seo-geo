"""Link and anchor analyzers."""

from collections import Counter

from backend.app.seo.analyzers.helpers import absolute_url, issue, same_host
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class InternalLinksAnalyzer:
    """Analyze internal links using only crawl-known URLs."""

    family = "internal_links"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        issues: list[SeoIssue] = []
        internal_count = 0
        for anchor in document.anchors:
            target = absolute_url(anchor.href, page)
            if not same_host(target, page):
                continue
            internal_count += 1
            normalized_target = target.rstrip("/")
            known_page = context.known_pages.get(normalized_target) or context.known_pages.get(f"{normalized_target}/")
            if known_page and known_page.status_code and known_page.status_code >= 400:
                issues.append(
                    issue(
                        self.family,
                        "broken",
                        "internal_link_broken",
                        "Internal link points to a known HTTP error.",
                        details=target,
                    ),
                )
        if internal_count == 0:
            issues.append(issue(self.family, "count", "internal_links_missing", "No internal link found."))
        return issues


class ExternalLinksAnalyzer:
    """Analyze external links without downloading targets."""

    family = "external_links"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        issues: list[SeoIssue] = []
        for anchor in document.anchors:
            target = absolute_url(anchor.href, page)
            if same_host(target, page):
                continue
            if target.lower().startswith("http://"):
                issues.append(
                    issue(
                        self.family,
                        "https",
                        "external_link_http",
                        "External link uses HTTP.",
                        severity="minor",
                        details=target,
                    ),
                )
        return issues


class AnchorAnalyzer:
    """Analyze anchor texts."""

    family = "anchors"
    weak_texts = {"click here", "cliquez ici", "here", "ici"}

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        texts = [anchor.text.strip().lower() for anchor in document.anchors]
        counts = Counter(text for text in texts if text)
        issues: list[SeoIssue] = []
        for anchor in document.anchors:
            text = anchor.text.strip().lower()
            if not text:
                issues.append(issue(self.family, "empty", "anchor_empty", "Anchor text is empty."))
            elif text in self.weak_texts:
                issues.append(
                    issue(
                        self.family,
                        "generic",
                        "anchor_generic_text",
                        "Anchor text is generic.",
                        severity="minor",
                        details=anchor.text,
                    ),
                )
        for text, count in counts.items():
            if count > 5:
                issues.append(
                    issue(
                        self.family,
                        "repetition",
                        "anchor_text_repeated",
                        "Anchor text is repeated many times.",
                        severity="minor",
                        details=text,
                    ),
                )
        return issues
