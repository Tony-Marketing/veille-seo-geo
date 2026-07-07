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

    def list_imports(self, params: object, *, property_id: int | None = None) -> dict[str, object]:
        return {"items": [_import_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

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
        client.get("/api/v1/google-analytics/imports"),
        client.get("/api/v1/google-analytics/imports/1"),
        client.post("/api/v1/google-analytics/oauth/connect", json={}),
        client.post("/api/v1/google-analytics/oauth/refresh", json={}),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401, 401, 401, 401, 401]


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
        assert client.get("/api/v1/google-analytics/imports", headers=headers).status_code == 200
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
