from __future__ import annotations

import httpx

from paylio._error import AuthenticationError
from paylio._http_client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, HTTPClient
from paylio.services._subscription_service import SubscriptionService


class PaylioClient:
    """Client for the Paylio API.

    Usage:
        client = PaylioClient("sk_live_xxx")

        sub = client.subscription.retrieve("user_123")
        print(sub.status, sub.plan.name)

        history = client.subscription.list("user_123")
        for item in history.items:
            print(item.plan_name)

        result = client.subscription.cancel("sub_uuid")
        print(result.success)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise AuthenticationError(
                message=(
                    "No API key provided. Set your API key when creating "
                    "the PaylioClient: PaylioClient('sk_live_xxx')"
                ),
            )

        self._api_key = api_key
        self._http = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            http_client=http_client,
        )

        self.subscription = SubscriptionService(self._http)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> PaylioClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
