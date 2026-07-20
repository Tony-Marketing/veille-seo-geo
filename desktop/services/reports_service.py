"""Desktop adapter for the existing Reports CRUD REST endpoint."""

from dataclasses import dataclass
from typing import Any

from core.api_client import ApiClient, ApiClientError


@dataclass(frozen=True)
class PaginatedReports:
    """Paginated Reports payload consumed by the placeholder page."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class ReportsServiceError(RuntimeError):
    """Readable Reports REST error."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ReportsService:
    """Read existing Reports through ApiClient without generation or export logic."""

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_reports(self) -> PaginatedReports:
        try:
            payload = self.api_client.get("/reports", params={"page": 1, "page_size": 100})
        except ApiClientError as exc:
            raise ReportsServiceError("Chargement Reports impossible.", status_code=exc.status_code) from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise ReportsServiceError("Reponse Reports inattendue.")
        missing = {"total", "page", "page_size", "pages"} - payload.keys()
        if missing:
            raise ReportsServiceError("Reponse Reports incomplete.")
        return PaginatedReports(
            items=[item for item in payload["items"] if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )
