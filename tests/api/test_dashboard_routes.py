"""Tests for Dashboard routes."""

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import dashboard


def _overview_payload() -> dict[str, object]:
    return {
        "crawl": {
            "crawled_pages_count": 2,
            "failed_pages_count": 0,
            "latest_crawl_status": "COMPLETED",
            "latest_crawl_date": None,
        },
        "seo": {
            "average_score": 75,
            "best_page": None,
            "worst_page": None,
            "analyzed_pages_count": 2,
            "critical_errors_count": 1,
            "warnings_count": 0,
            "information_count": 0,
            "top_issues": [],
        },
        "geo": {
            "average_score": 70,
            "best_page": None,
            "worst_page": None,
            "analyses_count": 1,
            "top_recommendations": [],
        },
        "priority_pages": [],
        "comparison": {
            "average_seo_score": 75,
            "average_geo_score": 70,
            "average_gap": 5,
            "pages": [],
        },
        "seo_score_distribution": [
            {"label": "Faible", "min_score": 0, "max_score": 49, "count": 0},
            {"label": "Moyen", "min_score": 50, "max_score": 74, "count": 1},
            {"label": "Bon", "min_score": 75, "max_score": 89, "count": 1},
            {"label": "Excellent", "min_score": 90, "max_score": 100, "count": 0},
        ],
        "geo_score_distribution": [
            {"label": "Faible", "min_score": 0, "max_score": 49, "count": 0},
            {"label": "Moyen", "min_score": 50, "max_score": 74, "count": 1},
            {"label": "Bon", "min_score": 75, "max_score": 89, "count": 0},
            {"label": "Excellent", "min_score": 90, "max_score": 100, "count": 0},
        ],
        "future_sources": {
            "google_search_console": {"available": False, "status": "planned"},
            "google_analytics_4": {"available": False, "status": "planned"},
            "reports": {"available": False, "status": "planned"},
        },
    }


class FakeDashboardService:
    """Route service stub."""

    def overview(self, **kwargs: object) -> dict[str, object]:
        return _overview_payload()


def test_dashboard_route_rejects_anonymous_user(client: TestClient) -> None:
    """Dashboard overview requires a JWT."""

    response = client.get("/api/v1/dashboard/overview")

    assert response.status_code == 401


def test_dashboard_route_allows_user_with_read_permission(client: TestClient, auth_headers_for) -> None:
    """Dashboard overview allows users with crawl read permission."""

    client.app.dependency_overrides[dashboard.get_service] = lambda: FakeDashboardService()
    headers = auth_headers_for(permission_codes=["crawl.read"])
    try:
        response = client.get("/api/v1/dashboard/overview", headers=headers)
    finally:
        client.app.dependency_overrides.pop(dashboard.get_service, None)

    assert response.status_code == 200
    assert response.json()["crawl"]["crawled_pages_count"] == 2
