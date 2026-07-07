"""Tests for Google Search Console routes."""

from datetime import UTC, date, datetime

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import google_search_console


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _property_payload(property_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": property_id,
        "website_id": None,
        "site_url": "https://example.com/",
        "property_type": "URL_PREFIX",
        "permission_level": "siteOwner",
        "status": "ACTIVE",
        "last_synced_at": None,
        "created_at": now,
        "updated_at": now,
    }


def _performance_payload(property_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": 1,
        "property_id": property_id,
        "date": date(2026, 7, 1).isoformat(),
        "page": "https://example.com/",
        "query": "example",
        "country": "fra",
        "device": "DESKTOP",
        "clicks": 10,
        "impressions": 100,
        "ctr": 0.1,
        "position": 2.4,
        "created_at": now,
        "updated_at": now,
    }


def _index_payload(property_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": 1,
        "property_id": property_id,
        "url": "https://example.com/",
        "coverage_state": "Indexed",
        "indexing_state": "INDEXING_ALLOWED",
        "verdict": "PASS",
        "page_fetch_state": None,
        "google_canonical": None,
        "user_canonical": None,
        "last_crawl_time": None,
        "inspected_at": None,
        "created_at": now,
        "updated_at": now,
    }


def _sitemap_payload(property_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": 1,
        "property_id": property_id,
        "sitemap_url": "https://example.com/sitemap.xml",
        "status": "OK",
        "last_submitted_at": None,
        "last_downloaded_at": None,
        "warnings": 0,
        "errors": 0,
        "contents": {},
        "created_at": now,
        "updated_at": now,
    }


def _import_payload(import_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": import_id,
        "property_id": 1,
        "import_type": "full",
        "status": "COMPLETED",
        "started_at": now,
        "finished_at": now,
        "items_processed": 3,
        "items_created": 3,
        "items_updated": 0,
        "items_skipped": 0,
        "error_message": None,
        "import_metadata": {},
        "created_at": now,
        "updated_at": now,
    }


class FakeGoogleSearchConsoleService:
    """Route service stub."""

    def list_properties(self, params: object) -> dict[str, object]:
        return {"items": [_property_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def create_property(self, payload: object) -> dict[str, object]:
        return _property_payload()

    def get_property(self, property_id: int) -> dict[str, object]:
        return _property_payload(property_id)

    def update_property(self, property_id: int, payload: object) -> dict[str, object]:
        return _property_payload(property_id)

    def list_performances(self, filters: object, params: object) -> dict[str, object]:
        return {"items": [_performance_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def list_index_coverages(self, filters: object, params: object) -> dict[str, object]:
        return {"items": [_index_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def list_sitemaps(self, filters: object, params: object) -> dict[str, object]:
        return {"items": [_sitemap_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def run_import(self, payload: object) -> dict[str, object]:
        return _import_payload()

    def list_imports(self, filters: object, params: object) -> dict[str, object]:
        return {"items": [_import_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def get_import(self, import_id: int) -> dict[str, object]:
        return _import_payload(import_id)


def test_google_search_console_routes_reject_anonymous_user(client: TestClient) -> None:
    """Google Search Console routes require a JWT."""

    responses = [
        client.get("/api/v1/google-search-console/properties"),
        client.post("/api/v1/google-search-console/properties", json={"site_url": "https://example.com/"}),
        client.get("/api/v1/google-search-console/properties/1"),
        client.put("/api/v1/google-search-console/properties/1", json={"status": "INACTIVE"}),
        client.get("/api/v1/google-search-console/performances?property_id=1"),
        client.get("/api/v1/google-search-console/indexation?property_id=1"),
        client.get("/api/v1/google-search-console/sitemaps?property_id=1"),
        client.post("/api/v1/google-search-console/imports", json={"import_type": "full", "property_id": 1}),
        client.get("/api/v1/google-search-console/imports"),
        client.get("/api/v1/google-search-console/imports/1"),
    ]

    assert [response.status_code for response in responses] == [401] * len(responses)


def test_google_search_console_routes_allow_user_with_permissions(
    client: TestClient,
    auth_headers_for,
) -> None:
    """Google Search Console routes allow users with GSC read and write permissions."""

    client.app.dependency_overrides[google_search_console.get_service] = lambda: FakeGoogleSearchConsoleService()
    headers = auth_headers_for(permission_codes=["gsc.read", "gsc.write"])
    try:
        assert client.get("/api/v1/google-search-console/properties", headers=headers).status_code == 200
        create_response = client.post(
            "/api/v1/google-search-console/properties",
            headers=headers,
            json={"site_url": "https://example.com/"},
        )
        assert create_response.status_code == 201
        assert client.get("/api/v1/google-search-console/properties/1", headers=headers).status_code == 200
        assert client.put(
            "/api/v1/google-search-console/properties/1",
            headers=headers,
            json={"status": "INACTIVE"},
        ).status_code == 200
        assert (
            client.get("/api/v1/google-search-console/performances?property_id=1", headers=headers).status_code == 200
        )
        assert client.get("/api/v1/google-search-console/indexation?property_id=1", headers=headers).status_code == 200
        assert client.get("/api/v1/google-search-console/sitemaps?property_id=1", headers=headers).status_code == 200
        assert client.post(
            "/api/v1/google-search-console/imports",
            headers=headers,
            json={"import_type": "full", "property_id": 1},
        ).status_code == 200
        assert client.get("/api/v1/google-search-console/imports", headers=headers).status_code == 200
        assert client.get("/api/v1/google-search-console/imports/1", headers=headers).status_code == 200
    finally:
        client.app.dependency_overrides.pop(google_search_console.get_service, None)
