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
        assert req.headers["content-type"] == "application/json"
        assert req.headers["accept"] == "application/json"

    def test_sends_sdk_source(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"ok": True})
        client.request("GET", "/test")
        req = httpx_mock.get_request()
        assert req is not None
        assert req.headers["x-sdk-source"] == "python"


class TestSuccessResponse:
    def test_returns_parsed_json(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"id": "sub_123", "status": "active"})
        result = client.request("GET", "/subscription/user_1")
        assert result == {"id": "sub_123", "status": "active"}

    def test_success_with_invalid_json_raises_api_error(
        self, client: HTTPClient, httpx_mock: HTTPXMock
    ) -> None:
        """200 response with non-JSON body should raise APIError."""
        httpx_mock.add_response(status_code=200, text="not json")
        with pytest.raises(APIError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 200
        assert exc_info.value.message == "Invalid JSON in response body"
        assert exc_info.value.http_body == "not json"


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
        assert exc_info.value.message == "Bad key"
        expected_body = {"error": {"code": "invalid_api_key", "message": "Bad key"}}
        assert exc_info.value.json_body == expected_body
        assert isinstance(exc_info.value.headers, dict)

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
        assert exc_info.value.code == "missing_param"
        assert exc_info.value.message == "user_id required"

    def test_404_raises_not_found_error(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=404, json={"error": {"message": "Not found"}})
        with pytest.raises(NotFoundError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 404
        assert exc_info.value.message == "Not found"

    def test_429_raises_rate_limit_error(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=429, json={"error": {"message": "Too many requests"}})
        with pytest.raises(RateLimitError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 429
        assert exc_info.value.message == "Too many requests"

    def test_500_raises_api_error(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=500, json={"error": {"message": "Server error"}})
        with pytest.raises(APIError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 500
        assert exc_info.value.message == "Server error"

    def test_structured_error_body_parsed(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"code": "invalid_parameter", "message": "bad value"}},
        )
        with pytest.raises(InvalidRequestError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.code == "invalid_parameter"
        assert exc_info.value.message == "bad value"
        assert exc_info.value.http_body is not None

    def test_detail_error_body(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        """FastAPI {"detail": "string"} format is parsed correctly."""
        httpx_mock.add_response(status_code=400, json={"detail": "bad request"})
        with pytest.raises(InvalidRequestError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 400
        assert exc_info.value.message == "bad request"
        assert exc_info.value.code is None

    def test_string_error_body(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        """Legacy {"error": "string"} format is parsed correctly."""
        httpx_mock.add_response(status_code=401, json={"error": "unauthorized"})
        with pytest.raises(AuthenticationError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.message == "unauthorized"
        assert exc_info.value.code is None

    def test_error_with_non_json_body(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        """Error response with non-JSON body uses raw body as message."""
        httpx_mock.add_response(status_code=502, text="Bad Gateway")
        with pytest.raises(APIError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 502
        assert exc_info.value.message == "Bad Gateway"
        assert exc_info.value.json_body is None
        assert exc_info.value.code is None

    def test_error_with_unrecognised_json_body(
        self, client: HTTPClient, httpx_mock: HTTPXMock
    ) -> None:
        """Error JSON that doesn't match any known format falls back to raw body."""
        httpx_mock.add_response(status_code=500, json={"unexpected": "shape"})
        with pytest.raises(APIError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_status == 500
        assert exc_info.value.code is None
        # Falls back to raw http_body since no known error key matched
        assert "unexpected" in exc_info.value.message

    def test_error_preserves_http_body(self, client: HTTPClient, httpx_mock: HTTPXMock) -> None:
        """All error responses preserve the raw HTTP body."""
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"code": "bad", "message": "oops"}},
        )
        with pytest.raises(InvalidRequestError) as exc_info:
            client.request("GET", "/test")
        assert exc_info.value.http_body is not None
        assert "bad" in exc_info.value.http_body


class TestConnectionErrors:
    def test_connection_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_exception(httpx.ConnectError("connection refused"))
        client = HTTPClient(api_key="sk_test", base_url="https://api.test.com/v1")
        with pytest.raises(APIConnectionError) as exc_info:
            client.request("GET", "/test")
        assert "connection refused" in exc_info.value.message.lower()
        assert exc_info.value.__cause__ is None
        assert exc_info.value.http_status is None
        assert exc_info.value.http_body is None

    def test_timeout_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_exception(httpx.ReadTimeout("timed out"))
        client = HTTPClient(api_key="sk_test", base_url="https://api.test.com/v1")
        with pytest.raises(APIConnectionError) as exc_info:
            client.request("GET", "/test")
        assert "timed out" in exc_info.value.message.lower()
        assert exc_info.value.__cause__ is None
        assert exc_info.value.http_status is None


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

    def test_default_base_url(self, httpx_mock: HTTPXMock) -> None:
        from paylio._http_client import DEFAULT_BASE_URL

        c = HTTPClient(api_key="sk_test")
        assert c._base_url == DEFAULT_BASE_URL

    def test_custom_http_client(self) -> None:
        """Injected httpx.Client is used instead of creating a new one."""
        custom_client = httpx.Client(timeout=5.0)
        c = HTTPClient(api_key="sk_test", http_client=custom_client)
        assert c._client is custom_client
        custom_client.close()


class TestClose:
    def test_close_delegates_to_underlying_client(self) -> None:
        """close() delegates to the underlying httpx.Client.close()."""
        mock_httpx = httpx.Client(timeout=10.0)
        c = HTTPClient(api_key="sk_test", http_client=mock_httpx)
        c.close()
        # After closing, attempting a request should fail
        with pytest.raises(RuntimeError):
            mock_httpx.request("GET", "https://example.com")
