"""HTTP fetching component for the crawler engine."""

from dataclasses import dataclass, field
from time import perf_counter

import httpx


@dataclass(frozen=True)
class FetchResult:
    """HTTP fetch result normalized for the crawler engine."""

    requested_url: str
    final_url: str | None = None
    status_code: int | None = None
    content_type: str | None = None
    text: str = ""
    is_redirect: bool = False
    redirect_url: str | None = None
    redirect_count: int = 0
    response_time_ms: int | None = None
    error_message: str | None = None
    redirect_chain: list[str] = field(default_factory=list)

    @property
    def is_html(self) -> bool:
        """Return whether the response looks like HTML."""

        return bool(self.content_type and "text/html" in self.content_type.lower())


class HttpFetcher:
    """Download pages over HTTP with redirects and network errors normalized."""

    def __init__(self, *, timeout: float = 10.0, client: httpx.Client | None = None) -> None:
        self.timeout = timeout
        self.client = client

    def fetch(self, url: str) -> FetchResult:
        """Fetch one URL and return a normalized result."""

        started_at = perf_counter()
        try:
            if self.client is not None:
                response = self.client.get(url, follow_redirects=True)
            else:
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                    response = client.get(url)
        except httpx.TooManyRedirects as exc:
            return self._error_result(url, started_at, f"Trop de redirections : {exc}")
        except httpx.RequestError as exc:
            return self._error_result(url, started_at, str(exc))

        elapsed_ms = int((perf_counter() - started_at) * 1000)
        redirect_chain = [str(item.url) for item in response.history]
        if response.history:
            redirect_chain.append(str(response.url))

        return FetchResult(
            requested_url=url,
            final_url=str(response.url),
            status_code=response.status_code,
            content_type=response.headers.get("content-type"),
            text=response.text,
            is_redirect=bool(response.history),
            redirect_url=str(response.url) if response.history else None,
            redirect_count=len(response.history),
            response_time_ms=elapsed_ms,
            redirect_chain=redirect_chain,
        )

    def _error_result(self, url: str, started_at: float, message: str) -> FetchResult:
        elapsed_ms = int((perf_counter() - started_at) * 1000)
        return FetchResult(
            requested_url=url,
            final_url=url,
            response_time_ms=elapsed_ms,
            error_message=message,
        )

