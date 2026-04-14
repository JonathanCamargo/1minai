"""Tests for the 1min.ai SDK exception hierarchy."""

import re

import pytest

from onemin._exceptions import (
    OneMinError,
    APIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    BadRequestError,
    InternalServerError,
    ConnectionError,
    TimeoutError,
)


def test_one_min_error_is_exception():
    """OneMinError must be a subclass of Exception."""
    assert issubclass(OneMinError, Exception)


def test_api_error_has_status_code():
    """APIError must store status_code attribute."""
    err = APIError("Something went wrong", 500)
    assert err.status_code == 500


def test_api_error_has_request_id():
    """APIError must store request_id attribute."""
    err = APIError("Something went wrong", 500, request_id="req-abc123")
    assert err.request_id == "req-abc123"


def test_api_error_request_id_defaults_none():
    """APIError request_id should default to None."""
    err = APIError("Something went wrong", 500)
    assert err.request_id is None


def test_api_error_message_format():
    """APIError message format is 'HTTP {code}: {msg}'."""
    err = APIError("Bad gateway", 502)
    assert str(err) == "HTTP 502: Bad gateway"


def test_authentication_error_is_api_error():
    """AuthenticationError must be a subclass of APIError."""
    assert issubclass(AuthenticationError, APIError)


def test_rate_limit_error_is_api_error():
    """RateLimitError must be a subclass of APIError."""
    assert issubclass(RateLimitError, APIError)


def test_not_found_error_is_api_error():
    """NotFoundError must be a subclass of APIError."""
    assert issubclass(NotFoundError, APIError)


def test_bad_request_error_is_api_error():
    """BadRequestError must be a subclass of APIError."""
    assert issubclass(BadRequestError, APIError)


def test_internal_server_error_is_api_error():
    """InternalServerError must be a subclass of APIError."""
    assert issubclass(InternalServerError, APIError)


def test_connection_error_is_one_min_error():
    """ConnectionError must be a subclass of OneMinError."""
    assert issubclass(ConnectionError, OneMinError)


def test_connection_error_is_not_api_error():
    """ConnectionError must NOT be a subclass of APIError (per D-09)."""
    assert not issubclass(ConnectionError, APIError)


def test_timeout_error_is_connection_error():
    """TimeoutError must be a subclass of ConnectionError."""
    assert issubclass(TimeoutError, ConnectionError)


def test_timeout_error_is_not_api_error():
    """TimeoutError must NOT be a subclass of APIError (per D-09)."""
    assert not issubclass(TimeoutError, APIError)


def test_api_error_str_does_not_contain_api_key():
    """str(APIError) must not contain any API key pattern."""
    # Test with various potential key patterns
    for key_pattern in ["sk-test123456", "key-abcdefghij", "APIKEY12345"]:
        err = APIError("Request failed", 401)
        msg = str(err)
        # The message should not contain 'sk-' or 'key-' followed by alphanumerics
        assert not re.search(r"sk-[a-zA-Z0-9]+", msg)
        assert not re.search(r"key-[a-zA-Z0-9]+", msg)
        assert key_pattern not in msg


def test_all_api_errors_are_one_min_errors():
    """All APIError subclasses must also be OneMinError instances."""
    for exc_class in [
        AuthenticationError,
        RateLimitError,
        NotFoundError,
        BadRequestError,
        InternalServerError,
    ]:
        err = exc_class("Test error", 400)
        assert isinstance(err, OneMinError), f"{exc_class.__name__} must be OneMinError"
        assert isinstance(err, APIError), f"{exc_class.__name__} must be APIError"


def test_api_error_inheritance_chain():
    """Verify the full exception inheritance chain."""
    err = AuthenticationError("Unauthorized", 401, request_id="req-xyz")
    assert isinstance(err, AuthenticationError)
    assert isinstance(err, APIError)
    assert isinstance(err, OneMinError)
    assert isinstance(err, Exception)
    assert err.status_code == 401
    assert err.request_id == "req-xyz"
    assert str(err) == "HTTP 401: Unauthorized"
