"""Tests for the AsyncOneMinClient — async HTTP transport with retry, error mapping,
and context manager support. All tests run with pytest-asyncio auto mode."""

import httpx
import pytest
import respx

from onemin._async_client import AsyncOneMinClient
from onemin._exceptions import (
    AuthenticationError,
    BadRequestError,
    ConnectionError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_client(api_key: str = "test-key-12345678", **kwargs) -> AsyncOneMinClient:
    """Create an AsyncOneMinClient with default test key."""
    return AsyncOneMinClient(api_key=api_key, **kwargs)


# ---------------------------------------------------------------------------
# Construction and configuration tests
# ---------------------------------------------------------------------------

async def test_async_client_accepts_same_kwargs():
    """AsyncOneMinClient accepts api_key, base_url, timeout, max_retries, base_delay."""
    client = AsyncOneMinClient(
        api_key="test-key-12345678",
        base_url="https://api.1min.ai",
        timeout=60.0,
        max_retries=3,
        base_delay=1.0,
    )
    assert client._api_key == "test-key-12345678"
    assert client._base_url == "https://api.1min.ai"
    assert client.timeout == 60.0
    assert client.max_retries == 3
    assert client.base_delay == 1.0
    await client.close()


async def test_async_client_env_var(monkeypatch):
    """AsyncOneMinClient reads API key from ONEMIN_API_KEY env var."""
    monkeypatch.setenv("ONEMIN_API_KEY", "env-test-key-abcd")
    client = AsyncOneMinClient()
    assert client._api_key == "env-test-key-abcd"
    await client.close()


async def test_async_client_missing_key_raises(monkeypatch):
    """AsyncOneMinClient raises AuthenticationError when no api_key provided."""
    monkeypatch.delenv("ONEMIN_API_KEY", raising=False)
    with pytest.raises(AuthenticationError):
        AsyncOneMinClient()


# ---------------------------------------------------------------------------
# Successful request tests
# ---------------------------------------------------------------------------

@respx.mock
async def test_get_request_returns_json():
    """async _request GET returns parsed JSON on 200."""
    respx.get("https://api.1min.ai/api/features").mock(
        return_value=httpx.Response(200, json={"features": ["image", "text"]})
    )
    client = make_client()
    result = await client._request("GET", "/api/features")
    assert result == {"features": ["image", "text"]}
    await client.close()


@respx.mock
async def test_post_request_returns_json():
    """async _request POST returns parsed JSON on 200."""
    respx.post("https://api.1min.ai/api/features").mock(
        return_value=httpx.Response(200, json={"result": "ok"})
    )
    client = make_client()
    result = await client._request("POST", "/api/features", json={"type": "TEXT_TO_TEXT"})
    assert result == {"result": "ok"}
    await client.close()


# ---------------------------------------------------------------------------
# HTTP error mapping tests
# ---------------------------------------------------------------------------

@respx.mock
async def test_401_raises_authentication_error():
    """async _request maps 401 to AuthenticationError."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    client = make_client(max_retries=0)
    with pytest.raises(AuthenticationError) as exc_info:
        await client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 401
    await client.close()


@respx.mock
async def test_429_raises_rate_limit_error():
    """async _request maps 429 (after retries exhausted) to RateLimitError."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(429, text="Too Many Requests")
    )
    client = make_client(max_retries=0)
    with pytest.raises(RateLimitError) as exc_info:
        await client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 429
    await client.close()


@respx.mock
async def test_404_raises_not_found_error():
    """async _request maps 404 to NotFoundError."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(404, text="Not Found")
    )
    client = make_client(max_retries=0)
    with pytest.raises(NotFoundError) as exc_info:
        await client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 404
    await client.close()


@respx.mock
async def test_400_raises_bad_request_error():
    """async _request maps 400 to BadRequestError."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(400, text="Bad Request")
    )
    client = make_client(max_retries=0)
    with pytest.raises(BadRequestError) as exc_info:
        await client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 400
    await client.close()


