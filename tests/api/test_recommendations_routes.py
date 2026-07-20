"""Tests for recommendation REST routes and permissions."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models import Recommendation


def _recommendation(db_session: Session) -> Recommendation:
    item = Recommendation(
        source="SEO",
        source_id="1",
        category="metadata",
        title="Corriger le Title",
        description="Ajouter un Title explicite.",
        priority="HIGH",
        impact="SEO",
        score=80.0,
        status="OPEN",
        deduplication_key="global|SEO|title_missing|seo_analysis_issue|1",
        metadata_={"rule_code": "title_missing"},
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


def test_recommendation_routes_require_permissions(client: TestClient, auth_headers_for) -> None:
    """Read and write operations require their dedicated permissions."""

    no_permission = auth_headers_for(permission_codes=[])
    read_only = auth_headers_for(permission_codes=["recommendation.read"])

    assert client.get("/api/v1/recommendations", headers=no_permission).status_code == 403
    response = client.patch(
        "/api/v1/recommendations/1/status",
        json={"status": "RESOLVED"},
        headers=read_only,
    )
    assert response.status_code == 403


def test_recommendation_routes_list_summary_detail_and_status(
    client: TestClient,
    db_session: Session,
    auth_headers_for,
) -> None:
    """The complete REST contract is filtered, paginated and lifecycle-aware."""

    item = _recommendation(db_session)
    headers = auth_headers_for(permission_codes=["recommendation.read", "recommendation.write"])

    listing = client.get("/api/v1/recommendations?priority=HIGH&page=1&page_size=10", headers=headers)
    summary = client.get("/api/v1/recommendations/summary", headers=headers)
    detail = client.get(f"/api/v1/recommendations/{item.id}", headers=headers)
    updated = client.patch(
        f"/api/v1/recommendations/{item.id}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=headers,
    )

    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert summary.status_code == 200
    assert summary.json()["open"] == 1
    assert detail.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["status"] == "ACKNOWLEDGED"
