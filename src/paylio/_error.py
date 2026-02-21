from __future__ import annotations

from typing import Any


class PaylioError(Exception):
    """Base error for all Paylio SDK errors."""

    def __init__(
        self,
        message: str | None = None,
        http_status: int | None = None,
        http_body: str | None = None,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message or ""
        self.http_status = http_status
        self.http_body = http_body
        self.json_body = json_body
        self.headers = headers or {}
        self.code = code

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(message={self.message!r}, "
            f"http_status={self.http_status}, code={self.code!r})"
        )


class APIError(PaylioError):
    """General API error (5xx or unexpected responses)."""


class AuthenticationError(PaylioError):
    """Invalid or missing API key (401)."""


class InvalidRequestError(PaylioError):
    """Bad request parameters (400)."""


class NotFoundError(PaylioError):
    """Resource not found (404)."""


class RateLimitError(PaylioError):
    """Rate limit exceeded (429)."""


class APIConnectionError(PaylioError):
    """Network/connection failure."""