@respx.mock
async def test_500_raises_internal_server_error():
    """async _request maps 500 (after retries exhausted) to InternalServerError."""
    respx.post("https://api.1min.ai/api/test").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    client = make_client(max_retries=0)
    with pytest.raises(InternalServerError) as exc_info:
        await client._request("POST", "/api/test", json={})
    assert exc_info.value.status_code == 500
    await client.close()


# ---------------------------------------------------------------------------
# Retry behavior tests
# ---------------------------------------------------------------------------

@respx.mock
async def test_503_retried_up_to_max_retries():
    """async _request retries 503 up to max_retries times, then raises InternalServerError."""
    call_count = 0

    def side_effect(request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(503, text="Service Unavailable")

    respx.post("https://api.1min.ai/api/test").mock(side_effect=side_effect)
    client = make_client(max_retries=2, base_delay=0.01)
    with pytest.raises(InternalServerError):
        await client._request("POST", "/api/test", json={})
    # With max_retries=2: initial attempt + 2 retries = 3 total
    assert call_count == 3
    await client.close()


@respx.mock
async def test_401_not_retried():
    """async _request does NOT retry 401 (exactly 1 attempt)."""
    call_count = 0

    def side_effect(request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, text="Unauthorized")

    respx.post("https://api.1min.ai/api/test").mock(side_effect=side_effect)
    client = make_client(max_retries=2)
    with pytest.raises(AuthenticationError):
        await client._request("POST", "/api/test", json={})
    assert call_count == 1
    await client.close()


@respx.mock
async def test_403_not_retried():
    """async _request does NOT retry 403 (exactly 1 attempt)."""
    call_count = 0

    def side_effect(request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(403, text="Forbidden")

    respx.post("https://api.1min.ai/api/test").mock(side_effect=side_effect)
    client = make_client(max_retries=2)
    with pytest.raises(Exception):  # APIError for 403
        await client._request("POST", "/api/test", json={})
    assert call_count == 1
    await client.close()


# ---------------------------------------------------------------------------
# Network error tests
# ---------------------------------------------------------------------------

@respx.mock
async def test_timeout_raises_timeout_error():
    """httpx.TimeoutException must raise onemin.TimeoutError."""
    respx.post("https://api.1min.ai/api/test").mock(
        side_effect=httpx.TimeoutException("Request timed out")
    )
    client = make_client(max_retries=0)
    with pytest.raises(TimeoutError):
        await client._request("POST", "/api/test", json={})
    await client.close()


@respx.mock
async def test_connect_error_raises_connection_error():
    """httpx.ConnectError must raise onemin.ConnectionError."""
    respx.post("https://api.1min.ai/api/test").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    client = make_client(max_retries=0)
    with pytest.raises(ConnectionError):
        await client._request("POST", "/api/test", json={})
    await client.close()


# ---------------------------------------------------------------------------
# Context manager tests
# ---------------------------------------------------------------------------

@respx.mock
async def test_async_context_manager_closes_pool():
    """async with AsyncOneMinClient(...) as client: closes pool on exit."""
    respx.get("https://api.1min.ai/api/features").mock(
        return_value=httpx.Response(200, json={})
    )
    async with make_client() as client:
        assert client is not None
        await client._request("GET", "/api/features")
    # After exiting context manager, async http client should be closed
    assert client._http.is_closed


async def test_explicit_close_closes_pool():
    """await client.close() closes the underlying httpx.AsyncClient pool."""
    client = make_client()
    await client.close()
    assert client._http.is_closed


# ---------------------------------------------------------------------------
# API key redaction tests
# ---------------------------------------------------------------------------

async def test_repr_masks_key():
    """repr(async_client) must show masked key, not full key."""
    client = AsyncOneMinClient(api_key="test-key-12345678")
    r = repr(client)
    assert "test-key-12345678" not in r
    assert "test" in r
    assert "5678" in r
    assert "..." in r
    await client.close()


async def test_str_masks_key():
    """str(async_client) must not contain the full API key."""
    client = AsyncOneMinClient(api_key="test-key-12345678")
    assert "test-key-12345678" not in str(client)
    await client.close()
