from __future__ import annotations

import pytest

from paylio._error import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    PaylioError,
    RateLimitError,
)

ALL_SUBCLASSES = [
    APIError,
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    APIConnectionError,
]


class TestPaylioError:
    def test_message(self) -> None:
        err = PaylioError(message="something went wrong")
        assert str(err) == "something went wrong"
        assert err.message == "something went wrong"

    def test_all_attributes(self) -> None:
        err = PaylioError(
            message="bad",
            http_status=400,
            http_body='{"error":"bad"}',
            json_body={"error": "bad"},
            code="invalid",
            headers={"x-request-id": "req_123"},
        )
        assert err.message == "bad"
        assert err.http_status == 400
        assert err.http_body == '{"error":"bad"}'
        assert err.json_body == {"error": "bad"}
        assert err.code == "invalid"
        assert err.headers == {"x-request-id": "req_123"}

    def test_repr_format(self) -> None:
        err = PaylioError(message="fail", http_status=500, code="internal")
        r = repr(err)
        assert r == ("PaylioError(message='fail', http_status=500, code='internal')")

    def test_defaults(self) -> None:
        err = PaylioError()
        assert err.message == ""
        assert err.http_status is None
        assert err.http_body is None
        assert err.json_body is None
        assert err.code is None
        assert err.headers == {}

    def test_is_exception(self) -> None:
        err = PaylioError(message="test")
        assert isinstance(err, Exception)
        with pytest.raises(PaylioError, match="test"):
            raise err


class TestErrorSubclasses:
    """Each subclass inherits PaylioError and can carry all attributes."""

    @pytest.mark.parametrize("cls", ALL_SUBCLASSES)
    def test_subclass_is_paylio_error(self, cls: type[PaylioError]) -> None:
        assert issubclass(cls, PaylioError)

    @pytest.mark.parametrize("cls", ALL_SUBCLASSES)
    def test_subclass_catchable_as_paylio_error(self, cls: type[PaylioError]) -> None:
        with pytest.raises(PaylioError):
            raise cls(message="test")

    @pytest.mark.parametrize("cls", ALL_SUBCLASSES)
    def test_subclass_carries_all_attributes(self, cls: type[PaylioError]) -> None:
        err = cls(
            message="err",
            http_status=400,
            http_body="body",
            json_body={"k": "v"},
            headers={"h": "v"},
            code="c",
        )
        assert err.message == "err"
        assert err.http_status == 400
        assert err.http_body == "body"
        assert err.json_body == {"k": "v"}
        assert err.headers == {"h": "v"}
        assert err.code == "c"

    @pytest.mark.parametrize("cls", ALL_SUBCLASSES)
    def test_subclass_str_is_message(self, cls: type[PaylioError]) -> None:
        err = cls(message="hello")
        assert str(err) == "hello"
