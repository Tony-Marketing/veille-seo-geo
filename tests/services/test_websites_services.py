"""Tests des services Websites."""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.websites import WebsiteCreate, WebsiteUpdate
from backend.app.services.websites import WebsiteService


def _service(db_session: Session) -> WebsiteService:
    return WebsiteService(WebsiteRepository(db_session))


def test_website_service_creates_website(db_session: Session) -> None:
    """The service creates a website."""

    result = _service(db_session).create(
        WebsiteCreate(name="Site Groupe", url="https://example.com", cms="WordPress"),
    )

    assert result.id is not None
    assert result.name == "Site Groupe"
    assert result.url == "https://example.com"
    assert result.cms == "WordPress"
    assert result.is_active is True


def test_website_service_rejects_duplicate_url(db_session: Session) -> None:
    """The service enforces URL uniqueness on creation."""

    service = _service(db_session)
    service.create(WebsiteCreate(name="Site A", url="https://duplicate.example.com"))

    with pytest.raises(HTTPException) as exc_info:
        service.create(WebsiteCreate(name="Site B", url="https://duplicate.example.com"))

    assert exc_info.value.status_code == 409


def test_website_service_updates_website(db_session: Session) -> None:
    """The service updates a website."""

    service = _service(db_session)
    created = service.create(WebsiteCreate(name="Site Groupe", url="https://example.com"))

    result = service.update(
        created.id,
        WebsiteUpdate(name="Site modifie", cms="Drupal", is_active=False),
    )

    assert result.id == created.id
    assert result.name == "Site modifie"
    assert result.cms == "Drupal"
    assert result.is_active is False


def test_website_service_rejects_duplicate_url_on_update(db_session: Session) -> None:
    """The service enforces URL uniqueness on update."""

    service = _service(db_session)
    first = service.create(WebsiteCreate(name="Site A", url="https://a.example.com"))
    second = service.create(WebsiteCreate(name="Site B", url="https://b.example.com"))

    with pytest.raises(HTTPException) as exc_info:
        service.update(second.id, WebsiteUpdate(url=first.url))

    assert exc_info.value.status_code == 409


def test_website_service_returns_404_for_unknown_resource(db_session: Session) -> None:
    """The service raises 404 for unknown resources."""

    with pytest.raises(HTTPException) as exc_info:
        _service(db_session).get(999)

    assert exc_info.value.status_code == 404


def test_website_service_lists_paginated_websites(db_session: Session) -> None:
    """The service returns paginated websites."""

    service = _service(db_session)
    service.create(WebsiteCreate(name="Site A", url="https://a.example.com"))
    service.create(WebsiteCreate(name="Site B", url="https://b.example.com"))
    service.create(WebsiteCreate(name="Site C", url="https://c.example.com"))

    result = service.list(PaginationParams(page=1, page_size=2))

    assert result.total == 3
    assert result.page == 1
    assert result.page_size == 2
    assert result.pages == 2
    assert len(result.items) == 2


def test_website_service_filters_active_and_inactive_websites(db_session: Session) -> None:
    """The service filters websites by active status."""

    service = _service(db_session)
    service.create(WebsiteCreate(name="Site actif", url="https://active.example.com", is_active=True))
    service.create(WebsiteCreate(name="Site inactif", url="https://inactive.example.com", is_active=False))

    active_result = service.list(PaginationParams(), is_active=True)
    inactive_result = service.list(PaginationParams(), is_active=False)

    assert active_result.total == 1
    assert active_result.items[0].is_active is True
    assert inactive_result.total == 1
    assert inactive_result.items[0].is_active is False
