"""Base HTTP client for the 1min.ai SDK.

Provides authentication, retry logic with exponential backoff and jitter,
per-request timeout overrides, connection pooling via a single shared httpx.Client
instance, and API key redaction in all public representations.
"""

import os
import random
import time
from typing import Any

import httpx

from onemin._constants import (
    API_KEY_HEADER,
    BASE_URL,
    DEFAULT_BASE_DELAY,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    RETRYABLE_STATUS_CODES,
)
from onemin._exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ConnectionError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
)


class BaseOneMinClient:
    """Base class providing HTTP transport with auth, retry, timeout, and connection pooling.

    Args:
        api_key: 1min.ai API key. Falls back to ONEMIN_API_KEY environment variable.
        base_url: Override the default API base URL.
        timeout: Default request timeout in seconds (default: 30).
        max_retries: Number of retries for retryable failures (default: 2).
        base_delay: Base delay in seconds for exponential backoff (default: 0.5).

    Raises:
        AuthenticationError: If no API key is provided and ONEMIN_API_KEY is not set.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY,
    ) -> None:
        # Auth resolution per D-06: constructor param > env var. No config file.
        resolved = api_key or os.environ.get("ONEMIN_API_KEY")
        if resolved is None:
            raise AuthenticationError(
                "No API key provided. Either pass api_key='...' to OneMinClient() "
                "or set the ONEMIN_API_KEY environment variable.",
                status_code=401,
            )
        self._api_key: str = resolved
        self._base_url: str = (base_url or BASE_URL).rstrip("/")
        self.timeout: float = timeout
        self.max_retries: int = max_retries
        self.base_delay: float = base_delay

        # Single shared httpx.Client instance for connection pooling (INFRA-08)
        self._client = httpx.Client(timeout=httpx.Timeout(timeout))

    def _mask_key(self) -> str:
        """Return a masked version of the API key for display purposes (per INFRA-09).

        Keys longer than 8 chars: show first 4 and last 4 chars with '...' in the middle.
        Shorter keys: return '***'.
        """
        key = self._api_key
        if len(key) > 8:
            return f"{key[:4]}...{key[-4:]}"
        return "***"

    def __repr__(self) -> str:
        """Return masked representation — API key is never exposed in full."""
        return f"OneMinClient(api_key='{self._mask_key()}', base_url='{self._base_url}')"

    def __str__(self) -> str:
        """Return same masked representation as __repr__."""
        return self.__repr__()

    def close(self) -> None:
        """Close the underlying httpx.Client and release connection pool resources."""
        self._client.close()

    def __enter__(self) -> "BaseOneMinClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _should_retry(self, status_code: int | None, attempt: int) -> bool:
        """Determine whether the request should be retried.

        Args:
            status_code: HTTP status code of the response, or None for network errors.
            attempt: Current attempt number (0-based).

        Returns:
            True if the request should be retried, False otherwise.
        """
        if attempt >= self.max_retries:
            return False
        if status_code is None:
            # Network-level error — retry
            return True
        return status_code in RETRYABLE_STATUS_CODES

    def _get_retry_delay(
        self,
        response: httpx.Response | None,
        attempt: int,
    ) -> float:
        """Calculate the delay before the next retry attempt.

        Honors the Retry-After header for 429 responses (per D-12).
        Otherwise uses exponential backoff with 30-50% jitter.

        Args:
            response: The HTTP response from the last attempt, or None.
            attempt: Current attempt number (0-based), used for backoff exponent.

        Returns:
            Number of seconds to sleep before the next attempt.
        """
        if response is not None and response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    return float(retry_after)
                except ValueError:
                    pass

        delay = self.base_delay * (2 ** attempt)
        jitter = delay * random.uniform(0.3, 0.5)
        return delay + jitter

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Map HTTP responses to typed exceptions or return parsed JSON.

        API key is never included in error messages (per D-10).

        Args:
            response: The HTTP response to process.

        Returns:
            Parsed JSON response body as a dict.

        Raises:
            AuthenticationError: For 401 responses.
            RateLimitError: For 429 responses.
            NotFoundError: For 404 responses.
            BadRequestError: For 400 responses.
            InternalServerError: For 5xx responses.
            APIError: For other non-success responses (including 403).
        """
        request_id: str | None = response.headers.get("x-request-id")

        if response.is_success:
            try:
                return response.json()
            except Exception:
                raise APIError(
                    f"Non-JSON response: {response.text[:200]}",
                    response.status_code,
                    request_id,
                )

        status = response.status_code

        if status == 401:
            raise AuthenticationError(response.text, 401, request_id)
        elif status == 403:
            # Forbidden — raise APIError, NOT retried per D-11
            raise APIError(response.text, 403, request_id)
        elif status == 429:
            raise RateLimitError(response.text, 429, request_id)
        elif status == 404:
            raise NotFoundError(response.text, 404, request_id)
        elif status == 400:
            raise BadRequestError(response.text, 400, request_id)
        elif status >= 500:
            raise InternalServerError(response.text, status, request_id)
        else:
            raise APIError(response.text, status, request_id)

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute an HTTP request with retry logic and error mapping.

        Args:
            method: HTTP method (e.g., 'POST', 'GET').
            path: API path (e.g., '/api/features'). Leading slash is normalized.
            timeout: Per-request timeout override in seconds. If None, uses self.timeout.
                     Domain resources use this to pass their domain-specific timeout
                     (e.g., 90s for image, 300s for video) per INFRA-07.
            **kwargs: Additional arguments passed to httpx.Client.request().

        Returns:
            Parsed JSON response as a dict.

        Raises:
            TimeoutError: If the request times out after all retry attempts.
            ConnectionError: For network-level connection failures.
            APIError (or subclass): For HTTP error responses after all retry attempts.
        """
        url = f"{self._base_url}/{path.lstrip('/')}"
        effective_timeout = timeout if timeout is not None else self.timeout

        # Build headers: merge API key header with any caller-provided headers
        base_headers: dict[str, str] = {
            API_KEY_HEADER: self._api_key,
            "Content-Type": "application/json",
        }
        extra_headers = kwargs.pop("headers", {})
        headers = {**base_headers, **extra_headers}

        last_response: httpx.Response | None = None
        total_attempts = self.max_retries + 1

        for attempt in range(total_attempts):
            if attempt > 0:
                delay = self._get_retry_delay(last_response, attempt - 1)
                time.sleep(delay)

            try:
                response = self._client.request(
                    method,
                    url,
                    headers=headers,
                    timeout=httpx.Timeout(effective_timeout),
                    **kwargs,
                )
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    last_response = None
                    continue
                raise TimeoutError(str(exc)) from exc
            except httpx.ConnectError as exc:
                # Connection errors are not retried (can't recover from refused connection)
                raise ConnectionError(str(exc)) from exc
            except httpx.RequestError as exc:
                raise ConnectionError(str(exc)) from exc

            if self._should_retry(response.status_code, attempt):
                last_response = response
                continue

            return self._handle_response(response)

        # Exhausted all attempts — handle the last response
        return self._handle_response(last_response)  # type: ignore[arg-type]
