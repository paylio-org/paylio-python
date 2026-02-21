from __future__ import annotations

from typing import Any

import httpx

from paylio._error import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    PaylioError,
    RateLimitError,
)
from paylio._version import VERSION

DEFAULT_BASE_URL = "https://api.paylio.pro/flying/v1"
DEFAULT_TIMEOUT = 30.0


class HTTPClient:
    """Low-level HTTP client wrapping httpx."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = http_client or httpx.Client(timeout=timeout)

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers = self._build_headers()

        try:
            response = self._client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
            )
        except httpx.ConnectError as e:
            raise APIConnectionError(message=f"Connection error: {e}") from None
        except httpx.TimeoutException as e:
            raise APIConnectionError(message=f"Request timed out: {e}") from None

        return self._handle_response(response)

    def _build_headers(self) -> dict[str, str]:
        return {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"paylio-python/{VERSION}",
        }

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        http_status = response.status_code
        http_body = response.text
        headers = dict(response.headers)

        try:
            json_body: dict[str, Any] | None = response.json()
        except Exception:
            json_body = None

        if 200 <= http_status < 300:
            if json_body is None:
                raise APIError(
                    message="Invalid JSON in response body",
                    http_status=http_status,
                    http_body=http_body,
                )
            return json_body

        # Extract error details — handle all backend response formats:
        #   {"error": {"code": "...", "message": "..."}}  (public API v1)
        #   {"error": "string"}                           (legacy API)
        #   {"detail": "string"}                          (FastAPI / dashboard)
        error_code = None
        error_message = http_body
        if json_body:
            err = json_body.get("error")
            if isinstance(err, dict):
                error_code = err.get("code")
                error_message = err.get("message", http_body)
            elif isinstance(err, str):
                error_message = err
            elif isinstance(json_body.get("detail"), str):
                error_message = json_body["detail"]

        error_cls = _error_class_for_status(http_status)
        raise error_cls(
            message=error_message,
            http_status=http_status,
            http_body=http_body,
            json_body=json_body,
            headers=headers,
            code=error_code,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()


def _error_class_for_status(status: int) -> type[PaylioError]:
    if status == 401:
        return AuthenticationError
    elif status == 400:
        return InvalidRequestError
    elif status == 404:
        return NotFoundError
    elif status == 429:
        return RateLimitError
    else:
        return APIError
