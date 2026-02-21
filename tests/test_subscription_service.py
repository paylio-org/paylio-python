from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from paylio._http_client import HTTPClient
from paylio.resources._subscription import (
    PaginatedList,
    Subscription,
    SubscriptionCancel,
    SubscriptionHistoryItem,
)
from paylio.services._subscription_service import SubscriptionService


@pytest.fixture
def mock_http() -> MagicMock:
    return MagicMock(spec=HTTPClient)


@pytest.fixture
def service(mock_http: MagicMock) -> SubscriptionService:
    return SubscriptionService(mock_http)


class TestRetrieve:
    def test_returns_subscription(self, service: SubscriptionService, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "id": "sub_123",
            "object": "subscription",
            "status": "active",
            "user_id": "user_1",
            "plan": {"slug": "pro-monthly", "name": "Pro Plan", "amount": 999, "currency": "usd"},
            "subscription_period": {"start": "2026-02-01T00:00:00Z", "end": "2026-03-01T00:00:00Z"},
            "cancel_at_period_end": False,
            "canceled_at": None,
            "provider": "stripe",
            "created_at": "2026-02-01T00:00:00Z",
        }

        sub = service.retrieve("user_1")

        assert isinstance(sub, Subscription)
        assert sub.id == "sub_123"
        assert sub.status == "active"
        assert sub.plan.name == "Pro Plan"
        assert sub.plan.amount == 999
        mock_http.request.assert_called_once_with("GET", "/subscription/user_1")

    def test_none_status(self, service: SubscriptionService, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "id": "",
            "object": "subscription",
            "status": "none",
            "user_id": "user_new",
        }
        sub = service.retrieve("user_new")
        assert sub.status == "none"

    def test_empty_user_id_raises(self, service: SubscriptionService) -> None:
        with pytest.raises(ValueError, match="user_id is required"):
            service.retrieve("")

    def test_whitespace_user_id_raises(self, service: SubscriptionService) -> None:
        with pytest.raises(ValueError, match="user_id is required"):
            service.retrieve("   ")


class TestList:
    def test_returns_paginated_list(
        self, service: SubscriptionService, mock_http: MagicMock
    ) -> None:
        mock_http.request.return_value = {
            "items": [
                {
                    "id": "sub_1",
                    "user_id": "user_1",
                    "plan_slug": "pro-monthly",
                    "plan_name": "Pro Plan",
                    "plan_amount": 999,
                    "plan_currency": "usd",
                    "plan_interval": "month",
                    "status": "active",
                    "current_period_start": "2026-02-01T00:00:00Z",
                    "current_period_end": "2026-03-01T00:00:00Z",
                    "created_at": "2026-02-01T00:00:00Z",
                },
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
        }

        result = service.list("user_1")

        assert isinstance(result, PaginatedList)
        assert len(result.items) == 1
        assert isinstance(result.items[0], SubscriptionHistoryItem)
        assert result.items[0].plan_name == "Pro Plan"
        assert result.total == 1
        assert result.has_more is False

    def test_pagination_params(self, service: SubscriptionService, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "items": [],
            "total": 0,
            "page": 2,
            "page_size": 10,
            "total_pages": 0,
        }
        service.list("user_1", page=2, page_size=10)
        mock_http.request.assert_called_once_with(
            "GET",
            "/users/user_1/subscriptions",
            params={"page": 2, "page_size": 10},
        )

    def test_has_more_true(self, service: SubscriptionService, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "items": [{"id": "s1"}],
            "total": 50,
            "page": 1,
            "page_size": 20,
            "total_pages": 3,
        }
        result = service.list("user_1")
        assert result.has_more is True

    def test_empty_user_id_raises(self, service: SubscriptionService) -> None:
        with pytest.raises(ValueError, match="user_id is required"):
            service.list("")

    def test_whitespace_user_id_raises(self, service: SubscriptionService) -> None:
        with pytest.raises(ValueError, match="user_id is required"):
            service.list("  ")

    def test_response_without_items_key(
        self, service: SubscriptionService, mock_http: MagicMock
    ) -> None:
        """Backend may return response without items key — should not crash."""
        mock_http.request.return_value = {
            "total": 0,
            "page": 1,
            "page_size": 20,
            "total_pages": 0,
        }
        result = service.list("user_1")
        assert isinstance(result, PaginatedList)
        assert result.total == 0

    def test_has_more_defaults_to_false_when_fields_missing(
        self, service: SubscriptionService, mock_http: MagicMock
    ) -> None:
        """has_more defaults to False when page/total_pages are missing."""
        mock_http.request.return_value = {"items": [], "total": 0}
        result = service.list("user_1")
        assert result.has_more is False


class TestCancel:
    def test_returns_subscription_cancel(
        self, service: SubscriptionService, mock_http: MagicMock
    ) -> None:
        mock_http.request.return_value = {
            "id": "sub_123",
            "object": "subscription_cancel",
            "success": True,
            "cancel_at_period_end": True,
        }

        result = service.cancel("sub_123")

        assert isinstance(result, SubscriptionCancel)
        assert result.success is True
        assert result.cancel_at_period_end is True
        mock_http.request.assert_called_once_with(
            "POST",
            "/subscription/sub_123/cancel",
            json_body={"cancel_at_period_end": True},
        )

    def test_cancel_now_true(self, service: SubscriptionService, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "id": "sub_123",
            "object": "subscription_cancel",
            "success": True,
            "cancel_at_period_end": False,
        }

        result = service.cancel("sub_123", cancel_now=True)

        assert result.cancel_at_period_end is False
        mock_http.request.assert_called_once_with(
            "POST",
            "/subscription/sub_123/cancel",
            json_body={"cancel_at_period_end": False},
        )

    def test_cancel_default_is_safe(
        self, service: SubscriptionService, mock_http: MagicMock
    ) -> None:
        """Default cancel_now=False means cancel_at_period_end=True (safe)."""
        mock_http.request.return_value = {"id": "s", "success": True, "cancel_at_period_end": True}
        service.cancel("sub_123")
        call_kwargs = mock_http.request.call_args
        assert call_kwargs[1]["json_body"]["cancel_at_period_end"] is True

    def test_empty_subscription_id_raises(self, service: SubscriptionService) -> None:
        with pytest.raises(ValueError, match="subscription_id is required"):
            service.cancel("")

    def test_whitespace_subscription_id_raises(self, service: SubscriptionService) -> None:
        with pytest.raises(ValueError, match="subscription_id is required"):
            service.cancel("  ")
