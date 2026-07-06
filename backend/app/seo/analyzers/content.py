"""Content and semantic HTML analyzers."""

import re

from backend.app.seo.analyzers.helpers import issue
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class ReadabilityAnalyzer:
    """Analyze deterministic text readability metrics without AI."""

    family = "readability"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        words = re.findall(r"\w+", document.text)
        sentences = [part for part in re.split(r"[.!?]+", document.text) if part.strip()]
        issues: list[SeoIssue] = []
        if not words:
            issues.append(issue(self.family, "words", "readability_no_text", "No readable text found."))
        elif len(words) < 50:
            issues.append(
                issue(self.family, "words", "readability_low_word_count", "Readable text is very short."),
            )
        if sentences and len(words) / len(sentences) > 35:
            issues.append(
                issue(
                    self.family,
                    "sentences",
                    "readability_long_sentences",
                    "Average sentence length is high.",
                    severity="minor",
                ),
            )
        return issues


class LanguageAnalyzer:
    """Analyze html lang declaration."""

    family = "language"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None or document.html_lang:
            return []
        return [issue(self.family, "html_lang", "language_missing", "HTML lang attribute is missing.")]


class LandmarkAnalyzer:
    """Analyze important semantic HTML tags."""

    family = "html_landmarks"
    expected_tags = ("main", "nav", "header", "footer")

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
                "html_landmark_missing",
                "Important semantic HTML tag is missing.",
                severity="minor",
                details=tag,
            )
            for tag in self.expected_tags
            if document.landmark_counts.get(tag, 0) == 0
        ]
