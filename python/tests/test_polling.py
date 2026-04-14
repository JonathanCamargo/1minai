"""Tests for the polling module — sync poll_job, async apoll_job, and completion detection.

Tests verify:
- is_job_complete with multiple completion patterns
- is_job_failed with failure status values
- poll_job returns result after polling (mocked HTTP)
- poll_job raises TimeoutError on deadline exceeded
- poll_job raises APIError immediately on failed job
- apoll_job mirrors sync behavior (async version)
- Linear backoff from 3s toward 10s max
"""

import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import respx

from onemin._exceptions import APIError, TimeoutError
from onemin._polling import (
    DEFAULT_MAX_WAIT,
    DEFAULT_POLL_INTERVAL,
    MAX_POLL_INTERVAL,
    POLL_BACKOFF_STEP,
    apoll_job,
    is_job_complete,
    is_job_failed,
    poll_job,
)


# ---------------------------------------------------------------------------
# is_job_complete tests
# ---------------------------------------------------------------------------


def test_is_job_complete_status_completed():
    """is_job_complete returns True when status == 'completed'."""
    assert is_job_complete({"status": "completed", "output": {"url": "http://example.com"}}) is True


def test_is_job_complete_status_done():
    """is_job_complete returns True when status == 'done'."""
    assert is_job_complete({"status": "done"}) is True


def test_is_job_complete_result_field():
    """is_job_complete returns True when result field is present and non-null."""
    assert is_job_complete({"result": "http://example.com/image.png"}) is True


def test_is_job_complete_output_field():
    """is_job_complete returns True when output field is present and non-null."""
    assert is_job_complete({"output": {"url": "http://example.com"}}) is True


def test_is_job_complete_processing_returns_false():
    """is_job_complete returns False when status == 'processing'."""
    assert is_job_complete({"status": "processing"}) is False


def test_is_job_complete_empty_dict_returns_false():
    """is_job_complete returns False for empty response."""
    assert is_job_complete({}) is False


def test_is_job_complete_null_result_returns_false():
    """is_job_complete returns False when result is explicitly null/None."""
    assert is_job_complete({"result": None, "status": "processing"}) is False


# ---------------------------------------------------------------------------
# is_job_failed tests
# ---------------------------------------------------------------------------


def test_is_job_failed_status_failed():
    """is_job_failed returns True when status == 'failed'."""
    assert is_job_failed({"status": "failed"}) is True


def test_is_job_failed_status_error():
    """is_job_failed returns True when status == 'error'."""
    assert is_job_failed({"status": "error"}) is True


def test_is_job_failed_status_cancelled():
    """is_job_failed returns True when status == 'cancelled'."""
    assert is_job_failed({"status": "cancelled"}) is True


def test_is_job_failed_processing_returns_false():
    """is_job_failed returns False when status == 'processing'."""
    assert is_job_failed({"status": "processing"}) is False


def test_is_job_failed_empty_returns_false():
    """is_job_failed returns False for empty response."""
    assert is_job_failed({}) is False


# ---------------------------------------------------------------------------
# poll_job sync tests (using respx to mock httpx.Client)
# ---------------------------------------------------------------------------

BASE_URL = "https://api.1min.ai"
JOB_ID = "test-job-123"
JOB_URL = f"{BASE_URL}/api/jobs/{JOB_ID}"


@respx.mock
@patch("time.sleep")
def test_poll_job_returns_result_after_two_polls(mock_sleep: MagicMock):
    """poll_job returns the completed response after two HTTP polls."""
    respx.get(JOB_URL).mock(
        side_effect=[
            httpx.Response(200, json={"status": "processing"}),
            httpx.Response(200, json={"status": "completed", "output": {"url": "http://img.com/1.png"}}),
        ]
    )
    client = httpx.Client()
    result = poll_job(client, BASE_URL, "test-api-key", JOB_ID, interval=0.01)
    assert result["status"] == "completed"
    assert result["output"]["url"] == "http://img.com/1.png"
    # sleep was called once (after first poll)
    mock_sleep.assert_called_once()
    client.close()


@respx.mock
@patch("time.sleep")
def test_poll_job_raises_timeout_error_on_deadline_exceeded(mock_sleep: MagicMock):
    """poll_job raises TimeoutError if max_wait is exceeded with no completion."""
    respx.get(JOB_URL).mock(return_value=httpx.Response(200, json={"status": "processing"}))
    client = httpx.Client()
    with pytest.raises(TimeoutError) as exc_info:
        poll_job(client, BASE_URL, "test-api-key", JOB_ID, interval=0.001, max_wait=0.005)
    assert JOB_ID in str(exc_info.value)
    client.close()


