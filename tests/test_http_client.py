from __future__ import annotations

import httpx
import pytest
from pytest_httpx import HTTPXMock

from paylio._error import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
)
from paylio._http_client import HTTPClient


@pytest.fixture
def client(httpx_mock: HTTPXMock) -> HTTPClient:
    return HTTPClient(api_key="sk_test_abc", base_url="https://api.test.com/v1")


class TestHeaders:
    def test_sends_api_key(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"ok": True})
        client.request("GET", "/test")
        req = httpx_mock.get_request()
        assert req is not None
        assert req.headers["x-api-key"] == "sk_test_abc"

    def test_sends_user_agent(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"ok": True})
        client.request("GET", "/test")
        req = httpx_mock.get_request()
        assert req is not None
        assert "paylio-python/" in req.headers["user-agent"]

    def test_sends_content_type(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"ok": True})
        client.request("GET", "/test")
        req = httpx_mock.get_request()
        assert req is not None
        assert req.headers["accept"] == "application/json"


class TestSuccessResponse:
    def test_returns_parsed_json(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"id": "sub_123", "status": "active"})
        result = client.request("GET", "/subscription/user_1")
        assert result == {"id": "sub_123", "status": "active"}


class TestErrorMapping:
    def test_401_raises_authentication_error(
        self, client: HTTPClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(
            status_code=401,
            json={"error": {"code": "invalid_api_key", "message": "Bad key"}},
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 401
        assert exc_info.value.code == "invalid_api_key"
        assert "Bad key" in exc_info.value.message

    def test_400_raises_invalid_request_error(
        self, client: HTTPClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"code": "missing_param", "message": "user_id required"}},
        )
        with pytest.raises(InvalidRequestError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 400

    def test_404_raises_not_found_error(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=404, json={"error": {"message": "Not found"}})
        with pytest.raises(NotFoundError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 404

    def test_429_raises_rate_limit_error(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=429, json={"error": {"message": "Too many"}})
        with pytest.raises(RateLimitError):
            client.request("GET", "/test")

    def test_500_raises_api_error(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=500, json={"error": {"message": "Server error"}})
        with pytest.raises(APIError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 500

    def test_structured_error_body_parsed(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"code": "invalid_parameter", "message": "bad value"}},
        )
        with pytest.raises(InvalidRequestError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.code == "invalid_parameter"
        assert exc_info.value.message == "bad value"

    def test_plain_error_body(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=400, json={"detail": "bad request"})
        with pytest.raises(InvalidRequestError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 400


class TestConnectionErrors:
    def test_connection_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_exception(httpx.ConnectError("connection refused"))
        client = HTTPClient(api_key="sk_test", base_url="https://api.test.com/v1")
        with pytest.raises(APIConnectionError) as exc_info:
            client.request("GET", "/test")
        assert "connection refused" in exc_info.value.message.lower()

    def test_timeout_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_exception(httpx.ReadTimeout("timed out"))
        client = HTTPClient(api_key="sk_test", base_url="https://api.test.com/v1")
        with pytest.raises(APIConnectionError) as exc_info:
            client.request("GET", "/test")
        assert "timed out" in exc_info.value.message.lower()


class TestRequestBuilding:
    def test_get_with_query_params(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"items": []})
        client.request("GET", "/users/u1/subscriptions", params={"page": 1, "page_size": 10})
        req = httpx_mock.get_request()
        assert req is not None
        assert req.url.params["page"] == "1"
        assert req.url.params["page_size"] == "10"

    def test_post_with_json_body(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"success": True})
        client.request("POST", "/subscription/sub_1/cancel", json_body={"cancel_now": False})
        req = httpx_mock.get_request()
        assert req is not None
        import json

        body = json.loads(req.content)
        assert body == {"cancel_now": False}

    def test_custom_base_url(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"ok": True})
        c = HTTPClient(api_key="sk_test", base_url="https://custom.api.com/v2/")
        c.request("GET", "/ping")
        req = httpx_mock.get_request()
        assert req is not None
        assert str(req.url) == "https://custom.api.com/v2/ping"


class TestClose:
    def test_close(self, client: HTTPClient) -> None:
        client.close()
