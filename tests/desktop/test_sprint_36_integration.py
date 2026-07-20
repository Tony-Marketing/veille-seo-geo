"""Critical Desktop integration coverage for Sprint 36."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from core.session import DesktopSession
from PySide6.QtWidgets import QApplication
from services.bing_webmaster_tools_service import BingWebmasterToolsService
from services.reports_service import ReportsService
from services.seo_analysis_service import SeoAnalysisService
from ui.dialogs.crawl_dialog import CrawlDialog
from ui.dialogs.keyword_dialog import KeywordDialog


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    """Return a QApplication for context-prefill widget tests."""

    return QApplication.instance() or QApplication([])


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def _page(items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "items": items,
        "total": len(items),
        "page": 1,
        "page_size": 100,
        "pages": 1 if items else 0,
    }


def test_session_and_forms_preserve_website_entity_context(qt_app: QApplication) -> None:
    """The selected Website and Entity prefill the next Crawl and Keyword forms."""

    assert qt_app is not None
    session = DesktopSession()
    session.set_current_website({"id": 7, "entity_id": 3, "name": "Site Groupe"})
    crawl_dialog = CrawlDialog(default_website_id=session.current_website_id)
    keyword_dialog = KeywordDialog(default_entity_id=session.current_entity_id)

    assert crawl_dialog.website_id_input.text() == "7"
    assert keyword_dialog.entity_id_input.text() == "3"


def test_seo_analysis_adapter_uses_existing_rest_endpoints() -> None:
    """SEO Analysis remains a Desktop-to-ApiClient adapter without a backend contract change."""

    requests: list[tuple[str, str, dict[str, object] | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode()) if request.content else None
        requests.append((request.method, request.url.path, body))
        if request.method == "GET":
            return httpx.Response(200, json=_page([{"id": 9, "crawl_session_id": 4}]))
        return httpx.Response(200, json={"id": 9, "status": "COMPLETED"})

    service = SeoAnalysisService(_client(handler))

    assert service.list_analyses().items[0]["crawl_session_id"] == 4
    assert service.create_analysis(4)["id"] == 9
    assert service.run_analysis(9)["status"] == "COMPLETED"
    assert requests == [
        ("GET", "/api/v1/seo-analysis", None),
        ("POST", "/api/v1/seo-analysis", {"crawl_id": 4}),
        ("POST", "/api/v1/seo-analysis/9/run", None),
    ]


def test_bing_adapter_propagates_website_and_import_context() -> None:
    """Bing operations use backend REST endpoints and propagate the current Website filter."""

    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(200, json={"id": 12, "status": "SUCCEEDED"})
        return httpx.Response(200, json=_page([]))

    service = BingWebmasterToolsService(_client(handler))

    service.list_sites(website_id=7)
    service.list_metrics(website_id=7)
    result = service.run_manual_import(
        connection_id=2,
        bing_site_id=5,
        date_from="2026-07-01",
        date_to="2026-07-20",
    )

    assert requests[0].url.params["website_id"] == "7"
    assert requests[1].url.params["website_id"] == "7"
    assert requests[2].url.path == "/api/v1/bing-webmaster-tools/import"
    assert result["status"] == "SUCCEEDED"


def test_reports_adapter_only_reads_existing_crud_endpoint() -> None:
    """Reports integration stays limited to persisted CRUD data."""

    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=_page([{"id": 1, "entity_id": 3, "title": "Rapport"}]))

    reports = ReportsService(_client(handler)).list_reports()

    assert reports.items == [{"id": 1, "entity_id": 3, "title": "Rapport"}]
    assert [(request.method, request.url.path) for request in requests] == [("GET", "/api/v1/reports")]
