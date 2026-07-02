"""Tests for crawl routes."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.api.v1.routes import crawls


def _crawl_payload(crawl_id: int = 1, status: str = "PENDING") -> dict[str, object]:
    now = datetime.now(UTC).isoformat()
    return {
        "id": crawl_id,
        "website_id": None,
        "start_url": "https://example.com",
        "normalized_start_url": "https://example.com/",
        "status": status,
        "max_depth": 2,
        "max_pages": 100,
        "pages_found": 0,
        "pages_crawled": 0,
        "pages_failed": 0,
        "pending_urls": 0,
        "max_depth_reached": 0,
        "cancel_requested": False,
        "error_message": None,
        "started_at": None,
        "finished_at": None,
        "last_progress_at": None,
        "created_at": now,
        "updated_at": now,
    }


class FakeCrawlService:
    """Route service stub."""

    def list(self, params: object) -> dict[str, object]:
        return {"items": [_crawl_payload()], "total": 1, "page": 1, "page_size": 20, "pages": 1}

    def create(self, payload: object) -> dict[str, object]:
        return _crawl_payload()

    def get(self, crawl_id: int) -> dict[str, object]:
        return _crawl_payload(crawl_id)

    def start(self, crawl_id: int, payload: object | None = None) -> dict[str, object]:
        return _crawl_payload(crawl_id, "COMPLETED")

    def cancel(self, crawl_id: int) -> dict[str, object]:
        data = _crawl_payload(crawl_id, "CANCELLED")
        data["cancel_requested"] = True
        return data

    def list_pages(self, crawl_id: int, params: object) -> dict[str, object]:
        now = datetime.now(UTC).isoformat()
        return {
            "items": [
                {
                    "id": 1,
                    "crawl_session_id": crawl_id,
                    "website_id": None,
                    "url": "https://example.com",
                    "normalized_url": "https://example.com/",
                    "final_url": "https://example.com",
                    "final_normalized_url": "https://example.com/",
                    "depth": 0,
                    "status_code": 200,
                    "content_type": "text/html",
                    "is_redirect": False,
                    "redirect_url": None,
                    "redirect_count": 0,
                    "response_time_ms": 12,
                    "error_message": None,
                    "discovered_at": now,
                    "visited_at": now,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }


def test_crawl_routes_reject_anonymous_user(client: TestClient) -> None:
    """Crawl routes require a JWT."""

    responses = [
        client.get("/api/v1/crawls"),
        client.post("/api/v1/crawls", json={"start_url": "https://example.com"}),
        client.get("/api/v1/crawls/1"),
        client.post("/api/v1/crawls/1/start", json={}),
        client.post("/api/v1/crawls/1/cancel"),
        client.get("/api/v1/crawls/1/pages"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401, 401]


def test_crawl_routes_allow_user_with_permissions(
    client: TestClient,
    auth_headers_for,
) -> None:
    """Crawl routes allow users with crawl read and write permissions."""

    client.app.dependency_overrides[crawls.get_service] = lambda: FakeCrawlService()
    headers = auth_headers_for(permission_codes=["crawl.read", "crawl.write"])
    try:
        assert client.get("/api/v1/crawls", headers=headers).status_code == 200
        create_response = client.post(
            "/api/v1/crawls",
            headers=headers,
            json={"start_url": "https://example.com"},
        )
        assert create_response.status_code == 201
        assert client.get("/api/v1/crawls/1", headers=headers).status_code == 200
        assert client.post("/api/v1/crawls/1/start", headers=headers, json={}).status_code == 200
        assert client.post("/api/v1/crawls/1/cancel", headers=headers).status_code == 200
        assert client.get("/api/v1/crawls/1/pages", headers=headers).status_code == 200
    finally:
        client.app.dependency_overrides.pop(crawls.get_service, None)
