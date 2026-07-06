"""Small HTML parser used by deterministic SEO analyzers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any


@dataclass(frozen=True)
class LinkElement:
    """Anchor element extracted from HTML."""

    href: str
    text: str


@dataclass(frozen=True)
class HeadingElement:
    """Heading element extracted from HTML."""

    level: int
    text: str


@dataclass
class HtmlDocument:
    """Parsed HTML document data used by analyzers."""

    raw_html: str
    title_values: list[str] = field(default_factory=list)
    meta_tags: list[dict[str, str]] = field(default_factory=list)
    link_tags: list[dict[str, str]] = field(default_factory=list)
    anchors: list[LinkElement] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    headings: list[HeadingElement] = field(default_factory=list)
    json_ld_blocks: list[str] = field(default_factory=list)
    scripts_count: int = 0
    css_count: int = 0
    iframe_count: int = 0
    landmark_counts: dict[str, int] = field(default_factory=dict)
    html_lang: str | None = None
    text: str = ""

    def meta_by_name(self, name: str) -> dict[str, str] | None:
        """Return the first meta tag matching a name."""

        expected = name.lower()
        return next((tag for tag in self.meta_tags if tag.get("name", "").lower() == expected), None)

    def meta_by_property(self, property_name: str) -> dict[str, str] | None:
        """Return the first meta tag matching a property."""

        expected = property_name.lower()
        return next((tag for tag in self.meta_tags if tag.get("property", "").lower() == expected), None)

    def link_by_rel(self, rel_name: str) -> dict[str, str] | None:
        """Return the first link tag containing a rel value."""

        expected = rel_name.lower()
        return next((tag for tag in self.link_tags if expected in _rel_values(tag)), None)

    def links_by_rel(self, rel_name: str) -> list[dict[str, str]]:
        """Return all link tags containing a rel value."""

        expected = rel_name.lower()
        return [tag for tag in self.link_tags if expected in _rel_values(tag)]

    @property
    def title(self) -> str | None:
        """Return the first title value."""

        return self.title_values[0] if self.title_values else None

    @property
    def meta_description(self) -> str | None:
        """Return the meta description content."""

        tag = self.meta_by_name("description")
        return tag.get("content") if tag else None

    @property
    def charset(self) -> str | None:
        """Return the declared charset."""

        for tag in self.meta_tags:
            if tag.get("charset"):
                return tag["charset"]
            if tag.get("http-equiv", "").lower() == "content-type":
                match = re.search(r"charset=([^;\s]+)", tag.get("content", ""), re.IGNORECASE)
                if match:
                    return match.group(1)
        return None

    @property
    def schema_types(self) -> list[str]:
        """Return Schema.org types found in JSON-LD blocks."""

        types: list[str] = []
        for block in self.json_ld_blocks:
            try:
                payload = json.loads(block)
            except json.JSONDecodeError:
                continue
            types.extend(_jsonld_types(payload))
        return sorted(set(types))


class SeoHtmlParser(HTMLParser):
    """Extract deterministic SEO signals from HTML using the standard library."""

    def __init__(self, raw_html: str) -> None:
        super().__init__(convert_charrefs=True)
        self.document = HtmlDocument(raw_html=raw_html)
        self._title_parts: list[str] | None = None
        self._heading_parts: tuple[int, list[str]] | None = None
        self._anchor_stack: list[dict[str, Any]] = []
        self._jsonld_parts: list[str] | None = None
        self._ignored_text_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle HTML start tags."""

        tag_name = tag.lower()
        attr_map = _attrs(attrs)
        if tag_name == "html":
            self.document.html_lang = attr_map.get("lang")
        if tag_name == "title":
            self._title_parts = []
        if tag_name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_parts = (int(tag_name[1]), [])
        if tag_name == "a" and attr_map.get("href"):
            self._anchor_stack.append({"href": attr_map["href"], "parts": []})
        if tag_name == "img":
            self.document.images.append(attr_map)
        if tag_name == "meta":
            self.document.meta_tags.append(attr_map)
        if tag_name == "link":
            self.document.link_tags.append(attr_map)
            if "stylesheet" in _rel_values(attr_map):
                self.document.css_count += 1
        if tag_name == "style":
            self.document.css_count += 1
            self._ignored_text_depth += 1
        if tag_name == "script":
            self.document.scripts_count += 1
            if attr_map.get("type", "").lower() == "application/ld+json":
                self._jsonld_parts = []
            else:
                self._ignored_text_depth += 1
        if tag_name == "iframe":
            self.document.iframe_count += 1
        if tag_name in {"main", "nav", "header", "footer", "article", "section"}:
            self.document.landmark_counts[tag_name] = self.document.landmark_counts.get(tag_name, 0) + 1

    def handle_endtag(self, tag: str) -> None:
        """Handle HTML end tags."""

        tag_name = tag.lower()
        if tag_name == "title" and self._title_parts is not None:
            self.document.title_values.append(_clean(" ".join(self._title_parts)))
            self._title_parts = None
        if tag_name in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading_parts is not None:
            level, parts = self._heading_parts
            self.document.headings.append(HeadingElement(level=level, text=_clean(" ".join(parts))))
            self._heading_parts = None
        if tag_name == "a" and self._anchor_stack:
            current = self._anchor_stack.pop()
            self.document.anchors.append(LinkElement(href=current["href"], text=_clean(" ".join(current["parts"]))))
        if tag_name == "script":
            if self._jsonld_parts is not None:
                self.document.json_ld_blocks.append("\n".join(self._jsonld_parts).strip())
                self._jsonld_parts = None
            elif self._ignored_text_depth:
                self._ignored_text_depth -= 1
        if tag_name == "style" and self._ignored_text_depth:
            self._ignored_text_depth -= 1

    def handle_data(self, data: str) -> None:
        """Handle text data."""

        if self._title_parts is not None:
            self._title_parts.append(data)
        if self._heading_parts is not None:
            self._heading_parts[1].append(data)
        if self._anchor_stack:
            self._anchor_stack[-1]["parts"].append(data)
        if self._jsonld_parts is not None:
            self._jsonld_parts.append(data)
            return
        if not self._ignored_text_depth:
            cleaned = _clean(data)
            if cleaned:
                self.document.text += f" {cleaned}"


def parse_html(raw_html: str) -> HtmlDocument:
    """Parse raw HTML into deterministic signals."""

    parser = SeoHtmlParser(raw_html)
    parser.feed(raw_html)
    parser.close()
    parser.document.text = _clean(parser.document.text)
    return parser.document


def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {name.lower(): value or "" for name, value in attrs}


def _rel_values(tag: dict[str, str]) -> set[str]:
    return {value.strip().lower() for value in tag.get("rel", "").split() if value.strip()}


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _jsonld_types(payload: Any) -> list[str]:
    if isinstance(payload, list):
        return [item for entry in payload for item in _jsonld_types(entry)]
    if not isinstance(payload, dict):
        return []
    found: list[str] = []
    value = payload.get("@type")
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, list):
        found.extend(item for item in value if isinstance(item, str))
    graph = payload.get("@graph")
    if isinstance(graph, list):
        found.extend(item for entry in graph for item in _jsonld_types(entry))
    return found
