"""Tests for Dashboard V2 routes."""

from datetime import date, datetime

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import dashboard_v2


def _overview_payload() -> dict[str, object]:
    return {
        "generated_at": datetime(2026, 7, 10).isoformat(),
        "filters": {},
        "period": {
            "date_from": date(2026, 6, 11).isoformat(),
            "date_to": date(2026, 7, 10).isoformat(),
            "period": "30d",
        },
        "previous_period": None,
        "sources": [],
        "global_health": {
            "score": 80,
            "status": "good",
            "components": [],
            "available_components": [],
            "missing_components": [],
        },
        "seo": {},
        "geo": {},
        "gsc": {},
        "ga4": {},
        "bing": {},
        "technical": {"name": "technical", "score": 80, "status": "good", "available": True},
        "operations": {},
        "monitoring": {},
        "alerts": {},
        "workers": {},
        "top_websites": [],
        "top_recommendations": [],
        "partial_data": [],
    }


def _trends_payload() -> dict[str, object]:
    return {"generated_at": datetime(2026, 7, 10).isoformat(), "filters": {}, "granularity": "day", "series": []}


def _paginated_payload() -> dict[str, object]:
    return {"items": [], "total": 0, "page": 1, "page_size": 20, "pages": 0, "filters": {}}


class FakeDashboardV2Service:
    """Route service stub."""

    def overview(self, _filters: object) -> dict[str, object]:
        return _overview_payload()

    def trends(self, **_kwargs: object) -> dict[str, object]:
        return _trends_payload()

    def websites(self, *_args: object, **_kwargs: object) -> dict[str, object]:
        return _paginated_payload()

    def recommendations(self, *_args: object, **_kwargs: object) -> dict[str, object]:
        return _paginated_payload()


def test_dashboard_v2_overview_rejects_anonymous_user(client: TestClient) -> None:
    """Dashboard V2 requires authentication."""

    response = client.get("/api/v1/dashboard-v2/overview")

    assert response.status_code == 401


def test_dashboard_v2_overview_requires_read_permission(client: TestClient, auth_headers_for) -> None:
    """Dashboard V2 requires crawl read permission."""

    response = client.get("/api/v1/dashboard-v2/overview", headers=auth_headers_for(permission_codes=[]))

    assert response.status_code == 403


def test_dashboard_v2_endpoints_allow_user_with_read_permission(client: TestClient, auth_headers_for) -> None:
    """Dashboard V2 endpoints allow users with crawl read permission."""

    client.app.dependency_overrides[dashboard_v2.get_service] = lambda: FakeDashboardV2Service()
    headers = auth_headers_for(permission_codes=["crawl.read"])
    try:
        overview = client.get("/api/v1/dashboard-v2/overview", headers=headers)
        trends = client.get("/api/v1/dashboard-v2/trends", headers=headers)
        websites = client.get("/api/v1/dashboard-v2/websites", headers=headers)
        recommendations = client.get("/api/v1/dashboard-v2/recommendations", headers=headers)
    finally:
        client.app.dependency_overrides.pop(dashboard_v2.get_service, None)

    assert overview.status_code == 200
    assert trends.status_code == 200
    assert websites.status_code == 200
    assert recommendations.status_code == 200


def test_dashboard_v2_trends_rejects_unknown_metric(client: TestClient, auth_headers_for) -> None:
    """Trend metrics are whitelisted by the route schema."""

    headers = auth_headers_for(permission_codes=["crawl.read"])

    response = client.get("/api/v1/dashboard-v2/trends?metrics=unknown", headers=headers)

    assert response.status_code == 422
