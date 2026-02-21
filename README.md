# Paylio Python SDK

Python client library for the [Paylio](https://paylio.pro) API.

## Installation

```bash
pip install paylio
```

## Usage

```python
import paylio

client = paylio.PaylioClient("sk_live_xxx")

# Get current subscription
sub = client.subscription.retrieve("user_123")
print(sub.status)       # "active"
print(sub.plan.name)    # "Pro Plan"
print(sub.plan.amount)  # 999

# List subscription history
history = client.subscription.list("user_123", page=1, page_size=10)
for item in history.items:
    print(item.plan_name, item.status)

if history.has_more:
    next_page = client.subscription.list("user_123", page=2)

# Cancel subscription (safe default: cancels at end of billing period)
result = client.subscription.cancel("subscription-uuid")
print(result.success)  # True

# Cancel immediately
result = client.subscription.cancel("subscription-uuid", cancel_now=True)
```

### Context Manager

```python
with paylio.PaylioClient("sk_live_xxx") as client:
    sub = client.subscription.retrieve("user_123")
```

### Custom Base URL

```python
client = paylio.PaylioClient("sk_test_xxx", base_url="https://api.paylio.pro/flying/v1")
```

### Error Handling

```python
import paylio

client = paylio.PaylioClient("sk_live_xxx")

try:
    sub = client.subscription.retrieve("user_123")
except paylio.AuthenticationError:
    print("Invalid API key")
except paylio.NotFoundError:
    print("Subscription not found")
except paylio.InvalidRequestError as e:
    print(f"Bad request: {e.message}")
except paylio.APIError as e:
    print(f"API error: {e.message} (status {e.http_status})")
except paylio.APIConnectionError:
    print("Network error")
```

## Requirements

- Python 3.9+
- [httpx](https://www.python-httpx.org/)
