# Paylio Python SDK

[![PyPI version](https://img.shields.io/pypi/v/paylio.svg)](https://pypi.org/project/paylio/)
[![CI](https://github.com/paylio-org/paylio-python/actions/workflows/ci.yml/badge.svg)](https://github.com/paylio-org/paylio-python/actions/workflows/ci.yml)

The Paylio Python SDK provides convenient access to the Paylio API from applications written in Python.

## Documentation

See the [Paylio API docs](https://paylio.pro/docs).

## Requirements

- Python 3.9+

## Installation

```bash
pip install paylio
```

## Usage

```python
import paylio

client = paylio.PaylioClient("sk_live_xxx")

# Retrieve current subscription
sub = client.subscription.retrieve("user_123")
print(sub.status)       # "active"
print(sub.plan.name)    # "Pro Plan"
print(sub.plan.amount)  # 999
```

### List subscription history

```python
history = client.subscription.list("user_123", page=1, page_size=10)
for item in history.items:
    print(item.plan_name, item.status)

if history.has_more:
    next_page = client.subscription.list("user_123", page=2)
```

### Cancel a subscription

```python
# Cancel at end of billing period (safe default)
result = client.subscription.cancel("subscription_uuid")
print(result.success)  # True

# Cancel immediately
result = client.subscription.cancel("subscription_uuid", cancel_now=True)
```

### Context manager

```python
with paylio.PaylioClient("sk_live_xxx") as client:
    sub = client.subscription.retrieve("user_123")
```

### Configuration

```python
client = paylio.PaylioClient(
    "sk_live_xxx",
    base_url="https://api.paylio.pro/flying/v1",
)
```

### Error handling

```python
import paylio

client = paylio.PaylioClient("sk_live_xxx")

try:
    sub = client.subscription.retrieve("user_123")
except paylio.AuthenticationError:
    print("Invalid API key")
except paylio.NotFoundError:
    print("Subscription not found")
except paylio.RateLimitError:
    print("Rate limited, try again later")
except paylio.InvalidRequestError as e:
    print(f"Bad request: {e.message}")
except paylio.APIError as e:
    print(f"API error: {e.message} (status {e.http_status})")
except paylio.APIConnectionError:
    print("Network error")
```

## Error types

| Error | HTTP Status | Description |
|-------|-------------|-------------|
| `AuthenticationError` | 401 | Invalid or missing API key |
| `InvalidRequestError` | 400 | Bad request parameters |
| `NotFoundError` | 404 | Resource not found |
| `RateLimitError` | 429 | Rate limit exceeded |
| `APIError` | 5xx | Server error |
| `APIConnectionError` | — | Network or connection failure |

All errors inherit from `PaylioError`.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy .
```

## License

MIT
