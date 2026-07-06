"""Tests for Google Search Console routes."""

from datetime import UTC, date, datetime

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import gsc


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _property_payload() -> dict[str, object]:
    now = _timestamp()
    return {
        "id": 1,
        "website_id": None,
        "site_url": "https://example.com/",
        "property_type": "url_prefix",
        "permission_level": "siteOwner",
        "is_verified": True,
        "last_synced_at": None,
        "created_at": now,
        "updated_at": now,
    }


def _import_payload() -> dict[str, object]:
    now = _timestamp()
    return {
        "id": 1,
        "property_id": 1,
        "status": "COMPLETED",
        "import_type": "full",
        "date_start": "2026-07-01",
        "date_end": "2026-07-02",
        "rows_imported": 1,
        "error_message": None,
        "started_at": now,
        "completed_at": now,
        "created_at": now,
        "updated_at": now,
    }


class FakeGscService:
    """Route service stub."""

    def list_properties(self, params: object) -> dict[str, object]:
        return {"items": [_property_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def sync_properties(self) -> dict[str, object]:
        return {"items": [_property_payload()], "total": 1, "page": 1, "page_size": 1, "pages": 1}

    def get_property(self, property_id: int) -> dict[str, object]:
        return _property_payload()

    def list_performance(self, property_id: int, params: object, **kwargs: object) -> dict[str, object]:
        now = _timestamp()
        return {
            "items": [
                {
                    "id": 1,
                    "property_id": property_id,
                    "import_run_id": 1,
                    "date": "2026-07-01",
                    "page": "https://example.com/",
                    "query": "example",
                    "device": "DESKTOP",
                    "country": "FRA",
                    "search_type": "web",
                    "clicks": 10,
                    "impressions": 100,
                    "ctr": 0.1,
                    "position": 2.5,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }

    def list_coverage(self, property_id: int, params: object) -> dict[str, object]:
        now = _timestamp()
        return {
            "items": [
                {
                    "id": 1,
                    "property_id": property_id,
                    "import_run_id": 1,
                    "date": "2026-07-01",
                    "category": "indexed",
                    "state": "valid",
                    "pages_count": 12,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }

    def list_indexing(self, property_id: int, params: object) -> dict[str, object]:
        now = _timestamp()
        return {
            "items": [
                {
                    "id": 1,
                    "property_id": property_id,
                    "import_run_id": 1,
                    "inspected_url": "https://example.com/",
                    "coverage_state": "Indexed",
                    "indexing_state": "INDEXING_ALLOWED",
                    "verdict": "PASS",
                    "robots_txt_state": None,
                    "page_fetch_state": None,
                    "google_canonical": None,
                    "user_canonical": None,
                    "last_crawl_time": None,
                    "inspected_at": now,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }

    def list_sitemaps(self, property_id: int, params: object) -> dict[str, object]:
        now = _timestamp()
        return {
            "items": [
                {
                    "id": 1,
                    "property_id": property_id,
                    "import_run_id": 1,
                    "sitemap_url": "https://example.com/sitemap.xml",
                    "path": None,
                    "last_submitted": None,
                    "last_downloaded": None,
                    "is_pending": False,
                    "is_sitemaps_index": False,
                    "sitemap_type": None,
                    "errors": 0,
                    "warnings": 0,
                    "contents": None,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }

    def run_import(self, payload: object) -> dict[str, object]:
        return _import_payload()

    def list_import_runs(self, params: object) -> dict[str, object]:
        return {"items": [_import_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def get_import_run(self, import_run_id: int) -> dict[str, object]:
        return _import_payload()

    def oauth_status(self) -> dict[str, object]:
        return {"configured": False, "active_credentials_count": 0, "latest_credential": None}

    def authorization_url(self) -> dict[str, object]:
        return {"authorization_url": "https://accounts.google.com/mock", "scopes": ["scope"], "configured": False}

    def oauth_callback(self, payload: object, user_id: int | None = None) -> dict[str, object]:
        now = _timestamp()
        return {
            "id": 1,
            "provider": "google",
            "scopes": ["scope"],
            "token_expires_at": now,
            "status": "ACTIVE",
            "error_message": None,
            "created_by_id": user_id,
            "updated_by_id": user_id,
            "created_at": now,
            "updated_at": now,
        }

    def delete_credential(self, credential_id: int) -> None:
        return None


def test_gsc_routes_reject_anonymous_user(client: TestClient) -> None:
    """GSC routes require a JWT."""

    responses = [
        client.get("/api/v1/gsc/properties"),
        client.post("/api/v1/gsc/properties/sync"),
        client.get("/api/v1/gsc/oauth/status"),
        client.post("/api/v1/gsc/import-runs", json={"property_id": 1}),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401]


def test_gsc_routes_allow_user_with_permissions(client: TestClient, auth_headers_for) -> None:
    """GSC routes delegate to the service for authorized users."""

    client.app.dependency_overrides[gsc.get_service] = lambda: FakeGscService()
    headers = auth_headers_for(permission_codes=["gsc.read", "gsc.write"])
    try:
        assert client.get("/api/v1/gsc/properties", headers=headers).status_code == 200
        assert client.post("/api/v1/gsc/properties/sync", headers=headers).status_code == 200
        assert client.get("/api/v1/gsc/properties/1", headers=headers).status_code == 200
        assert client.get("/api/v1/gsc/properties/1/performance", headers=headers).status_code == 200
        assert client.get("/api/v1/gsc/properties/1/coverage", headers=headers).status_code == 200
        assert client.get("/api/v1/gsc/properties/1/indexing", headers=headers).status_code == 200
        assert client.get("/api/v1/gsc/properties/1/sitemaps", headers=headers).status_code == 200
        assert client.post("/api/v1/gsc/import-runs", headers=headers, json={"property_id": 1}).status_code == 201
        assert client.get("/api/v1/gsc/import-runs", headers=headers).status_code == 200
        assert client.get("/api/v1/gsc/import-runs/1", headers=headers).status_code == 200
        assert client.get("/api/v1/gsc/oauth/status", headers=headers).status_code == 200
        assert client.get("/api/v1/gsc/oauth/authorization-url", headers=headers).status_code == 200
        callback_response = client.post("/api/v1/gsc/oauth/callback", headers=headers, json={"code": "abc"})
        assert callback_response.status_code == 201
        assert client.delete("/api/v1/gsc/oauth/credentials/1", headers=headers).status_code == 204
    finally:
        client.app.dependency_overrides.pop(gsc.get_service, None)


def test_gsc_performance_route_accepts_date_filters(client: TestClient, auth_headers_for) -> None:
    """Performance endpoint accepts date range filters."""

    client.app.dependency_overrides[gsc.get_service] = lambda: FakeGscService()
    headers = auth_headers_for(permission_codes=["gsc.read"])
    try:
        response = client.get(
            "/api/v1/gsc/properties/1/performance",
            headers=headers,
            params={"date_start": date(2026, 7, 1).isoformat(), "date_end": date(2026, 7, 2).isoformat()},
        )
    finally:
        client.app.dependency_overrides.pop(gsc.get_service, None)

    assert response.status_code == 200
    assert response.json()["items"][0]["clicks"] == 10
