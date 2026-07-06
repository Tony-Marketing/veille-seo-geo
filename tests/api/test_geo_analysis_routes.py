"""Tests for GEO analysis routes."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import geo_analysis


def _analysis_payload(analysis_id: int = 1, status: str = "PENDING") -> dict[str, object]:
    now = datetime.now(UTC).isoformat()
    return {
        "id": analysis_id,
        "seo_analysis_id": 1,
        "crawl_session_id": 1,
        "status": status,
        "progress_percent": 0,
        "geo_score": None,
        "llm_score": None,
        "global_score": None,
        "providers_requested": ["openai"],
        "pages_total": 0,
        "pages_analyzed": 0,
        "provider_results_count": 0,
        "recommendations_count": 0,
        "summary": None,
        "error_message": None,
        "started_at": None,
        "completed_at": None,
        "provider_results": [],
        "recommendations": [],
        "created_at": now,
        "updated_at": now,
    }


class FakeGeoAnalysisService:
    """Route service stub."""

    def list(self, params: object) -> dict[str, object]:
        return {"items": [_analysis_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def create(self, payload: object) -> dict[str, object]:
        return _analysis_payload()

    def get(self, analysis_id: int) -> dict[str, object]:
        return _analysis_payload(analysis_id)

    def run(self, analysis_id: int) -> dict[str, object]:
        return _analysis_payload(analysis_id, "PARTIAL")

    def delete(self, analysis_id: int) -> None:
        return None


def test_geo_analysis_routes_reject_anonymous_user(client: TestClient) -> None:
    """GEO Analysis routes require a JWT."""

    responses = [
        client.get("/api/v1/geo-analysis"),
        client.post("/api/v1/geo-analysis", json={"seo_analysis_id": 1, "providers": ["openai"]}),
        client.get("/api/v1/geo-analysis/1"),
        client.post("/api/v1/geo-analysis/1/run"),
        client.delete("/api/v1/geo-analysis/1"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401]


def test_geo_analysis_routes_allow_user_with_permissions(
    client: TestClient,
    auth_headers_for,
) -> None:
    """GEO Analysis routes allow users with crawl read and write permissions."""

    client.app.dependency_overrides[geo_analysis.get_service] = lambda: FakeGeoAnalysisService()
    headers = auth_headers_for(permission_codes=["crawl.read", "crawl.write"])
    try:
        assert client.get("/api/v1/geo-analysis", headers=headers).status_code == 200
        create_response = client.post(
            "/api/v1/geo-analysis",
            headers=headers,
            json={"seo_analysis_id": 1, "providers": ["openai"]},
        )
        assert create_response.status_code == 201
        assert client.get("/api/v1/geo-analysis/1", headers=headers).status_code == 200
        assert client.post("/api/v1/geo-analysis/1/run", headers=headers).status_code == 200
        assert client.delete("/api/v1/geo-analysis/1", headers=headers).status_code == 204
    finally:
        client.app.dependency_overrides.pop(geo_analysis.get_service, None)
