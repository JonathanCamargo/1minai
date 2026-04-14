"""Auto-polling for long-running jobs in the 1min.ai SDK.

Provides sync and async poll loops for jobs that return asynchronously —
e.g. Midjourney image generation, video creation. The poller takes a job ID,
polls GET /api/jobs/{id} at increasing intervals until a completion signal is
detected, then returns the final result dict.

Completion detection is flexible and handles multiple response shapes:
  - ``{"status": "completed", "output": {...}}`` — status-based completion
  - ``{"result": "http://..."}`` — result field present and non-null
  - ``{"output": {...}}`` — output field present and non-null

Usage (sync)::

    import httpx
    from onemin._polling import poll_job

    with httpx.Client() as client:
        result = poll_job(client, "https://api.1min.ai", api_key, job_id)

Usage (async)::

    import httpx
    from onemin._polling import apoll_job

    async with httpx.AsyncClient() as client:
        result = await apoll_job(client, "https://api.1min.ai", api_key, job_id)
"""

import time
from typing import Any

import anyio
import httpx

from onemin._constants import API_KEY_HEADER
from onemin._exceptions import APIError, TimeoutError

# ---------------------------------------------------------------------------
# Polling configuration defaults
# ---------------------------------------------------------------------------

DEFAULT_POLL_INTERVAL: float = 3.0     # seconds — starting interval
MAX_POLL_INTERVAL: float = 10.0        # seconds — cap on interval (linear backoff)
POLL_BACKOFF_STEP: float = 1.0         # seconds added per poll cycle
DEFAULT_MAX_WAIT: float = 300.0        # seconds (5 minutes, matches video timeout)

# ---------------------------------------------------------------------------
# Completion / failure status sets
# ---------------------------------------------------------------------------

_COMPLETE_STATUSES: frozenset[str] = frozenset({
    "completed", "complete", "done", "succeeded", "success",
})
_FAILED_STATUSES: frozenset[str] = frozenset({
    "failed", "error", "cancelled", "canceled",
})


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------


def is_job_complete(data: dict[str, Any]) -> bool:
    """Check if a job polling response indicates completion.

    Handles three patterns observed in 1min.ai job responses:
    1. ``status`` field set to a completion value (e.g. "completed", "done")
    2. ``result`` field is present and non-null
    3. ``output`` field is present and non-null

    Args:
        data: Parsed JSON response from GET /api/jobs/{id}.

    Returns:
        True if the job appears to be complete, False otherwise.
    """
    status = str(data.get("status", "")).lower()
    if status in _COMPLETE_STATUSES:
        return True
    if data.get("result") is not None:
        return True
    if data.get("output") is not None:
        return True
    return False


def is_job_failed(data: dict[str, Any]) -> bool:
    """Check if a job polling response indicates a failure.

    Args:
        data: Parsed JSON response from GET /api/jobs/{id}.

    Returns:
        True if the job has failed (should not keep polling), False otherwise.
    """
    status = str(data.get("status", "")).lower()
    return status in _FAILED_STATUSES


# ---------------------------------------------------------------------------
# Sync polling
# ---------------------------------------------------------------------------


def poll_job(
    client: httpx.Client,
    base_url: str,
    api_key: str,
    job_id: str,
    *,
    interval: float = DEFAULT_POLL_INTERVAL,
    max_wait: float = DEFAULT_MAX_WAIT,
) -> dict[str, Any]:
    """Sync: poll GET /api/jobs/{job_id} until the job completes or times out.

    Polls at ``interval`` seconds initially, increasing linearly by
    ``POLL_BACKOFF_STEP`` each cycle up to ``MAX_POLL_INTERVAL``.

    Args:
        client: An ``httpx.Client`` instance for making requests.
        base_url: API base URL (e.g. "https://api.1min.ai").
        api_key: 1min.ai API key for the ``API-KEY`` header.
        job_id: Job identifier returned by the job creation endpoint.
        interval: Starting poll interval in seconds (default: 3.0).
        max_wait: Maximum total wait time in seconds (default: 300.0).

    Returns:
        The final job response dict when the job completes.

    Raises:
        APIError: If the job status indicates failure (fail fast, no more polls).
        TimeoutError: If ``max_wait`` is exceeded without a completion signal.
    """
    deadline = time.monotonic() + max_wait
    current_interval = interval
    last_data: dict[str, Any] = {}

    while time.monotonic() < deadline:
        response = client.get(
            f"{base_url}/api/jobs/{job_id}",
            headers={API_KEY_HEADER: api_key},
            timeout=httpx.Timeout(30.0),
        )
        response.raise_for_status()
        last_data = response.json()

        if is_job_failed(last_data):
            error_msg = str(
                last_data.get("error", last_data.get("message", last_data))
            )
            raise APIError(f"Job {job_id} failed: {error_msg}", status_code=0)

        if is_job_complete(last_data):
            return last_data

        time.sleep(current_interval)
        current_interval = min(current_interval + POLL_BACKOFF_STEP, MAX_POLL_INTERVAL)

    raise TimeoutError(
        f"Job {job_id} did not complete within {max_wait}s. "
        f"Last response: {last_data}"
    )


# ---------------------------------------------------------------------------
# Async polling
# ---------------------------------------------------------------------------


async def apoll_job(
    client: httpx.AsyncClient,
    base_url: str,
    api_key: str,
    job_id: str,
    *,
    interval: float = DEFAULT_POLL_INTERVAL,
    max_wait: float = DEFAULT_MAX_WAIT,
) -> dict[str, Any]:
    """Async: poll GET /api/jobs/{job_id} until the job completes or times out.

    Mirrors ``poll_job`` but uses ``await anyio.sleep()`` for non-blocking waits,
    making it compatible with both asyncio and trio event loops.

    Args:
        client: An ``httpx.AsyncClient`` instance for making requests.
        base_url: API base URL (e.g. "https://api.1min.ai").
        api_key: 1min.ai API key for the ``API-KEY`` header.
        job_id: Job identifier returned by the job creation endpoint.
        interval: Starting poll interval in seconds (default: 3.0).
        max_wait: Maximum total wait time in seconds (default: 300.0).

    Returns:
        The final job response dict when the job completes.

    Raises:
        APIError: If the job status indicates failure (fail fast, no more polls).
        TimeoutError: If ``max_wait`` is exceeded without a completion signal.
    """
    deadline = time.monotonic() + max_wait
    current_interval = interval
    last_data: dict[str, Any] = {}

    while time.monotonic() < deadline:
        response = await client.get(
            f"{base_url}/api/jobs/{job_id}",
            headers={API_KEY_HEADER: api_key},
            timeout=httpx.Timeout(30.0),
        )
        response.raise_for_status()
        last_data = response.json()

        if is_job_failed(last_data):
            error_msg = str(
                last_data.get("error", last_data.get("message", last_data))
            )
            raise APIError(f"Job {job_id} failed: {error_msg}", status_code=0)

        if is_job_complete(last_data):
            return last_data

        await anyio.sleep(current_interval)
        current_interval = min(current_interval + POLL_BACKOFF_STEP, MAX_POLL_INTERVAL)

    raise TimeoutError(
        f"Job {job_id} did not complete within {max_wait}s. "
        f"Last response: {last_data}"
    )
