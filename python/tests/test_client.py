"""Tests for the 1min.ai SDK base client with auth, retry, timeout, and key redaction."""

import os
import time

import httpx
import pytest
import respx

import onemin
from onemin._exceptions import (
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    BadRequestError,
    InternalServerError,
    ConnectionError,
    TimeoutError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_client(api_key: str = "test-key-12345678", **kwargs):
    """Create a OneMinClient with default test key."""
    from onemin import OneMinClient
    return OneMinClient(api_key=api_key, **kwargs)


# ---------------------------------------------------------------------------
# Authentication tests
# ---------------------------------------------------------------------------

def test_auth_from_constructor():
    """Client can be created with api_key passed directly to constructor."""
    from onemin import OneMinClient
    client = OneMinClient(api_key="test-key-12345678")
    assert client is not None
    client.close()


def test_auth_from_env_var(monkeypatch):
    """Client can be created using ONEMIN_API_KEY environment variable."""
    from onemin import OneMinClient
    monkeypatch.setenv("ONEMIN_API_KEY", "env-test-key")
    client = OneMinClient()
    assert client is not None
    client.close()


def test_auth_missing_raises(monkeypatch):
    """Constructor with no api_key and no env var must raise AuthenticationError."""
    from onemin import OneMinClient
    monkeypatch.delenv("ONEMIN_API_KEY", raising=False)
    with pytest.raises(AuthenticationError) as exc_info:
        OneMinClient()
    assert "ONEMIN_API_KEY" in str(exc_info.value)


def test_constructor_precedence_over_env(monkeypatch):
    """Constructor api_key takes precedence over ONEMIN_API_KEY env var (per D-06)."""
    from onemin import OneMinClient
    monkeypatch.setenv("ONEMIN_API_KEY", "env-key-that-should-not-be-used")
    client = OneMinClient(api_key="constructor-key-12345678")
    # The client should use constructor key, not env var.
    # We verify indirectly: repr should show constructor key's last 4 chars.
    assert "5678" in repr(client)
    client.close()


# ---------------------------------------------------------------------------
# Key redaction tests
# ---------------------------------------------------------------------------

def test_repr_masks_key():
    """repr(client) must show masked key like 'test...5678', not full key."""
    from onemin import OneMinClient
    client = OneMinClient(api_key="test-key-12345678")
    r = repr(client)
    assert "test-key-12345678" not in r
    # Should show first 4 chars and last 4 chars
    assert "test" in r
    assert "5678" in r
    assert "..." in r
    client.close()


def test_str_masks_key():
    """str(client) must not contain the full API key."""
    from onemin import OneMinClient
    client = OneMinClient(api_key="test-key-12345678")
    assert "test-key-12345678" not in str(client)
    client.close()


def test_repr_masks_short_key():
    """repr(client) must mask short keys as '***'."""
    from onemin import OneMinClient
    client = OneMinClient(api_key="short")
    r = repr(client)
    assert "short" not in r
    assert "***" in r
    client.close()


# ---------------------------------------------------------------------------
# HTTP error mapping tests
# ---------------------------------------------------------------------------

@respx.mock
def test_401_raises_authentication_error():
    """401 response must raise AuthenticationError with status_code=401."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    client = make_client()
    with pytest.raises(AuthenticationError) as exc_info:
        client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 401
    client.close()


@respx.mock
def test_429_raises_rate_limit_error():
    """429 response (after exhausted retries) must raise RateLimitError."""
    # Return 429 for every attempt so retries are exhausted
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(429, text="Too Many Requests")
    )
    client = make_client(max_retries=0)  # no retries to keep test fast
    with pytest.raises(RateLimitError) as exc_info:
        client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 429
    client.close()


@respx.mock
def test_404_raises_not_found_error():
    """404 response must raise NotFoundError with status_code=404."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(404, text="Not Found")
    )
    client = make_client()
    with pytest.raises(NotFoundError) as exc_info:
        client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 404
    client.close()


@respx.mock
def test_400_raises_bad_request_error():
    """400 response must raise BadRequestError with status_code=400."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(400, text="Bad Request")
    )
    client = make_client()
    with pytest.raises(BadRequestError) as exc_info:
        client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 400
    client.close()


@respx.mock
def test_500_raises_internal_server_error():
    """500 response (after exhausted retries) must raise InternalServerError."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    client = make_client(max_retries=0)  # no retries to keep test fast
    with pytest.raises(InternalServerError) as exc_info:
        client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 500
    client.close()


# ---------------------------------------------------------------------------
# Retry behavior tests
# ---------------------------------------------------------------------------

