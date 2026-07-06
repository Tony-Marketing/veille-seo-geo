"""SEO analyzer registry."""

from backend.app.seo.analyzers.content import LandmarkAnalyzer, LanguageAnalyzer, ReadabilityAnalyzer
from backend.app.seo.analyzers.headings import H1Analyzer, H2Analyzer, HeadingHierarchyAnalyzer
from backend.app.seo.analyzers.http import HttpAnalyzer
from backend.app.seo.analyzers.links import AnchorAnalyzer, ExternalLinksAnalyzer, InternalLinksAnalyzer
from backend.app.seo.analyzers.media import ImageAnalyzer
from backend.app.seo.analyzers.metadata import (
    CanonicalAnalyzer,
    CharsetAnalyzer,
    FaviconAnalyzer,
    MetaDescriptionAnalyzer,
    OpenGraphAnalyzer,
    PaginationAnalyzer,
    RobotsAnalyzer,
    TitleAnalyzer,
    TwitterCardAnalyzer,
    ViewportAnalyzer,
)
from backend.app.seo.analyzers.performance import HtmlPerformanceAnalyzer
from backend.app.seo.analyzers.structured_data import HreflangAnalyzer, JsonLdAnalyzer, SchemaOrgAnalyzer
from backend.app.seo.analyzers.types import Analyzer

DEFAULT_ANALYZERS: tuple[Analyzer, ...] = (
    HttpAnalyzer(),
    TitleAnalyzer(),
    MetaDescriptionAnalyzer(),
    CanonicalAnalyzer(),
    RobotsAnalyzer(),
    H1Analyzer(),
    H2Analyzer(),
    HeadingHierarchyAnalyzer(),
    ImageAnalyzer(),
    OpenGraphAnalyzer(),
    TwitterCardAnalyzer(),
    JsonLdAnalyzer(),
    SchemaOrgAnalyzer(),
    HreflangAnalyzer(),
    InternalLinksAnalyzer(),
    ExternalLinksAnalyzer(),
    AnchorAnalyzer(),
    HtmlPerformanceAnalyzer(),
    ReadabilityAnalyzer(),
    LanguageAnalyzer(),
    CharsetAnalyzer(),
    ViewportAnalyzer(),
    FaviconAnalyzer(),
    PaginationAnalyzer(),
    LandmarkAnalyzer(),
)

__all__ = ["DEFAULT_ANALYZERS"]
