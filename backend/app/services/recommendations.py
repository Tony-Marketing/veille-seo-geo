"""Business service for the transverse recommendation engine."""

from dataclasses import dataclass
from datetime import UTC, datetime
from math import ceil
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from backend.app.models import Recommendation
from backend.app.repositories.recommendations import RecommendationRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.recommendations import (
    RecommendationDifficulty,
    RecommendationFilters,
    RecommendationImpact,
    RecommendationList,
    RecommendationPriority,
    RecommendationRead,
    RecommendationSource,
    RecommendationStatus,
    RecommendationSummary,
)
from backend.app.services.geo_intelligence import GeoIntelligenceService


@dataclass(frozen=True)
class RecommendationCandidate:
    """Normalized recommendation before persistence."""

    website_id: int | None
    source: RecommendationSource
    rule_code: str
    source_object_type: str
    source_object_id: str
    category: str
    title: str
    description: str
    priority: RecommendationPriority
    impact: RecommendationImpact
    score: float
    difficulty: RecommendationDifficulty | None = None
    metadata: dict[str, Any] | None = None


class RecommendationService:
    """Normalize, consolidate, deduplicate, prioritize and manage recommendations."""

    ALLOWED_TRANSITIONS = {
        RecommendationStatus.OPEN: {
            RecommendationStatus.ACKNOWLEDGED,
            RecommendationStatus.RESOLVED,
            RecommendationStatus.IGNORED,
        },
        RecommendationStatus.ACKNOWLEDGED: {
            RecommendationStatus.OPEN,
            RecommendationStatus.RESOLVED,
            RecommendationStatus.IGNORED,
        },
        RecommendationStatus.RESOLVED: {RecommendationStatus.OPEN},
        RecommendationStatus.IGNORED: {RecommendationStatus.OPEN},
    }

    def __init__(
        self,
        repository: RecommendationRepository,
        geo_intelligence_service: GeoIntelligenceService | None = None,
    ) -> None:
        self.repository = repository
        self.geo_intelligence_service = geo_intelligence_service

    def list_recommendations(
        self,
        params: PaginationParams,
        *,
        filters: RecommendationFilters | None = None,
        website_ids: list[int] | None = None,
        synchronize: bool = True,
    ) -> RecommendationList:
        """Synchronize and return paginated persisted recommendations."""

        filters = filters or RecommendationFilters()
        if synchronize:
            self.synchronize()
        try:
            items, total = self.repository.list_recommendations(
                params,
                filters=filters,
                website_ids=website_ids,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        return RecommendationList(
            items=[self._read(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=self._filters_dict(filters),
        )

    def get_recommendation(self, recommendation_id: int) -> RecommendationRead:
        """Return one persisted recommendation."""

        return self._read(self._get_model(recommendation_id))

    def summary(
        self,
        *,
        filters: RecommendationFilters | None = None,
        website_ids: list[int] | None = None,
    ) -> RecommendationSummary:
        """Synchronize and return reusable recommendation counters."""

        filters = filters or RecommendationFilters()
        self.synchronize()
        by_status = self.repository.grouped_counts("status", filters=filters, website_ids=website_ids)
        by_priority = self.repository.grouped_counts("priority", filters=filters, website_ids=website_ids)
        by_category = self.repository.grouped_counts("category", filters=filters, website_ids=website_ids)
        recent = self.list_recommendations(
            PaginationParams(page=1, page_size=5, sort="created_at", order="desc"),
            filters=filters,
            website_ids=website_ids,
            synchronize=False,
        )
        return RecommendationSummary(
            total=sum(by_status.values()),
            open=by_status.get(RecommendationStatus.OPEN.value, 0),
            acknowledged=by_status.get(RecommendationStatus.ACKNOWLEDGED.value, 0),
            resolved=by_status.get(RecommendationStatus.RESOLVED.value, 0),
            ignored=by_status.get(RecommendationStatus.IGNORED.value, 0),
            critical=by_priority.get(RecommendationPriority.CRITICAL.value, 0),
            high=by_priority.get(RecommendationPriority.HIGH.value, 0),
            medium=by_priority.get(RecommendationPriority.MEDIUM.value, 0),
            low=by_priority.get(RecommendationPriority.LOW.value, 0),
            by_priority=by_priority,
            by_category=by_category,
            recent=recent.items,
            generated_at=datetime.now(UTC),
        )

    def update_status(self, recommendation_id: int, target: RecommendationStatus) -> RecommendationRead:
        """Apply one explicit and validated lifecycle transition."""

        item = self._get_model(recommendation_id)
        current = RecommendationStatus(item.status)
        if current == target:
            return self._read(item)
        if target not in self.ALLOWED_TRANSITIONS[current]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transition de recommandation interdite: {current.value} vers {target.value}.",
            )
        self.repository.update_pending(item, {"status": target.value})
        self.repository.commit()
        return self._read(self._get_model(recommendation_id))

    def synchronize(self) -> None:
        """Consolidate every supported persisted source without executing an analyzer or connector."""

        candidates = self._candidates()
        unique_candidates = {self.deduplication_key(candidate): candidate for candidate in candidates}
        try:
            for key in sorted(unique_candidates):
                candidate = unique_candidates[key]
                data = self._candidate_data(candidate, key)
                existing = self.repository.get_by_deduplication_key(key)
                if existing is None:
                    self.repository.add_pending(data)
                    continue
                data.pop("status")
                self.repository.update_pending(existing, data)
            self.repository.commit()
        except IntegrityError as exc:
            self.repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Consolidation concurrente des recommandations. Reessayez.",
            ) from exc

    @staticmethod
    def deduplication_key(candidate: RecommendationCandidate) -> str:
        """Build the stable business key without title or description."""

        website = str(candidate.website_id) if candidate.website_id is not None else "global"
        return "|".join(
            (
                website,
                candidate.source.value,
                candidate.rule_code,
                candidate.source_object_type,
                candidate.source_object_id,
            ),
        )

    def _candidates(self) -> list[RecommendationCandidate]:
        alerts = self.repository.active_alert_rows()
        covered_monitoring_ids = {
            str(row["item"].source_id)
            for row in alerts
            if row["item"].source_type == "monitoring" and row["item"].source_id is not None
        }
        return [
            *self._seo_candidates(),
            *self._geo_candidates(),
            *self._alert_candidates(alerts),
            *self._monitoring_candidates(covered_monitoring_ids),
            *self._gsc_candidates(),
            *self._ga4_candidates(),
            *self._bing_candidates(),
            *self._geo_intelligence_candidates(),
        ]

    def _geo_intelligence_candidates(self) -> list[RecommendationCandidate]:
        if self.geo_intelligence_service is None:
            return []
        priority_map = {
            "low_visibility": (RecommendationPriority.HIGH, 75.0),
            "significant_decrease": (RecommendationPriority.HIGH, 85.0),
            "citation_loss": (RecommendationPriority.HIGH, 80.0),
            "insufficient_source_diversity": (RecommendationPriority.MEDIUM, 55.0),
            "provider_absence": (RecommendationPriority.HIGH, 90.0),
        }
        candidates = []
        for signal in self.geo_intelligence_service.recommendation_signals():
            priority, score = priority_map[signal.rule_code]
            candidates.append(
                RecommendationCandidate(
                    website_id=signal.website_id,
                    source=RecommendationSource.GEO_INTELLIGENCE,
                    rule_code=signal.rule_code,
                    source_object_type="geo_visibility_scope",
                    source_object_id=signal.source_object_id,
                    category="geo_intelligence",
                    title=signal.title,
                    description=signal.description,
                    priority=priority,
                    impact=RecommendationImpact.GEO,
                    score=score,
                    metadata={
                        "rule_code": signal.rule_code,
                        "source_object_type": "geo_visibility_scope",
                        "source_object_id": signal.source_object_id,
                        "provider": signal.provider,
                        "prompt": signal.prompt,
                        "entity": signal.entity,
                        "ranking_factors": signal.factors,
                    },
                ),
            )
        return candidates

    def _seo_candidates(self) -> list[RecommendationCandidate]:
        candidates = []
        for row in self.repository.seo_issue_rows():
            item = row["item"]
            priority, score = self._severity_priority(item.severity)
            candidates.append(
                RecommendationCandidate(
                    website_id=self._website_id(row.get("website_id")),
                    source=RecommendationSource.SEO,
                    rule_code=str(item.code),
                    source_object_type="seo_analysis_issue",
                    source_object_id=str(item.id),
                    category=str(item.family),
                    title=f"Corriger l'issue SEO {item.code}",
                    description=str(item.message),
                    priority=priority,
                    impact=RecommendationImpact.SEO,
                    score=score,
                    metadata=self._metadata(
                        item,
                        rule_code=str(item.code),
                        source_object_type="seo_analysis_issue",
                        factors={"severity": item.severity, "criterion": item.criterion},
                    ),
                ),
            )
        return candidates

    def _geo_candidates(self) -> list[RecommendationCandidate]:
        candidates = []
        for row in self.repository.geo_recommendation_rows():
            item = row["item"]
            priority, score = self._geo_priority(item.priority)
            candidates.append(
                RecommendationCandidate(
                    website_id=self._website_id(row.get("website_id")),
                    source=RecommendationSource.GEO,
                    rule_code=str(item.recommendation_type),
                    source_object_type="geo_recommendation",
                    source_object_id=str(item.id),
                    category=str(item.recommendation_type),
                    title=str(item.title),
                    description=str(item.description),
                    priority=priority,
                    impact=RecommendationImpact.GEO,
                    score=score,
                    metadata=self._metadata(
                        item,
                        rule_code=str(item.recommendation_type),
                        source_object_type="geo_recommendation",
                        factors={
                            "source_priority": item.priority,
                            "severity": item.severity,
                            "impact_score": item.impact_score,
                        },
                    ),
                ),
            )
        return candidates

    def _alert_candidates(self, rows: list[dict[str, Any]]) -> list[RecommendationCandidate]:
        candidates = []
        for row in rows:
            item = row["item"]
            priority, score = self._alert_priority(item.severity)
            candidates.append(
                RecommendationCandidate(
                    website_id=self._website_id((item.metadata_ or {}).get("website_id")),
                    source=RecommendationSource.ALERTS,
                    rule_code="active_alert",
                    source_object_type="alert",
                    source_object_id=str(item.id),
                    category=str(item.category),
                    title=f"Traiter l'alerte : {item.title}",
                    description=str(item.message),
                    priority=priority,
                    impact=self._alert_impact(item.category),
                    score=score,
                    metadata=self._metadata(
                        item,
                        rule_code="active_alert",
                        source_object_type="alert",
                        factors={"severity": item.severity, "alert_status": item.status},
                    ),
                ),
            )
        return candidates

    def _monitoring_candidates(self, covered_ids: set[str]) -> list[RecommendationCandidate]:
        candidates = []
        for row in self.repository.monitoring_event_rows():
            item = row["item"]
            if str(item.id) in covered_ids or str(item.severity).lower() not in {"error", "critical"}:
                continue
            priority, score = self._severity_priority(item.severity)
            candidates.append(
                RecommendationCandidate(
                    website_id=self._website_id((item.details or {}).get("website_id")),
                    source=RecommendationSource.MONITORING,
                    rule_code=f"monitoring_{item.event_type}",
                    source_object_type="monitoring_event",
                    source_object_id=str(item.id),
                    category=str(item.event_type),
                    title=f"Traiter l'evenement {item.event_type}",
                    description=str(item.message),
                    priority=priority,
                    impact=RecommendationImpact.TECHNIQUE,
                    score=score,
                    metadata=self._metadata(
                        item,
                        rule_code=f"monitoring_{item.event_type}",
                        source_object_type="monitoring_event",
                        factors={"severity": item.severity, "event_source": item.source},
                    ),
                ),
            )
        return candidates

    def _gsc_candidates(self) -> list[RecommendationCandidate]:
        candidates = []
        for row in self.repository.gsc_performance_rows():
            item = row["item"]
            if item.impressions <= 0 or item.ctr >= 0.02:
                continue
            candidates.append(
                RecommendationCandidate(
                    website_id=self._website_id(row.get("website_id")),
                    source=RecommendationSource.GSC,
                    rule_code="gsc_low_ctr",
                    source_object_type="gsc_performance",
                    source_object_id=str(item.id),
                    category="search_performance",
                    title="Ameliorer le CTR Google Search Console",
                    description="Les impressions existent mais le CTR est inferieur a 2 %.",
                    priority=RecommendationPriority.HIGH,
                    impact=RecommendationImpact.SEO,
                    score=70.0,
                    metadata=self._metadata(
                        item,
                        rule_code="gsc_low_ctr",
                        source_object_type="gsc_performance",
                        factors={"ctr": item.ctr, "clicks": item.clicks, "impressions": item.impressions},
                    ),
                ),
            )
        return candidates

    def _ga4_candidates(self) -> list[RecommendationCandidate]:
        candidates = []
        for row in self.repository.ga4_metric_rows():
            item = row["item"]
            if item.sessions <= 0 or item.engagement_rate >= 0.3:
                continue
            candidates.append(
                RecommendationCandidate(
                    website_id=self._website_id(row.get("website_id")),
                    source=RecommendationSource.GA4,
                    rule_code="ga4_low_engagement",
                    source_object_type="ga4_metric",
                    source_object_id=str(item.id),
                    category="engagement",
                    title="Surveiller l'engagement GA4",
                    description="Le taux d'engagement GA4 est inferieur a 0.3.",
                    priority=RecommendationPriority.MEDIUM,
                    impact=RecommendationImpact.BUSINESS,
                    score=55.0,
                    metadata=self._metadata(
                        item,
                        rule_code="ga4_low_engagement",
                        source_object_type="ga4_metric",
                        factors={"engagement_rate": item.engagement_rate, "sessions": item.sessions},
                    ),
                ),
            )
        return candidates

    def _bing_candidates(self) -> list[RecommendationCandidate]:
        candidates = []
        for row in self.repository.bing_crawl_rows():
            item = row["item"]
            has_error = (item.http_status is not None and item.http_status >= 400) or bool(item.issue_type)
            has_error = has_error or str(item.severity or "").lower() in {"error", "critical"}
            if not has_error:
                continue
            candidates.append(
                RecommendationCandidate(
                    website_id=self._website_id(row.get("website_id")),
                    source=RecommendationSource.BING,
                    rule_code="bing_crawl_error",
                    source_object_type="bing_crawl_stat",
                    source_object_id=str(item.id),
                    category="crawl",
                    title="Corriger une erreur de crawl Bing",
                    description=str(item.details or item.issue_type or f"Erreur HTTP {item.http_status}."),
                    priority=RecommendationPriority.HIGH,
                    impact=RecommendationImpact.TECHNIQUE,
                    score=75.0,
                    metadata=self._metadata(
                        item,
                        rule_code="bing_crawl_error",
                        source_object_type="bing_crawl_stat",
                        factors={"http_status": item.http_status, "severity": item.severity, "url": item.url},
                    ),
                ),
            )
        for row in self.repository.bing_sitemap_rows():
            item = row["item"]
            invalid_status = str(item.status or "").lower() in {"error", "failed", "invalid"}
            if item.error_count <= 0 and not invalid_status:
                continue
            candidates.append(
                RecommendationCandidate(
                    website_id=self._website_id(row.get("website_id")),
                    source=RecommendationSource.BING,
                    rule_code="bing_sitemap_invalid",
                    source_object_type="bing_sitemap",
                    source_object_id=str(item.id),
                    category="sitemap",
                    title="Corriger un sitemap Bing invalide",
                    description=f"Le sitemap contient {item.error_count} erreur(s).",
                    priority=RecommendationPriority.HIGH,
                    impact=RecommendationImpact.TECHNIQUE,
                    score=80.0,
                    metadata=self._metadata(
                        item,
                        rule_code="bing_sitemap_invalid",
                        source_object_type="bing_sitemap",
                        factors={"errors": item.error_count, "warnings": item.warning_count, "status": item.status},
                    ),
                ),
            )
        return candidates

    def _candidate_data(self, candidate: RecommendationCandidate, key: str) -> dict[str, Any]:
        return {
            "website_id": candidate.website_id,
            "source": candidate.source.value,
            "source_id": candidate.source_object_id,
            "category": candidate.category,
            "title": candidate.title,
            "description": candidate.description,
            "priority": candidate.priority.value,
            "impact": candidate.impact.value,
            "difficulty": candidate.difficulty.value if candidate.difficulty is not None else None,
            "score": candidate.score,
            "status": RecommendationStatus.OPEN.value,
            "deduplication_key": key,
            "metadata_": candidate.metadata,
        }

    def _metadata(
        self,
        item: Any,
        *,
        rule_code: str,
        source_object_type: str,
        factors: dict[str, Any],
    ) -> dict[str, Any]:
        created_at = getattr(item, "created_at", None)
        return {
            "rule_code": rule_code,
            "source_object_type": source_object_type,
            "source_object_id": str(item.id),
            "source_created_at": created_at.isoformat() if isinstance(created_at, datetime) else None,
            "ranking_factors": factors,
        }

    def _read(self, item: Recommendation) -> RecommendationRead:
        return RecommendationRead(
            id=item.id,
            website_id=item.website_id,
            website_name=item.website.name if item.website is not None else None,
            source=item.source,
            source_id=item.source_id,
            category=item.category,
            title=item.title,
            description=item.description,
            priority=item.priority,
            impact=item.impact,
            difficulty=item.difficulty,
            score=item.score,
            status=item.status,
            deduplication_key=item.deduplication_key,
            metadata_=item.metadata_,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    def _get_model(self, recommendation_id: int) -> Recommendation:
        item = self.repository.get_recommendation(recommendation_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommandation introuvable.")
        return item

    def _filters_dict(self, filters: RecommendationFilters) -> dict[str, Any]:
        return filters.model_dump(mode="json", exclude_none=True)

    def _severity_priority(self, severity: str) -> tuple[RecommendationPriority, float]:
        value = str(severity).lower()
        if value in {"critical", "blocker"}:
            return RecommendationPriority.CRITICAL, 100.0
        if value in {"major", "high", "error"}:
            return RecommendationPriority.HIGH, 80.0
        if value in {"warning", "medium"}:
            return RecommendationPriority.MEDIUM, 55.0
        return RecommendationPriority.LOW, 30.0

    def _geo_priority(self, priority: int) -> tuple[RecommendationPriority, float]:
        if priority <= 1:
            return RecommendationPriority.CRITICAL, 100.0
        if priority == 2:
            return RecommendationPriority.HIGH, 85.0
        if priority == 3:
            return RecommendationPriority.MEDIUM, 60.0
        return RecommendationPriority.LOW, 30.0

    def _alert_priority(self, severity: str) -> tuple[RecommendationPriority, float]:
        value = str(severity).lower()
        if value == "critical":
            return RecommendationPriority.CRITICAL, 95.0
        if value == "warning":
            return RecommendationPriority.HIGH, 75.0
        return RecommendationPriority.MEDIUM, 50.0

    def _alert_impact(self, category: str) -> RecommendationImpact:
        value = str(category).lower()
        if value == "seo":
            return RecommendationImpact.SEO
        if value == "geo":
            return RecommendationImpact.GEO
        if value in {"performance", "crawl"}:
            return RecommendationImpact.PERFORMANCE
        return RecommendationImpact.TECHNIQUE

    def _website_id(self, value: Any) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None
