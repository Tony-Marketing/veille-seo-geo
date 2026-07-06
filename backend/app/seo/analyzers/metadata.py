"""Metadata-oriented SEO analyzers."""

from backend.app.seo.analyzers.helpers import is_absolute_url, issue
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class TitleAnalyzer:
    """Analyze title tags."""

    family = "title"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        issues: list[SeoIssue] = []
        title = document.title
        if title is None:
            return [issue(self.family, "presence", "title_missing", "Title tag is missing.")]
        if not title:
            issues.append(issue(self.family, "empty", "title_empty", "Title tag is empty."))
        if len(document.title_values) > 1:
            issues.append(issue(self.family, "duplicates", "title_multiple", "Multiple title tags found."))
        if title and len(title) > 70:
            issues.append(issue(self.family, "length", "title_too_long", "Title tag is too long.", severity="minor"))
        if title and len(title) < 10:
            issues.append(issue(self.family, "length", "title_too_short", "Title tag is too short.", severity="minor"))
        return issues


class MetaDescriptionAnalyzer:
    """Analyze meta descriptions."""

    family = "meta_description"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        descriptions = [
            tag.get("content", "")
            for tag in document.meta_tags
            if tag.get("name", "").lower() == "description"
        ]
        if not descriptions:
            return [issue(self.family, "presence", "meta_description_missing", "Meta description is missing.")]
        description = descriptions[0].strip()
        issues: list[SeoIssue] = []
        if not description:
            issues.append(issue(self.family, "empty", "meta_description_empty", "Meta description is empty."))
        if len(descriptions) > 1:
            issues.append(
                issue(self.family, "duplicates", "meta_description_multiple", "Multiple meta descriptions found."),
            )
        if description and len(description) > 160:
            issues.append(
                issue(self.family, "length", "meta_description_too_long", "Meta description is too long."),
            )
        if description and len(description) < 50:
            issues.append(
                issue(
                    self.family,
                    "length",
                    "meta_description_too_short",
                    "Meta description is too short.",
                    severity="minor",
                ),
            )
        return issues


class CanonicalAnalyzer:
    """Analyze canonical link tags."""

    family = "canonical"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        canonical = document.link_by_rel("canonical")
        if canonical is None:
            return [issue(self.family, "presence", "canonical_missing", "Canonical URL is missing.")]
        href = canonical.get("href", "").strip()
        issues: list[SeoIssue] = []
        if not href:
            issues.append(issue(self.family, "empty", "canonical_empty", "Canonical URL is empty."))
        elif not is_absolute_url(href):
            issues.append(issue(self.family, "absolute", "canonical_not_absolute", "Canonical URL is not absolute."))
        elif href.rstrip("/") != page.effective_url.rstrip("/"):
            issues.append(
                issue(
                    self.family,
                    "self_reference",
                    "canonical_different",
                    "Canonical URL differs from the page URL.",
                    severity="minor",
                    details=href,
                ),
            )
        return issues


class RobotsAnalyzer:
    """Analyze meta robots directives."""

    family = "robots"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        robots = document.meta_by_name("robots")
        directives = robots.get("content", "").lower() if robots else ""
        if "noindex" in directives:
            return [issue(self.family, "meta_robots", "robots_noindex", "Meta robots contains noindex.")]
        if "nofollow" in directives:
            return [
                issue(
                    self.family,
                    "meta_robots",
                    "robots_nofollow",
                    "Meta robots contains nofollow.",
                    severity="minor",
                ),
            ]
        return []


class OpenGraphAnalyzer:
    """Analyze Open Graph tags."""

    family = "open_graph"
    required_properties = ("og:title", "og:description", "og:url", "og:image")

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        return [
            issue(
                self.family,
                "presence",
                "open_graph_missing_property",
                "Open Graph property is missing.",
                severity="minor",
                details=property_name,
            )
            for property_name in self.required_properties
            if document.meta_by_property(property_name) is None
        ]


class TwitterCardAnalyzer:
    """Analyze Twitter Card tags."""

    family = "twitter_cards"
    required_names = ("twitter:card", "twitter:title", "twitter:description", "twitter:image")

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        return [
            issue(
                self.family,
                "presence",
                "twitter_card_missing_tag",
                "Twitter Card tag is missing.",
                severity="minor",
                details=name,
            )
            for name in self.required_names
            if document.meta_by_name(name) is None
        ]


class CharsetAnalyzer:
    """Analyze charset declaration."""

    family = "charset"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None or document.charset:
            return []
        return [issue(self.family, "presence", "charset_missing", "Charset declaration is missing.")]


class ViewportAnalyzer:
    """Analyze viewport declaration."""

    family = "viewport"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None or document.meta_by_name("viewport") is not None:
            return []
        return [issue(self.family, "presence", "viewport_missing", "Viewport meta tag is missing.")]


class FaviconAnalyzer:
    """Analyze favicon declaration."""

    family = "favicon"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        has_favicon = any(
            {"icon", "shortcut icon"} & set(tag.get("rel", "").lower().split()) for tag in document.link_tags
        )
        if has_favicon:
            return []
        return [issue(self.family, "presence", "favicon_missing", "Favicon link is missing.", severity="minor")]


class PaginationAnalyzer:
    """Analyze prev/next pagination links."""

    family = "pagination"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        issues: list[SeoIssue] = []
        for rel in ("prev", "next"):
            for tag in document.links_by_rel(rel):
                if not tag.get("href", "").strip():
                    issues.append(
                        issue(
                            self.family,
                            rel,
                            "pagination_empty_href",
                            "Pagination link has an empty href.",
                            severity="minor",
                            details=rel,
                        ),
                    )
        return issues
