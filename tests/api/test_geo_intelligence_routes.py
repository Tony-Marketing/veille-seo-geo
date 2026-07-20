"""Tests for GEO Intelligence REST routes and permissions."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models import Website


def _payload(website_id: int) -> dict[str, object]:
    return {
        "observations": [
            {
                "website_id": website_id,
                "provider": "ChatGPT",
                "prompt": "Prompt",
                "entity": "Marque",
                "visibility_score": 25,
                "citation_count": 1,
                "source_count": 1,
                "ranking": 2,
                "answer_hash": "a" * 64,
                "captured_at": datetime(2026, 7, 20, 10, tzinfo=UTC).isoformat(),
            },
        ],
    }


def test_routes_apply_read_and_write_permissions(client: TestClient, auth_headers_for, db_session: Session) -> None:
    website = Website(name="Routes GEO", url="https://geo-routes.example", is_active=True)
    db_session.add(website)
    db_session.commit()
    read_headers = auth_headers_for(permission_codes=["geo.read"])
    write_headers = auth_headers_for(permission_codes=["geo.write"])

    assert client.get("/api/v1/geo-intelligence").status_code == 401
    assert client.get("/api/v1/geo-intelligence", headers=write_headers).status_code == 403
    forbidden_import = client.post(
        "/api/v1/geo-intelligence/import",
        headers=read_headers,
        json=_payload(website.id),
    )
    assert forbidden_import.status_code == 403

    imported = client.post(
        "/api/v1/geo-intelligence/import",
        headers=write_headers,
        json=_payload(website.id),
    )
    listing = client.get(
        "/api/v1/geo-intelligence?provider=CHATGPT&page=1&page_size=1&sort=visibility_score&order=desc",
        headers=read_headers,
    )

    assert imported.status_code == 201
    assert imported.json()["created"] == 1
    assert listing.status_code == 200
    assert listing.json()["items"][0]["provider"] == "chatgpt"
    for path in ("summary", "providers", "history"):
        assert client.get(f"/api/v1/geo-intelligence/{path}", headers=read_headers).status_code == 200


def test_routes_reject_invalid_score_and_sort(client: TestClient, auth_headers_for, db_session: Session) -> None:
    website = Website(name="Validation GEO", url="https://geo-validation.example", is_active=True)
    db_session.add(website)
    db_session.commit()
    write_headers = auth_headers_for(permission_codes=["geo.write"])
    read_headers = auth_headers_for(permission_codes=["geo.read"])
    payload = _payload(website.id)
    payload["observations"][0]["visibility_score"] = -1  # type: ignore[index]

    assert client.post("/api/v1/geo-intelligence/import", headers=write_headers, json=payload).status_code == 422
    assert client.get("/api/v1/geo-intelligence?sort=unknown", headers=read_headers).status_code == 422