@respx.mock
@patch("time.sleep")
def test_poll_job_raises_api_error_on_failed_job(mock_sleep: MagicMock):
    """poll_job raises APIError immediately when job status is 'failed'."""
    respx.get(JOB_URL).mock(
        return_value=httpx.Response(200, json={"status": "failed", "error": "generation failed"})
    )
    client = httpx.Client()
    with pytest.raises(APIError) as exc_info:
        poll_job(client, BASE_URL, "test-api-key", JOB_ID)
    assert "generation failed" in str(exc_info.value) or JOB_ID in str(exc_info.value)
    # sleep should NOT be called — fail fast
    mock_sleep.assert_not_called()
    client.close()


@respx.mock
@patch("time.sleep")
def test_poll_job_includes_last_response_in_timeout_message(mock_sleep: MagicMock):
    """TimeoutError message from poll_job includes the last received response."""
    respx.get(JOB_URL).mock(
        return_value=httpx.Response(200, json={"status": "processing", "progress": 42})
    )
    client = httpx.Client()
    with pytest.raises(TimeoutError) as exc_info:
        poll_job(client, BASE_URL, "test-api-key", JOB_ID, interval=0.001, max_wait=0.005)
    # Last response data should appear in the error message
    assert "processing" in str(exc_info.value) or "42" in str(exc_info.value)
    client.close()


@respx.mock
@patch("time.sleep")
def test_poll_job_linear_backoff(mock_sleep: MagicMock):
    """poll_job interval increases linearly from starting value toward MAX_POLL_INTERVAL."""
    # Need enough responses to get 3 polls so we can check 2 sleep calls
    respx.get(JOB_URL).mock(
        side_effect=[
            httpx.Response(200, json={"status": "processing"}),
            httpx.Response(200, json={"status": "processing"}),
            httpx.Response(200, json={"status": "completed", "output": {}}),
        ]
    )
    client = httpx.Client()
    poll_job(client, BASE_URL, "test-api-key", JOB_ID, interval=3.0)
    assert mock_sleep.call_count == 2
    calls = [c.args[0] for c in mock_sleep.call_args_list]
    # First sleep: 3.0s, second sleep: 4.0s (3.0 + POLL_BACKOFF_STEP)
    assert calls[0] == pytest.approx(3.0)
    assert calls[1] == pytest.approx(3.0 + POLL_BACKOFF_STEP)
    client.close()


# ---------------------------------------------------------------------------
# apoll_job async tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
@patch("anyio.sleep", new_callable=AsyncMock)
async def test_apoll_job_returns_result_after_two_polls(mock_sleep: AsyncMock):
    """apoll_job returns the completed response after two HTTP polls."""
    respx.get(JOB_URL).mock(
        side_effect=[
            httpx.Response(200, json={"status": "processing"}),
            httpx.Response(200, json={"status": "completed", "output": {"url": "http://img.com/2.png"}}),
        ]
    )
    async with httpx.AsyncClient() as client:
        result = await apoll_job(client, BASE_URL, "test-api-key", JOB_ID, interval=0.01)
    assert result["status"] == "completed"
    mock_sleep.assert_called_once()


@pytest.mark.asyncio
@respx.mock
@patch("anyio.sleep", new_callable=AsyncMock)
async def test_apoll_job_raises_timeout_error_on_deadline_exceeded(mock_sleep: AsyncMock):
    """apoll_job raises TimeoutError if max_wait is exceeded."""
    respx.get(JOB_URL).mock(return_value=httpx.Response(200, json={"status": "processing"}))
    async with httpx.AsyncClient() as client:
        with pytest.raises(TimeoutError) as exc_info:
            await apoll_job(client, BASE_URL, "test-api-key", JOB_ID, interval=0.001, max_wait=0.005)
    assert JOB_ID in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
@patch("anyio.sleep", new_callable=AsyncMock)
async def test_apoll_job_raises_api_error_on_failed_job(mock_sleep: AsyncMock):
    """apoll_job raises APIError immediately when job status is 'failed'."""
    respx.get(JOB_URL).mock(
        return_value=httpx.Response(200, json={"status": "failed", "error": "async fail"})
    )
    async with httpx.AsyncClient() as client:
        with pytest.raises(APIError):
            await apoll_job(client, BASE_URL, "test-api-key", JOB_ID)
    mock_sleep.assert_not_called()


# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------


def test_default_poll_interval():
    """DEFAULT_POLL_INTERVAL should be 3.0 seconds."""
    assert DEFAULT_POLL_INTERVAL == 3.0


def test_max_poll_interval():
    """MAX_POLL_INTERVAL should be 10.0 seconds."""
    assert MAX_POLL_INTERVAL == 10.0


def test_default_max_wait():
    """DEFAULT_MAX_WAIT should be 300.0 seconds (5 minutes)."""
    assert DEFAULT_MAX_WAIT == 300.0


def test_poll_backoff_step():
    """POLL_BACKOFF_STEP should be 1.0 second."""
    assert POLL_BACKOFF_STEP == 1.0
