"""HTML link extraction for the crawler engine."""

from html.parser import HTMLParser


class _AnchorParser(HTMLParser):
    """Collect href attributes from anchor tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.links.append(value.strip())


class LinkExtractor:
    """Extract links from HTML payloads."""

    def extract(self, html: str) -> list[str]:
        """Return raw href values found in anchor tags."""

        parser = _AnchorParser()
        parser.feed(html)
        parser.close()
        return parser.links

