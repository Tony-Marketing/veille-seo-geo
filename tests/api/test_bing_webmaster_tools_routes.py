"""Tests for Bing Webmaster Tools routes."""

from datetime import UTC, date, datetime

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import bing_webmaster_tools


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _connection_payload(connection_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": connection_id,
        "website_id": None,
        "auth_type": "API_KEY",
        "client_id": "client-id",
        "token_expires_at": None,
        "scopes": [],
        "is_active": True,
        "last_sync_at": None,
        "last_error": None,
        "has_client_secret": False,
        "has_access_token": False,
        "has_refresh_token": False,
        "has_api_key": True,
        "created_at": now,
        "updated_at": now,
    }


def _site_payload(site_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": site_id,
        "connection_id": 1,
        "website_id": None,
        "site_url": "https://example.com/",
        "is_verified": True,
        "is_active": True,
        "last_import_at": None,
        "created_at": now,
        "updated_at": now,
    }


def _metric_payload(metric_id: int = 1) -> dict[str, object]:
    return {
        "id": metric_id,
        "bing_site_id": 1,
        "import_id": 1,
        "date": date(2026, 7, 1).isoformat(),
        "query": "audit seo",
        "page_url": "https://example.com/audit",
        "country": "FRA",
        "device": "DESKTOP",
        "clicks": 10,
        "impressions": 100,
        "ctr": 0.1,
        "average_position": 2.5,
        "created_at": _now(),
    }


def _crawl_stat_payload(crawl_stat_id: int = 1) -> dict[str, object]:
    return {
        "id": crawl_stat_id,
        "bing_site_id": 1,
        "import_id": 1,
        "date": date(2026, 7, 1).isoformat(),
        "url": "https://example.com/missing",
        "http_status": 404,
        "issue_type": "NOT_FOUND",
        "issue_category": "CRAWL",
        "severity": "ERROR",
        "details": None,
        "created_at": _now(),
    }


def _sitemap_payload(sitemap_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": sitemap_id,
        "bing_site_id": 1,
        "import_id": 1,
        "sitemap_url": "https://example.com/sitemap.xml",
        "status": "OK",
        "submitted_at": None,
        "last_crawled_at": None,
        "url_count": 42,
        "error_count": 0,
        "warning_count": 1,
        "created_at": now,
        "updated_at": now,
    }


def _import_run_payload(import_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": import_id,
        "connection_id": 1,
        "bing_site_id": 1,
        "import_type": "MANUAL",
        "status": "COMPLETED",
        "started_at": now,
        "finished_at": now,
        "items_processed": 3,
        "error_message": None,
        "created_at": now,
        "duration_seconds": 0.1,
    }


class FakeBingWebmasterToolsService:
    """Route service stub."""

    def list_connections(self, params: object) -> dict[str, object]:
        return {"items": [_connection_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def create_connection(self, payload: object) -> dict[str, object]:
        return _connection_payload()

    def get_connection(self, connection_id: int) -> dict[str, object]:
        return _connection_payload(connection_id)

    def update_connection(self, connection_id: int, payload: object) -> dict[str, object]:
        return _connection_payload(connection_id)

    def delete_connection(self, connection_id: int) -> None:
        return None

    def list_sites(
        self,
        params: object,
        *,
        connection_id: int | None = None,
        website_id: int | None = None,
        is_active: bool | None = None,
    ) -> dict[str, object]:
        return {"items": [_site_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def get_site(self, bing_site_id: int) -> dict[str, object]:
        return _site_payload(bing_site_id)

    def run_manual_import(self, payload: object) -> dict[str, object]:
        return _import_run_payload()

    def list_metrics(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_metric_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def list_crawl_stats(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_crawl_stat_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def list_sitemaps(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_sitemap_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}

    def list_import_runs(self, params: object, *, filters: object | None = None) -> dict[str, object]:
        return {"items": [_import_run_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1, "filters": {}}


def test_bing_webmaster_routes_reject_anonymous_user(client: TestClient) -> None:
    """Bing Webmaster Tools routes require a JWT."""

    responses = [
        client.get("/api/v1/bing-webmaster-tools/connections"),
        client.post("/api/v1/bing-webmaster-tools/connections", json={}),
        client.get("/api/v1/bing-webmaster-tools/connections/1"),
        client.patch("/api/v1/bing-webmaster-tools/connections/1", json={}),
        client.delete("/api/v1/bing-webmaster-tools/connections/1"),
        client.get("/api/v1/bing-webmaster-tools/sites"),
        client.get("/api/v1/bing-webmaster-tools/sites/1"),
        client.post("/api/v1/bing-webmaster-tools/import", json={}),
        client.get("/api/v1/bing-webmaster-tools/metrics"),
        client.get("/api/v1/bing-webmaster-tools/crawl-stats"),
        client.get("/api/v1/bing-webmaster-tools/sitemaps"),
        client.get("/api/v1/bing-webmaster-tools/import-runs"),
    ]

    assert [response.status_code for response in responses] == [401] * 12


def test_bing_webmaster_routes_reject_user_without_permission(client: TestClient, auth_headers_for) -> None:
    """Bing Webmaster Tools routes reject authenticated users without crawl permissions."""

    headers = auth_headers_for()

    assert client.get("/api/v1/bing-webmaster-tools/connections", headers=headers).status_code == 403
    assert client.post("/api/v1/bing-webmaster-tools/connections", headers=headers, json={}).status_code == 403


def test_bing_webmaster_routes_allow_user_with_permissions(client: TestClient, auth_headers_for) -> None:
    """Bing Webmaster Tools routes allow users with crawl read and write permissions."""

    client.app.dependency_overrides[bing_webmaster_tools.get_service] = lambda: FakeBingWebmasterToolsService()
    headers = auth_headers_for(permission_codes=["crawl.read", "crawl.write"])
    try:
        assert client.get("/api/v1/bing-webmaster-tools/connections", headers=headers).status_code == 200
        create_response = client.post(
            "/api/v1/bing-webmaster-tools/connections",
            headers=headers,
            json={"auth_type": "API_KEY", "api_key": "fake-api-key"},
        )
        assert create_response.status_code == 201
        assert "api_key_encrypted" not in create_response.json()
        assert client.get("/api/v1/bing-webmaster-tools/connections/1", headers=headers).status_code == 200
        assert client.patch("/api/v1/bing-webmaster-tools/connections/1", headers=headers, json={}).status_code == 200
        assert client.delete("/api/v1/bing-webmaster-tools/connections/1", headers=headers).status_code == 204
        assert client.get("/api/v1/bing-webmaster-tools/sites", headers=headers).status_code == 200
        assert client.get("/api/v1/bing-webmaster-tools/sites/1", headers=headers).status_code == 200
        import_response = client.post(
            "/api/v1/bing-webmaster-tools/import",
            headers=headers,
            json={"connection_id": 1, "date_from": "2026-07-01", "date_to": "2026-07-07"},
        )
        assert import_response.status_code == 200
        assert client.get("/api/v1/bing-webmaster-tools/metrics?query=audit", headers=headers).status_code == 200
        assert client.get("/api/v1/bing-webmaster-tools/crawl-stats?status=404", headers=headers).status_code == 200
        assert client.get("/api/v1/bing-webmaster-tools/sitemaps?status=OK", headers=headers).status_code == 200
        import_runs_response = client.get(
            "/api/v1/bing-webmaster-tools/import-runs?status=COMPLETED",
            headers=headers,
        )
        assert import_runs_response.status_code == 200
    finally:
        client.app.dependency_overrides.pop(bing_webmaster_tools.get_service, None)
