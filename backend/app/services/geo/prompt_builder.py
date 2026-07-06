"""Prompt construction for GEO providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MAX_HTML_EXCERPT_CHARS = 8000


@dataclass(frozen=True)
class GeoPromptContext:
    """Structured data used to build provider-independent GEO prompts."""

    page: dict[str, Any]
    raw_html: str | None
    seo_page_analysis: dict[str, Any] | None = None
    seo_issues: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


class GeoPromptBuilder:
    """Build provider-independent prompts from crawl, HTML and SEO data."""

    def build(self, context: GeoPromptContext) -> str:
        """Return a stable prompt for GEO analysis."""

        html_excerpt = self._html_excerpt(context.raw_html)
        page = context.page
        seo_page = context.seo_page_analysis or {}
        issues = context.seo_issues
        metrics = context.metrics
        issue_lines = "\n".join(
            f"- {issue.get('severity', 'unknown')} | {issue.get('family', 'unknown')} | {issue.get('message', '')}"
            for issue in issues[:30]
        )
        if not issue_lines:
            issue_lines = "- Aucun probleme SEO connu pour cette page."

        return "\n".join(
            [
                "Tu es un analyste GEO specialise dans la visibilite des pages web dans les IA generatives.",
                "Analyse uniquement les donnees fournies. Ne suppose pas de donnees externes.",
                "",
                "Objectifs:",
                "- evaluer la comprehension de la page par un LLM;",
                "- evaluer la citabilite et la clarte des entites;",
                "- proposer des recommandations SEO, GEO et editoriales;",
                "- retourner une sortie structuree exploitable par le moteur GEO.",
                "",
                "Page:",
                f"- URL: {page.get('url') or ''}",
                f"- URL finale: {page.get('final_url') or ''}",
                f"- Code HTTP: {page.get('status_code') or ''}",
                f"- Type de contenu: {page.get('content_type') or ''}",
                "",
                "Resultats SEO:",
                f"- Statut SEO page: {seo_page.get('status') or ''}",
                f"- Score SEO page: {seo_page.get('score') or ''}",
                f"- Nombre d'issues SEO: {len(issues)}",
                "",
                "Metriques utiles:",
                f"- Taille HTML: {metrics.get('html_length', 0)} caracteres",
                f"- Nombre de mots approx.: {metrics.get('word_count', 0)}",
                "",
                "Issues SEO principales:",
                issue_lines,
                "",
                "HTML persiste extrait:",
                html_excerpt,
                "",
                "Format attendu:",
                "Retourner des signaux GEO, des signaux LLM, une synthese et une liste de recommandations.",
            ],
        )

    def build_context(
        self,
        *,
        page: dict[str, Any],
        raw_html: str | None,
        seo_page_analysis: dict[str, Any] | None,
        seo_issues: list[dict[str, Any]],
    ) -> GeoPromptContext:
        """Return a structured prompt context with basic deterministic metrics."""

        html = raw_html or ""
        return GeoPromptContext(
            page=page,
            raw_html=raw_html,
            seo_page_analysis=seo_page_analysis,
            seo_issues=seo_issues,
            metrics={
                "html_length": len(html),
                "word_count": len(html.split()),
                "seo_issue_count": len(seo_issues),
            },
        )

    def _html_excerpt(self, raw_html: str | None) -> str:
        if not raw_html:
            return "[HTML manquant]"
        if len(raw_html) <= MAX_HTML_EXCERPT_CHARS:
            return raw_html
        return f"{raw_html[:MAX_HTML_EXCERPT_CHARS]}\n[HTML tronque pour analyse GEO]"
