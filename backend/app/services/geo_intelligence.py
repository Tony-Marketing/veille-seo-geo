"""Business logic for normalized multi-provider GEO Intelligence data."""

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from math import ceil
from statistics import fmean
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from backend.app.connectors.geo_intelligence import (
    GeoIntelligenceConnector,
    NotConfiguredGeoIntelligenceConnector,
)
from backend.app.models import GeoVisibilitySnapshot
from backend.app.repositories.geo_intelligence import GeoIntelligenceRepository
from backend.app.schemas.geo_intelligence import (
    INITIAL_GEO_PROVIDERS,
    GeoProviderList,
    GeoProviderRead,
    GeoProviderSummary,
    GeoRecommendationSignal,
    GeoVisibilityFilters,
    GeoVisibilityHistory,
    GeoVisibilityHistoryPoint,
    GeoVisibilityImportRequest,
    GeoVisibilityImportResult,
    GeoVisibilitySnapshotList,
    GeoVisibilitySnapshotRead,
    GeoVisibilitySummary,
)
from backend.app.schemas.pagination import PaginationParams

Scope = tuple[int, str, str, str]
CampaignScope = tuple[int, str, str]


class GeoIntelligenceService:
    """Validate, persist, aggregate and compare GEO Intelligence snapshots."""

    def __init__(
        self,
        repository: GeoIntelligenceRepository,
        *,
        connectors: dict[str, GeoIntelligenceConnector] | None = None,
    ) -> None:
        self.repository = repository
        self.connectors = connectors or {
            provider: NotConfiguredGeoIntelligenceConnector(provider) for provider in INITIAL_GEO_PROVIDERS
        }

    def list_snapshots(
        self,
        params: PaginationParams,
        *,
        filters: GeoVisibilityFilters | None = None,
    ) -> GeoVisibilitySnapshotList:
        """Return filtered and paginated snapshots."""

        filters = self._validated_filters(filters or GeoVisibilityFilters())
        try:
            snapshots, total = self.repository.list_snapshots(params, filters=filters)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
        return GeoVisibilitySnapshotList(
            items=[self._read(item) for item in snapshots],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=self._filters_dict(filters),
        )

    def import_observations(self, payload: GeoVisibilityImportRequest) -> GeoVisibilityImportResult:
        """Persist a normalized batch once without executing an external connector."""

        website_ids = {item.website_id for item in payload.observations}
        missing = sorted(website_id for website_id in website_ids if self.repository.get_website(website_id) is None)
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website(s) introuvable(s): {', '.join(str(value) for value in missing)}.",
            )

        created: list[GeoVisibilitySnapshot] = []
        duplicates = 0
        try:
            for item in payload.observations:
                if self.repository.find_exact(item) is not None:
                    duplicates += 1
                    continue
                created.append(self.repository.add_pending(item))
            self.repository.commit()
        except IntegrityError as exc:
            self.repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Import GEO Intelligence concurrent. Reessayez.",
            ) from exc

        for snapshot in created:
            self.repository.refresh(snapshot)
        return GeoVisibilityImportResult(
            received=len(payload.observations),
            created=len(created),
            duplicates=duplicates,
            rejected=0,
            items=[self._read(item) for item in created],
        )

    def summary(
        self,
        *,
        filters: GeoVisibilityFilters | None = None,
        website_ids: list[int] | None = None,
    ) -> GeoVisibilitySummary:
        """Return explainable consolidated KPIs and provider comparisons."""

        filters = self._validated_filters(filters or GeoVisibilityFilters())
        snapshots = self.repository.all_snapshots(filters=filters, website_ids=website_ids)
        by_provider: dict[str, list[GeoVisibilitySnapshot]] = defaultdict(list)
        for snapshot in snapshots:
            by_provider[snapshot.provider].append(snapshot)
        provider_rows = [self._provider_summary(provider, rows) for provider, rows in sorted(by_provider.items())]
        return GeoVisibilitySummary(
            captures=len(snapshots),
            average_visibility_score=self._average_score(snapshots),
            providers_covered=sorted(by_provider),
            citation_count=sum(item.citation_count for item in snapshots),
            source_count=sum(item.source_count for item in snapshots),
            appearance_frequency=self._appearance_frequency(snapshots),
            latest_capture_at=max((item.captured_at for item in snapshots), default=None),
            by_provider=provider_rows,
            generated_at=datetime.now(UTC),
        )

    def history(
        self,
        *,
        filters: GeoVisibilityFilters | None = None,
        website_ids: list[int] | None = None,
        granularity: str = "day",
    ) -> GeoVisibilityHistory:
        """Return daily provider series for comparable temporal analysis."""

        filters = self._validated_filters(filters or GeoVisibilityFilters())
        snapshots = self.repository.all_snapshots(filters=filters, website_ids=website_ids)
        groups: dict[tuple[date, str], list[GeoVisibilitySnapshot]] = defaultdict(list)
        for snapshot in snapshots:
            groups[(self._bucket_date(snapshot.captured_at.date(), granularity), snapshot.provider)].append(snapshot)
        points = [
            GeoVisibilityHistoryPoint(
                date=day,
                provider=provider,
                captures=len(rows),
                average_visibility_score=self._average_score(rows) or 0.0,
                citation_count=sum(item.citation_count for item in rows),
                source_count=sum(item.source_count for item in rows),
                appearance_frequency=self._appearance_frequency(rows) or 0.0,
            )
            for (day, provider), rows in sorted(groups.items())
        ]
        return GeoVisibilityHistory(points=points, generated_at=datetime.now(UTC))

    def providers(self) -> GeoProviderList:
        """Return the open connector registry without contacting providers."""

        provider_ids = sorted(set(INITIAL_GEO_PROVIDERS) | set(self.connectors))
        return GeoProviderList(
            providers=[
                GeoProviderRead(
                    provider=provider,
                    configured=bool(getattr(self.connectors.get(provider), "configured", False)),
                )
                for provider in provider_ids
            ],
        )

    def recommendation_signals(self) -> list[GeoRecommendationSignal]:
        """Build deterministic domain signals without assigning transverse priorities."""

        snapshots = self.repository.all_snapshots(filters=GeoVisibilityFilters())
        scoped: dict[Scope, dict[date, list[GeoVisibilitySnapshot]]] = defaultdict(lambda: defaultdict(list))
        campaigns: dict[CampaignScope, dict[date, set[str]]] = defaultdict(lambda: defaultdict(set))
        for item in snapshots:
            scoped[(item.website_id, item.provider, item.prompt, item.entity)][item.captured_at.date()].append(item)
            campaigns[(item.website_id, item.prompt, item.entity)][item.captured_at.date()].add(item.provider)

        signals: list[GeoRecommendationSignal] = []
        for scope, periods in sorted(scoped.items()):
            website_id, provider, prompt, entity = scope
            days = sorted(periods)
            current = periods[days[-1]]
            previous = periods[days[-2]] if len(days) > 1 else []
            current_score = self._average_score(current) or 0.0
            scope_id = self._scope_id(scope)
            if current_score < 30:
                signals.append(
                    self._signal(
                        scope,
                        "low_visibility",
                        scope_id,
                        f"Faible visibilite sur {provider}",
                        f"Le score moyen de visibilite est de {current_score:.1f}/100.",
                        {"current_score": current_score, "period": days[-1].isoformat()},
                    ),
                )
            if previous:
                previous_score = self._average_score(previous) or 0.0
                decrease = previous_score - current_score
                if decrease >= 15:
                    signals.append(
                        self._signal(
                            scope,
                            "significant_decrease",
                            scope_id,
                            f"Baisse de visibilite sur {provider}",
                            f"Le score moyen a diminue de {decrease:.1f} points.",
                            {
                                "current_score": current_score,
                                "previous_score": previous_score,
                                "decrease_points": decrease,
                            },
                        ),
                    )
                previous_citations = sum(item.citation_count for item in previous)
                current_citations = sum(item.citation_count for item in current)
                if previous_citations >= 1:
                    citation_decrease = (previous_citations - current_citations) / previous_citations * 100
                    if citation_decrease >= 30:
                        signals.append(
                            self._signal(
                                scope,
                                "citation_loss",
                                scope_id,
                                f"Perte de citations sur {provider}",
                                f"Les citations ont diminue de {citation_decrease:.1f} %.",
                                {
                                    "current_citations": current_citations,
                                    "previous_citations": previous_citations,
                                    "decrease_percent": citation_decrease,
                                },
                            ),
                        )
            average_sources = fmean(item.source_count for item in current)
            if current_score > 0 and average_sources < 2:
                signals.append(
                    self._signal(
                        scope,
                        "insufficient_source_diversity",
                        scope_id,
                        f"Diversite de sources insuffisante sur {provider}",
                        f"La capture recente identifie en moyenne {average_sources:.1f} source(s).",
                        {"current_score": current_score, "average_source_count": average_sources},
                    ),
                )

        for campaign, periods in sorted(campaigns.items()):
            website_id, prompt, entity = campaign
            current_day = max(periods)
            expected = set().union(*periods.values())
            missing = expected - periods[current_day]
            for provider in sorted(missing):
                scope = (website_id, provider, prompt, entity)
                signals.append(
                    self._signal(
                        scope,
                        "provider_absence",
                        self._scope_id(scope),
                        f"Absence de visibilite sur {provider}",
                        "Aucune capture exploitable n'existe pour la derniere periode configuree.",
                        {"period": current_day.isoformat(), "expected_provider": provider},
                    ),
                )
        return signals

    def _provider_summary(
        self,
        provider: str,
        snapshots: list[GeoVisibilitySnapshot],
    ) -> GeoProviderSummary:
        return GeoProviderSummary(
            provider=provider,
            captures=len(snapshots),
            average_visibility_score=self._average_score(snapshots),
            citation_count=sum(item.citation_count for item in snapshots),
            source_count=sum(item.source_count for item in snapshots),
            appearance_frequency=self._appearance_frequency(snapshots),
            latest_capture_at=max((item.captured_at for item in snapshots), default=None),
        )

    def _signal(
        self,
        scope: Scope,
        rule_code: str,
        source_object_id: str,
        title: str,
        description: str,
        factors: dict[str, Any],
    ) -> GeoRecommendationSignal:
        website_id, provider, prompt, entity = scope
        return GeoRecommendationSignal(
            website_id=website_id,
            provider=provider,
            prompt=prompt,
            entity=entity,
            rule_code=rule_code,
            source_object_id=f"{rule_code}:{source_object_id}",
            title=title,
            description=description,
            factors=factors,
        )

    def _read(self, snapshot: GeoVisibilitySnapshot) -> GeoVisibilitySnapshotRead:
        website_name = snapshot.website.name if snapshot.website is not None else None
        return GeoVisibilitySnapshotRead.model_validate(snapshot).model_copy(update={"website_name": website_name})

    def _validated_filters(self, filters: GeoVisibilityFilters) -> GeoVisibilityFilters:
        if filters.date_from and filters.date_to and filters.date_from > filters.date_to:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="date_from doit preceder ou etre egale a date_to.",
            )
        return filters

    def _filters_dict(self, filters: GeoVisibilityFilters) -> dict[str, Any]:
        return {key: value for key, value in filters.model_dump(mode="json").items() if value is not None}

    @staticmethod
    def _average_score(snapshots: list[GeoVisibilitySnapshot]) -> float | None:
        return round(fmean(item.visibility_score for item in snapshots), 2) if snapshots else None

    @staticmethod
    def _appearance_frequency(snapshots: list[GeoVisibilitySnapshot]) -> float | None:
        if not snapshots:
            return None
        visible = sum(1 for item in snapshots if item.visibility_score > 0)
        return round(visible / len(snapshots) * 100, 2)

    @staticmethod
    def _scope_id(scope: Scope) -> str:
        return sha256("|".join(str(value) for value in scope).encode()).hexdigest()[:24]

    @staticmethod
    def _bucket_date(value: date, granularity: str) -> date:
        if granularity == "week":
            return value - timedelta(days=value.weekday())
        if granularity == "month":
            return value.replace(day=1)
        if granularity != "day":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Granularite GEO Intelligence non autorisee: {granularity}.",
            )
        return value
