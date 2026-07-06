"""Structured data analyzers."""

from backend.app.seo.analyzers.helpers import issue
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class JsonLdAnalyzer:
    """Analyze JSON-LD presence and validity."""

    family = "json_ld"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        if not document.json_ld_blocks:
            return [issue(self.family, "presence", "json_ld_missing", "JSON-LD block is missing.", severity="minor")]
        if not document.schema_types:
            return [
                issue(
                    self.family,
                    "validity",
                    "json_ld_without_schema_type",
                    "JSON-LD block has no detectable Schema.org type or is invalid.",
                ),
            ]
        return []


class SchemaOrgAnalyzer:
    """Analyze Schema.org type detection."""

    family = "schema_org"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None or document.schema_types:
            return []
        return [
            issue(
                self.family,
                "types",
                "schema_org_type_missing",
                "No Schema.org type was detected.",
                severity="minor",
            ),
        ]


class HreflangAnalyzer:
    """Analyze hreflang link declarations."""

    family = "hreflang"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        alternates = document.links_by_rel("alternate")
        hreflang_tags = [tag for tag in alternates if "hreflang" in tag]
        if not hreflang_tags:
            return []
        issues: list[SeoIssue] = []
        has_default = False
        for tag in hreflang_tags:
            lang = tag.get("hreflang", "").strip()
            href = tag.get("href", "").strip()
            has_default = has_default or lang.lower() == "x-default"
            if not lang or not href:
                issues.append(issue(self.family, "validity", "hreflang_invalid", "hreflang tag is incomplete."))
        if not has_default:
            issues.append(
                issue(
                    self.family,
                    "x_default",
                    "hreflang_x_default_missing",
                    "hreflang x-default is missing.",
                    severity="minor",
                ),
            )
        return issues
