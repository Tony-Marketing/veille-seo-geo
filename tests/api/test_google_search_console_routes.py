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
        "google_property_id": "sc-domain:example.com",
        "property_url": "sc-domain:example.com",
        "property_type": "DOMAIN",
        "display_name": "Example",
        "permission_level": "siteOwner",
        "is_active": True,
        "token_scopes": [],
        "token_expires_at": None,
        "created_at": now,
        "updated_at": now,
    }


def _import_payload(import_id: int = 1) -> dict[str, object]:
    now = _now()
    return {
        "id": import_id,
        "property_id": 1,
        "import_type": "MANUAL",
        "status": "COMPLETED",
        "start_date": date(2026, 7, 1).isoformat(),
        "end_date": date(2026, 7, 7).isoformat(),
        "dimensions": ["query", "page"],
        "rows_requested": 0,
        "rows_imported": 3,
        "error_message": None,
        "started_at": now,
        "completed_at": now,
        "created_at": now,
        "updated_at": now,
    }


class FakeGoogleSearchConsoleService:
    """Route service stub."""

    def __init__(self) -> None:
        self.performance_params = None
        self.performance_filters = None

    def list_properties(self, params: object) -> dict[str, object]:
        return {"items": [_property_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def list_remote_properties(self) -> list[dict[str, object]]:
        return [
            {
                "google_property_id": "sc-domain:example.com",
                "property_url": "sc-domain:example.com",
                "property_type": "DOMAIN",
            },
        ]

    def create_property(self, payload: object) -> dict[str, object]:
        return _property_payload()

    def get_property(self, property_id: int) -> dict[str, object]:
        return _property_payload(property_id)

    def update_property(self, property_id: int, payload: object) -> dict[str, object]:
        return _property_payload(property_id)

    def update_oauth_tokens(self, property_id: int, payload: object) -> dict[str, object]:
        return _property_payload(property_id)

    def delete_property(self, property_id: int) -> None:
        return None

    def list_performances(
        self,
        params: object,
        *,
        property_id: int | None = None,
        filters: object | None = None,
    ) -> dict[str, object]:
        self.performance_params = params
        self.performance_filters = filters
        now = _now()
        return {
            "items": [
                {
                    "id": 1,
                    "property_id": 1,
                    "import_id": 1,
                    "date": date(2026, 7, 1).isoformat(),
                    "query": "audit seo",
                    "page": "https://example.com/",
                    "country": None,
                    "device": None,
                    "search_type": "web",
                    "clicks": 10,
                    "impressions": 100,
                    "ctr": 0.1,
                    "position": 2.0,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }

    def list_index_coverages(self, params: object, *, property_id: int | None = None) -> dict[str, object]:
        now = _now()
        return {
            "items": [
                {
                    "id": 1,
                    "property_id": 1,
                    "import_id": 1,
                    "url": "https://example.com/",
                    "coverage_state": "INDEXED",
                    "google_state": None,
                    "indexing_state": None,
                    "page_fetch_state": None,
                    "robots_txt_state": None,
                    "verdict": "PASS",
                    "issue_type": None,
                    "sitemap": None,
                    "referring_urls": [],
                    "last_crawled_at": None,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }

    def list_sitemaps(self, params: object, *, property_id: int | None = None) -> dict[str, object]:
        now = _now()
        return {
            "items": [
                {
                    "id": 1,
                    "property_id": 1,
                    "import_id": 1,
                    "sitemap_url": "https://example.com/sitemap.xml",
                    "sitemap_type": "WEB",
                    "is_pending": False,
                    "is_sitemaps_index": False,
                    "submitted_at": None,
                    "last_downloaded_at": None,
                    "warnings": 0,
                    "errors": 0,
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

    def run_manual_import(self, payload: object) -> dict[str, object]:
        return _import_payload()

    def list_imports(self, params: object, *, property_id: int | None = None) -> dict[str, object]:
        return {"items": [_import_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}


def test_google_search_console_routes_reject_anonymous_user(client: TestClient) -> None:
    """Google Search Console routes require a JWT."""

    responses = [
        client.get("/api/v1/google-search-console/properties"),
        client.post("/api/v1/google-search-console/properties", json={}),
        client.get("/api/v1/google-search-console/properties/1"),
        client.get("/api/v1/google-search-console/performances"),
        client.get("/api/v1/google-search-console/indexation"),
        client.get("/api/v1/google-search-console/sitemaps"),
        client.post("/api/v1/google-search-console/imports/manual", json={}),
        client.get("/api/v1/google-search-console/imports"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401, 401, 401, 401]


def test_google_search_console_routes_allow_user_with_permissions(
    client: TestClient,
    auth_headers_for,
) -> None:
    """Google Search Console routes allow users with crawl read and write permissions."""

    fake_service = FakeGoogleSearchConsoleService()
    client.app.dependency_overrides[google_search_console.get_service] = lambda: fake_service
    headers = auth_headers_for(permission_codes=["crawl.read", "crawl.write"])
    try:
        assert client.get("/api/v1/google-search-console/properties", headers=headers).status_code == 200
        assert client.get("/api/v1/google-search-console/properties/remote", headers=headers).status_code == 200
        create_response = client.post(
            "/api/v1/google-search-console/properties",
            headers=headers,
            json={
                "google_property_id": "sc-domain:example.com",
                "property_url": "sc-domain:example.com",
                "property_type": "DOMAIN",
            },
        )
        assert create_response.status_code == 201
        assert client.get("/api/v1/google-search-console/properties/1", headers=headers).status_code == 200
        assert client.put("/api/v1/google-search-console/properties/1", headers=headers, json={}).status_code == 200
        oauth_response = client.put(
            "/api/v1/google-search-console/properties/1/oauth",
            headers=headers,
            json={"access_token": "access-token", "refresh_token": "refresh-token"},
        )
        assert oauth_response.status_code == 200
        performances_response = client.get(
            "/api/v1/google-search-console/performances",
            headers=headers,
            params={
                "start_date": "2026-07-01",
                "end_date": "2026-07-07",
                "page": "https://example.com/",
                "query": "audit seo",
                "country": "FRA",
                "device": "DESKTOP",
            },
        )
        assert performances_response.status_code == 200
        assert fake_service.performance_filters is not None
        assert fake_service.performance_filters.start_date == date(2026, 7, 1)
        assert fake_service.performance_filters.end_date == date(2026, 7, 7)
        assert fake_service.performance_filters.page == "https://example.com/"
        assert fake_service.performance_filters.query == "audit seo"
        assert fake_service.performance_filters.country == "FRA"
        assert fake_service.performance_filters.device == "DESKTOP"
        assert client.get("/api/v1/google-search-console/indexation", headers=headers).status_code == 200
        assert client.get("/api/v1/google-search-console/sitemaps", headers=headers).status_code == 200
        import_response = client.post(
            "/api/v1/google-search-console/imports/manual",
            headers=headers,
            json={
                "property_id": 1,
                "start_date": "2026-07-01",
                "end_date": "2026-07-07",
                "dimensions": ["query", "page"],
            },
        )
        assert import_response.status_code == 200
        assert client.get("/api/v1/google-search-console/imports", headers=headers).status_code == 200
        assert client.delete("/api/v1/google-search-console/properties/1", headers=headers).status_code == 204
    finally:
        client.app.dependency_overrides.pop(google_search_console.get_service, None)
