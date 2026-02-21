from __future__ import annotations

from paylio._error import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    PaylioError,
    RateLimitError,
)


class TestPaylioError:
    def test_message(self) -> None:
        err = PaylioError(message="something went wrong")
        assert str(err) == "something went wrong"
        assert err.message == "something went wrong"

    def test_attributes(self) -> None:
        err = PaylioError(
            message="bad",
            http_status=400,
            json_body={"error": {"code": "invalid"}},
            code="invalid",
            headers={"x-request-id": "req_123"},
        )
        assert err.http_status == 400
        assert err.json_body == {"error": {"code": "invalid"}}
        assert err.code == "invalid"
        assert err.headers == {"x-request-id": "req_123"}

    def test_repr(self) -> None:
        err = PaylioError(message="fail", http_status=500, code="internal")
        r = repr(err)
        assert "PaylioError" in r
        assert "fail" in r
        assert "500" in r

    def test_defaults(self) -> None:
        err = PaylioError()
        assert err.message == ""
        assert err.http_status is None
        assert err.json_body is None
        assert err.code is None
        assert err.headers == {}


class TestErrorHierarchy:
    def test_api_error_is_paylio_error(self) -> None:
        assert issubclass(APIError, PaylioError)

    def test_authentication_error_is_paylio_error(self) -> None:
        assert issubclass(AuthenticationError, PaylioError)

    def test_invalid_request_error_is_paylio_error(self) -> None:
        assert issubclass(InvalidRequestError, PaylioError)

    def test_not_found_error_is_paylio_error(self) -> None:
        assert issubclass(NotFoundError, PaylioError)

    def test_rate_limit_error_is_paylio_error(self) -> None:
        assert issubclass(RateLimitError, PaylioError)

    def test_api_connection_error_is_paylio_error(self) -> None:
        assert issubclass(APIConnectionError, PaylioError)

    def test_all_catchable_as_paylio_error(self) -> None:
        for cls in [
            APIError,
            AuthenticationError,
            InvalidRequestError,
            NotFoundError,
            RateLimitError,
            APIConnectionError,
        ]:
            try:
                raise cls(message="test")
            except PaylioError:
                pass  # expected