@respx.mock
def test_503_retried():
    """503 response must be retried; mock verifies 2+ attempts before raising."""
    call_count = 0

    def side_effect(request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(503, text="Service Unavailable")

    respx.post("https://api.1min.ai/api/test").mock(side_effect=side_effect)
    client = make_client(max_retries=2, base_delay=0.01)  # fast retries
    with pytest.raises(InternalServerError):
        client._request("POST", "/api/test", json={})
    # With max_retries=2, expect 3 total attempts (initial + 2 retries)
    assert call_count == 3
    client.close()


@respx.mock
def test_429_honors_retry_after():
    """429 with Retry-After header must honor the delay."""
    call_count = 0
    start_time = None

    def side_effect(request):
        nonlocal call_count, start_time
        call_count += 1
        if call_count == 1:
            start_time = time.monotonic()
            return httpx.Response(429, headers={"Retry-After": "0.1"}, text="Rate Limited")
        # Second call: return success
        return httpx.Response(200, json={"result": "ok"})

    respx.post("https://api.1min.ai/api/test").mock(side_effect=side_effect)
    client = make_client(max_retries=1, base_delay=0.01)
    result = client._request("POST", "/api/test", json={})
    elapsed = time.monotonic() - start_time
    # Should have waited at least 0.1 seconds (Retry-After value)
    assert elapsed >= 0.1
    assert call_count == 2
    client.close()


@respx.mock
def test_401_not_retried():
    """401 response must NOT be retried (exactly 1 attempt)."""
    call_count = 0

    def side_effect(request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, text="Unauthorized")

    respx.post("https://api.1min.ai/api/test").mock(side_effect=side_effect)
    client = make_client(max_retries=2)
    with pytest.raises(AuthenticationError):
        client._request("POST", "/api/test", json={})
    assert call_count == 1  # Must be exactly 1 attempt
    client.close()


@respx.mock
def test_403_not_retried():
    """403 response must NOT be retried (per D-11), exactly 1 attempt."""
    call_count = 0

    def side_effect(request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(403, text="Forbidden")

    respx.post("https://api.1min.ai/api/test").mock(side_effect=side_effect)
    client = make_client(max_retries=2)
    with pytest.raises(Exception):  # Raises APIError for 403
        client._request("POST", "/api/test", json={})
    assert call_count == 1  # Must be exactly 1 attempt
    client.close()


# ---------------------------------------------------------------------------
# Network error tests
# ---------------------------------------------------------------------------

@respx.mock
def test_timeout_raises_timeout_error():
    """httpx.TimeoutException must raise onemin.TimeoutError."""
    respx.post("https://api.1min.ai/api/test").mock(
        side_effect=httpx.TimeoutException("Request timed out")
    )
    client = make_client(max_retries=0)
    with pytest.raises(TimeoutError):
        client._request("POST", "/api/test", json={})
    client.close()


@respx.mock
def test_connection_error():
    """httpx.ConnectError must raise onemin.ConnectionError."""
    respx.post("https://api.1min.ai/api/test").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    client = make_client(max_retries=0)
    with pytest.raises(ConnectionError):
        client._request("POST", "/api/test", json={})
    client.close()


# ---------------------------------------------------------------------------
# Connection pooling tests
# ---------------------------------------------------------------------------

def test_single_httpx_client_instance():
    """Client must use a single httpx.Client instance (connection pooling)."""
    from onemin import OneMinClient
    client = OneMinClient(api_key="test-key-12345678")
    # Access _client twice; must be same object
    first = client._client
    second = client._client
    assert first is second
    assert isinstance(first, httpx.Client)
    client.close()


def test_close():
    """client.close() must close the underlying httpx.Client."""
    from onemin import OneMinClient
    client = OneMinClient(api_key="test-key-12345678")
    client.close()
    # After close, the httpx client should be closed (is_closed attribute)
    assert client._client.is_closed


def test_context_manager():
    """Client must work as a context manager."""
    from onemin import OneMinClient
    with OneMinClient(api_key="test-key-12345678") as client:
        assert client is not None
    # After context manager exit, httpx client should be closed
    assert client._client.is_closed


# ---------------------------------------------------------------------------
# Configurable parameters tests
# ---------------------------------------------------------------------------

def test_configurable_retry_params():
    """max_retries, timeout, base_delay must be configurable via constructor (per D-13)."""
    from onemin import OneMinClient
    client = OneMinClient(
        api_key="test-key-12345678",
        max_retries=5,
        timeout=60.0,
        base_delay=1.0,
    )
    assert client.max_retries == 5
    assert client.timeout == 60.0
    assert client.base_delay == 1.0
    client.close()


@respx.mock
def test_request_timeout_override():
    """_request must accept optional timeout parameter that overrides default."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(200, json={"result": "ok"})
    )
    from onemin import OneMinClient
    client = OneMinClient(api_key="test-key-12345678", timeout=30.0)
    # Pass explicit timeout override; should not raise
    result = client._request("POST", "/api/test", json={}, timeout=90.0)
    assert result == {"result": "ok"}
    client.close()
