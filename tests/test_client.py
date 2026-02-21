from __future__ import annotations

import pytest

from paylio._client import PaylioClient
from paylio._error import AuthenticationError
from paylio.services._subscription_service import SubscriptionService


class TestInit:
    def test_with_api_key(self) -> None:
        client = PaylioClient("sk_live_test")
        assert client._api_key == "sk_live_test"
        client.close()

    def test_missing_api_key_raises(self) -> None:
        with pytest.raises(AuthenticationError, match="No API key provided"):
            PaylioClient("")

    def test_none_api_key_raises(self) -> None:
        with pytest.raises(AuthenticationError, match="No API key provided"):
            PaylioClient("")  # type: ignore[arg-type]

    def test_custom_base_url(self) -> None:
        client = PaylioClient("sk_test", base_url="https://custom.api.com/v1")
        assert client._http._base_url == "https://custom.api.com/v1"
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
