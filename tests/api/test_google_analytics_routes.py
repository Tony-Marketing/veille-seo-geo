"""Tests for Google Analytics routes."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import google_analytics


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _property_payload(property_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": property_id,
        "website_id": None,
        "property_id": "properties/123",
        "property_name": "Example GA4",
        "account_name": "Example Account",
        "measurement_id": "G-TEST123",
        "token_expires_at": None,
        "enabled": True,
        "created_at": now,
        "updated_at": now,
    }


def _import_payload(import_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": import_id,
        "property_id": 1,
        "started_at": now,
        "finished_at": now,
        "status": "COMPLETED",
        "imported_rows": 1,
        "error_message": None,
        "duration_seconds": 0.1,
        "created_at": now,
        "updated_at": now,
    }


def _metric_payload(metric_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": metric_id,
        "property_id": 1,
        "import_id": 1,
        "date": "2026-07-01",
        "source": "google",
        "medium": "organic",
        "campaign": "brand",
        "device_category": "desktop",
        "country": "France",
        "users": 10,
        "new_users": 4,
        "sessions": 12,
        "engaged_sessions": 9,
        "screen_page_views": 30,
        "average_session_duration": 42.5,
        "engagement_rate": 0.75,
        "conversions": 2.0,
        "total_revenue": 120.0,
        "created_at": now,
        "updated_at": now,
    }


def _kpis_payload() -> dict[str, object]:
    return {
        "rows": 1,
        "sessions": 12,
        "users": 10,
        "new_users": 4,
        "engaged_sessions": 9,
        "screen_page_views": 30,
        "average_session_duration": 42.5,
        "engagement_rate": 0.75,
        "conversions": 2.0,
        "total_revenue": 120.0,
    }


def _breakdown_payload(dimension: str = "source") -> dict[str, object]:
    return {
        "generated_at": _now(),
        "filters": {"property_id": 1},
        "dimension": dimension,
        "data": [{"dimension": "google", **_kpis_payload()}],
    }


class FakeGoogleAnalyticsService:
    """Route service stub."""

    def list_properties(self, params: object) -> dict[str, object]:
        return {"items": [_property_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def create_property(self, payload: object) -> dict[str, object]:
        return _property_payload()

    def update_property(self, property_id: int, payload: object) -> dict[str, object]:
        return _property_payload(property_id)

    def delete_property(self, property_id: int) -> None:
        return None

    def run_manual_import(self, payload: object) -> dict[str, object]:
        return _import_payload()

    def list_metrics(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_metric_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def overview(self, filters: object | None = None) -> dict[str, object]:
        return {"generated_at": _now(), "filters": {}, "data": _kpis_payload()}

    def traffic(self, filters: object | None = None) -> dict[str, object]:
        return _breakdown_payload("source")

    def acquisition(self, filters: object | None = None) -> dict[str, object]:
        return _breakdown_payload("medium")

    def engagement(self, filters: object | None = None) -> dict[str, object]:
        return _breakdown_payload("device_category")

    def conversions(self, filters: object | None = None) -> dict[str, object]:
        return _breakdown_payload("source")

    def revenue(self, filters: object | None = None) -> dict[str, object]:
        return _breakdown_payload("campaign")

    def list_imports(
        self,
        params: object,
        *,
        property_id: int | None = None,
        filters: object | None = None,
    ) -> dict[str, object]:
        return {"items": [_import_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def history(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        item = _import_payload()
        item["property_name"] = "Example GA4"
        item["google_property_id"] = "properties/123"
        return {"items": [item], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def get_import(self, import_id: int) -> dict[str, object]:
        return _import_payload(import_id)

    def connect_oauth(self, payload: object) -> dict[str, object]:
        return {"property_id": 1, "token_scopes": [], "token_expires_at": None, "status": "CONNECTED"}

    def refresh_oauth(self, payload: object) -> dict[str, object]:
        return {"property_id": 1, "token_scopes": [], "token_expires_at": None, "status": "REFRESHED"}


def test_google_analytics_routes_reject_anonymous_user(client: TestClient) -> None:
    """Google Analytics routes require a JWT."""

    responses = [
        client.get("/api/v1/google-analytics/properties"),
        client.post("/api/v1/google-analytics/properties", json={}),
        client.put("/api/v1/google-analytics/properties/1", json={}),
        client.delete("/api/v1/google-analytics/properties/1"),
        client.post("/api/v1/google-analytics/import", json={}),
        client.get("/api/v1/google-analytics/metrics"),
        client.get("/api/v1/google-analytics/overview"),
        client.get("/api/v1/google-analytics/traffic"),
        client.get("/api/v1/google-analytics/acquisition"),
        client.get("/api/v1/google-analytics/engagement"),
        client.get("/api/v1/google-analytics/conversions"),
        client.get("/api/v1/google-analytics/revenue"),
        client.get("/api/v1/google-analytics/imports"),
        client.get("/api/v1/google-analytics/history"),
        client.get("/api/v1/google-analytics/imports/1"),
        client.post("/api/v1/google-analytics/oauth/connect", json={}),
        client.post("/api/v1/google-analytics/oauth/refresh", json={}),
    ]

    assert [response.status_code for response in responses] == [
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        401,
    ]


def test_google_analytics_routes_allow_user_with_permissions(client: TestClient, auth_headers_for) -> None:
    """Google Analytics routes allow users with crawl read and write permissions."""

    client.app.dependency_overrides[google_analytics.get_service] = lambda: FakeGoogleAnalyticsService()
    headers = auth_headers_for(permission_codes=["crawl.read", "crawl.write"])
    try:
        assert client.get("/api/v1/google-analytics/properties", headers=headers).status_code == 200
        create_response = client.post(
            "/api/v1/google-analytics/properties",
            headers=headers,
            json={"property_id": "properties/123", "property_name": "Example GA4"},
        )
        assert create_response.status_code == 201
        assert client.put("/api/v1/google-analytics/properties/1", headers=headers, json={}).status_code == 200
        assert client.delete("/api/v1/google-analytics/properties/1", headers=headers).status_code == 204
        import_response = client.post(
            "/api/v1/google-analytics/import",
            headers=headers,
            json={"property_id": 1, "start_date": "2026-07-01", "end_date": "2026-07-07"},
        )
        assert import_response.status_code == 200
        assert client.get("/api/v1/google-analytics/metrics", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/overview", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/traffic", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/acquisition", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/engagement", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/conversions", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/revenue", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/imports", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/history", headers=headers).status_code == 200
        assert client.get("/api/v1/google-analytics/imports/1", headers=headers).status_code == 200
        connect_response = client.post(
            "/api/v1/google-analytics/oauth/connect",
            headers=headers,
            json={"property_id": 1, "access_token": "access-token", "refresh_token": "refresh-token"},
        )
        assert connect_response.status_code == 200
        refresh_response = client.post(
            "/api/v1/google-analytics/oauth/refresh",
            headers=headers,
            json={"property_id": 1},
        )
        assert refresh_response.status_code == 200
    finally:
        client.app.dependency_overrides.pop(google_analytics.get_service, None)
