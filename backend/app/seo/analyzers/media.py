"""Media analyzers."""

from backend.app.seo.analyzers.helpers import issue
from backend.app.seo.models import SeoAnalysisContext, SeoIssue, SeoPageInput
from backend.app.seo.parser import HtmlDocument


class ImageAnalyzer:
    """Analyze image markup without downloading images."""

    family = "images"

    def analyze(
        self,
        page: SeoPageInput,
        document: HtmlDocument | None,
        context: SeoAnalysisContext,
    ) -> list[SeoIssue]:
        if document is None:
            return []
        issues: list[SeoIssue] = []
        for index, image in enumerate(document.images, start=1):
            details = image.get("src") or f"image #{index}"
            if "alt" not in image or not image.get("alt", "").strip():
                issues.append(
                    issue(self.family, "alt", "image_alt_missing", "Image alt attribute is missing.", details=details),
                )
            if "loading" not in image:
                issues.append(
                    issue(
                        self.family,
                        "lazy_loading",
                        "image_lazy_loading_missing",
                        "Image loading attribute is missing.",
                        severity="minor",
                        details=details,
                    ),
                )
            if "width" not in image or "height" not in image:
                issues.append(
                    issue(
                        self.family,
                        "dimensions",
                        "image_dimensions_missing",
                        "Image dimensions are missing.",
                        severity="minor",
                        details=details,
                    ),
                )
        return issues
