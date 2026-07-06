"""Tests for the SEO HTML parser."""

from backend.app.seo.parser import parse_html


def test_parser_extracts_core_html_signals() -> None:
    """The parser extracts metadata, headings, links and schema types."""

    document = parse_html(
        """
        <html lang="fr">
          <head>
            <title>Example</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width">
            <link rel="canonical" href="https://example.com/">
            <script type="application/ld+json">{"@type":"Organization"}</script>
          </head>
          <body>
            <main><h1>Heading</h1><a href="/about">About</a></main>
          </body>
        </html>
        """,
    )

    assert document.title == "Example"
    assert document.html_lang == "fr"
    assert document.charset == "utf-8"
    assert document.link_by_rel("canonical") is not None
    assert document.headings[0].text == "Heading"
    assert document.anchors[0].href == "/about"
    assert document.schema_types == ["Organization"]
