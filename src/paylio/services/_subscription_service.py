from __future__ import annotations

from typing import Any

from paylio._http_client import HTTPClient
from paylio.resources._subscription import (
    PaginatedList,
    Subscription,
    SubscriptionCancel,
    SubscriptionHistoryItem,
)


class SubscriptionService:
    """Service for subscription-related API operations.

    Access via client.subscription:
        client.subscription.retrieve("user_123")
        client.subscription.list("user_123")
        client.subscription.cancel("sub_uuid")
    """

    def __init__(self, http_client: HTTPClient) -> None:
        self._http = http_client

    def retrieve(self, user_id: str) -> Subscription:
        """Get the current subscription for a user."""
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required")

        data = self._http.request("GET", f"/subscription/{user_id}")
        return Subscription(data)

    def list(
        self,
        user_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedList:
        """Get subscription history for a user."""
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required")

        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }

        data = self._http.request(
            "GET",
            f"/users/{user_id}/subscriptions",
            params=params,
        )

        # Convert items to typed objects.
        if "items" in data:
            data["items"] = [SubscriptionHistoryItem(item) for item in data["items"]]

        return PaginatedList(data)

    def cancel(
        self,
        subscription_id: str,
        *,
        cancel_now: bool = False,
    ) -> SubscriptionCancel:
        """Cancel a subscription.

        Args:
            subscription_id: The subscription UUID.
            cancel_now: If True, cancel immediately. If False (default),
                cancel at end of current billing period (safe default).
        """
        if not subscription_id or not subscription_id.strip():
            raise ValueError("subscription_id is required")

        data = self._http.request(
            "POST",
            f"/subscription/{subscription_id}/cancel",
            json_body={"cancel_at_period_end": not cancel_now},
        )
        return SubscriptionCancel(data)
