from __future__ import annotations

import httpx
import pytest

from paylio._client import PaylioClient
from paylio._error import AuthenticationError
from paylio._http_client import DEFAULT_BASE_URL
from paylio.services._subscription_service import SubscriptionService


class TestInit:
    def test_with_api_key(self) -> None:
        client = PaylioClient("sk_live_test")
        assert client._api_key == "sk_live_test"
        client.close()

    def test_empty_api_key_raises(self) -> None:
        with pytest.raises(AuthenticationError, match="No API key provided"):
            PaylioClient("")

    def test_none_api_key_raises(self) -> None:
        """None is falsy so it triggers the same guard."""
        with pytest.raises((AuthenticationError, TypeError)):
            PaylioClient(None)  # type: ignore[arg-type]

    def test_custom_base_url(self) -> None:
        client = PaylioClient("sk_test", base_url="https://custom.api.com/v1")
        assert client._http._base_url == "https://custom.api.com/v1"
        client.close()

    def test_default_base_url(self) -> None:
        client = PaylioClient("sk_test")
        assert client._http._base_url == DEFAULT_BASE_URL
        client.close()

    def test_custom_timeout(self) -> None:
        client = PaylioClient("sk_test", timeout=60.0)
        assert client._http._timeout == 60.0
        client.close()

    def test_custom_http_client(self) -> None:
        custom = httpx.Client(timeout=5.0)
        client = PaylioClient("sk_test", http_client=custom)
        assert client._http._client is custom
        client.close()


class TestSubscriptionService:
    def test_accessible(self) -> None:
        client = PaylioClient("sk_test")
        assert isinstance(client.subscription, SubscriptionService)
        client.close()


class TestContextManager:
    def test_with_statement(self) -> None:
        with PaylioClient("sk_test") as client:
            assert isinstance(client, PaylioClient)
            assert isinstance(client.subscription, SubscriptionService)

    def test_exit_closes_http(self) -> None:
        """__exit__ calls close() on the underlying HTTP client."""
        custom = httpx.Client(timeout=5.0)
        with PaylioClient("sk_test", http_client=custom):
            pass
        # After context manager exits, client is closed
        with pytest.raises(RuntimeError):
            custom.request("GET", "https://example.com")


class TestClose:
    def test_close_directly(self) -> None:
        custom = httpx.Client(timeout=5.0)
        client = PaylioClient("sk_test", http_client=custom)
        client.close()
        with pytest.raises(RuntimeError):
            custom.request("GET", "https://example.com")


class TestTopLevelImports:
    def test_import_client(self) -> None:
        from paylio import PaylioClient as PaylioClientImport

        assert PaylioClientImport is PaylioClient

    def test_import_errors(self) -> None:
        from paylio import (
            APIConnectionError,
            APIError,
            AuthenticationError,
            InvalidRequestError,
            NotFoundError,
            PaylioError,
            RateLimitError,
        )

        assert issubclass(APIError, PaylioError)
        assert issubclass(AuthenticationError, PaylioError)
        assert issubclass(InvalidRequestError, PaylioError)
        assert issubclass(NotFoundError, PaylioError)
        assert issubclass(RateLimitError, PaylioError)
        assert issubclass(APIConnectionError, PaylioError)

    def test_import_resources(self) -> None:
        from paylio import (
            PaginatedList,
            PaylioObject,
            Subscription,
            SubscriptionCancel,
            SubscriptionHistoryItem,
        )

        assert PaylioObject is not None
        assert Subscription is not None
        assert SubscriptionCancel is not None
        assert SubscriptionHistoryItem is not None
        assert PaginatedList is not None

    def test_version(self) -> None:
        import paylio

        assert paylio.__version__ == "0.1.2"

    def test_all_exports(self) -> None:
        import paylio

        for name in [
            "PaylioClient",
            "PaylioError",
            "APIError",
            "APIConnectionError",
            "AuthenticationError",
            "InvalidRequestError",
            "NotFoundError",
            "RateLimitError",
            "PaylioObject",
            "Subscription",
            "SubscriptionCancel",
            "SubscriptionHistoryItem",
            "PaginatedList",
        ]:
            assert name in paylio.__all__
