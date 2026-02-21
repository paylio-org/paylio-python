from __future__ import annotations

from paylio._paylio_object import PaylioObject


class Subscription(PaylioObject):
    """Represents a Paylio subscription."""

    OBJECT_NAME = "subscription"


class SubscriptionCancel(PaylioObject):
    """Represents a subscription cancellation response."""

    OBJECT_NAME = "subscription_cancel"


class SubscriptionHistoryItem(PaylioObject):
    """Represents a single item in subscription history."""

    OBJECT_NAME = "subscription_history_item"


class PaginatedList(PaylioObject):
    """Represents a paginated list response."""

    OBJECT_NAME = "list"

    @property
    def has_more(self) -> bool:
        """Whether there are more pages available."""
        page: int = self.get("page", 1)
        total_pages: int = self.get("total_pages", 1)
        return page < total_pages
