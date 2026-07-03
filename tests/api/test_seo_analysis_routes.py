"""Tests for SEO analysis routes."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import seo_analysis


def _analysis_payload(analysis_id: int = 1, status: str = "PENDING") -> dict[str, object]:
    now = datetime.now(UTC).isoformat()
    return {
        "id": analysis_id,
        "crawl_session_id": 1,
        "status": status,
        "progress_percent": 0,
        "global_score": None,
        "pages_total": 0,
        "pages_analyzed": 0,
        "issues_total": 0,
        "error_message": None,
        "started_at": None,
        "completed_at": None,
        "created_at": now,
        "updated_at": now,
    }


class FakeSeoAnalysisService:
    """Route service stub."""

    def list(self, params: object) -> dict[str, object]:
        return {"items": [_analysis_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def create(self, payload: object) -> dict[str, object]:
        return _analysis_payload()

    def get(self, analysis_id: int) -> dict[str, object]:
        return _analysis_payload(analysis_id)

    def delete(self, analysis_id: int) -> None:
        return None


def test_seo_analysis_routes_reject_anonymous_user(client: TestClient) -> None:
    """SEO Analysis routes require a JWT."""

    responses = [
        client.get("/api/v1/seo-analysis"),
        client.post("/api/v1/seo-analysis", json={"crawl_id": 1}),
        client.get("/api/v1/seo-analysis/1"),
        client.delete("/api/v1/seo-analysis/1"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401]


def test_seo_analysis_routes_allow_user_with_permissions(
    client: TestClient,
    auth_headers_for,
) -> None:
    """SEO Analysis routes allow users with crawl read and write permissions."""

    client.app.dependency_overrides[seo_analysis.get_service] = lambda: FakeSeoAnalysisService()
    headers = auth_headers_for(permission_codes=["crawl.read", "crawl.write"])
    try:
        assert client.get("/api/v1/seo-analysis", headers=headers).status_code == 200
        create_response = client.post("/api/v1/seo-analysis", headers=headers, json={"crawl_id": 1})
        assert create_response.status_code == 201
        assert client.get("/api/v1/seo-analysis/1", headers=headers).status_code == 200
        assert client.delete("/api/v1/seo-analysis/1", headers=headers).status_code == 204
    finally:
        client.app.dependency_overrides.pop(seo_analysis.get_service, None)

