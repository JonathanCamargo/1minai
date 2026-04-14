"""Async HTTP client for the 1min.ai SDK.

Provides the same auth, retry, error-mapping, and configuration as the sync
OneMinClient, but uses httpx.AsyncClient for non-blocking I/O. Suitable for
use in asyncio-based applications and in domain resources that need async
transport.

Usage:
    async with AsyncOneMinClient(api_key="...") as client:
        data = await client._request("POST", "/api/features", json={...})
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from onemin.resources.image import ImageResource
    from onemin.resources.text import TextResource
    from onemin.resources.audio import AudioResource
    from onemin.resources.video import VideoResource
    from onemin.resources.writing import WritingResource
    from onemin.resources.conversations import ConversationResource
    from onemin.resources.assets import AssetResource

import anyio
import httpx

from onemin._base_client import BaseOneMinClient
from onemin._constants import API_KEY_HEADER
from onemin._exceptions import (
    ConnectionError,
    TimeoutError,
)


class AsyncOneMinClient(BaseOneMinClient):
    """Async HTTP client for the 1min.ai API.

    Inherits auth resolution, config, retry logic, and error mapping from
    BaseOneMinClient. Overrides the transport layer with httpx.AsyncClient
    for non-blocking I/O with anyio.sleep() for retry backoff.

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
        timeout: float = 30.0,
        max_retries: int = 2,
        base_delay: float = 0.5,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            base_delay=base_delay,
        )
        # Close and discard the sync httpx.Client created by BaseOneMinClient —
        # we don't need it; the async client owns its own connection pool.
        self._client.close()
        del self._client

        # Own async connection pool
        self._http = httpx.AsyncClient(timeout=httpx.Timeout(timeout))

    def __repr__(self) -> str:
        """Return masked representation — API key is never exposed in full."""
        return f"AsyncOneMinClient(api_key='{self._mask_key()}', base_url='{self._base_url}')"

    def __str__(self) -> str:
        """Return same masked representation as __repr__."""
        return self.__repr__()

    async def close(self) -> None:
        """Close the underlying httpx.AsyncClient and release connection pool resources."""
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncOneMinClient":
        """Return self for use as an async context manager."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Close the connection pool on async context manager exit."""
        await self.close()

    # ------------------------------------------------------------------
    # Domain resource properties (lazy-initialized, same pattern as sync client)
    # ------------------------------------------------------------------

    @property
    def image(self) -> "ImageResource":
        """Image generation and editing resource."""
        if not hasattr(self, "_image"):
            from onemin.resources.image import ImageResource
            self._image = ImageResource(self)
        return self._image

    @property
    def text(self) -> "TextResource":
        """Text generation and LLM chat resource."""
        if not hasattr(self, "_text"):
            from onemin.resources.text import TextResource
            self._text = TextResource(self)
        return self._text

    @property
    def audio(self) -> "AudioResource":
        """Audio generation and processing resource."""
        if not hasattr(self, "_audio"):
            from onemin.resources.audio import AudioResource
            self._audio = AudioResource(self)
        return self._audio

    @property
    def video(self) -> "VideoResource":
        """Video generation resource."""
        if not hasattr(self, "_video"):
            from onemin.resources.video import VideoResource
            self._video = VideoResource(self)
        return self._video

    @property
    def writing(self) -> "WritingResource":
        """Writing assistance resource."""
        if not hasattr(self, "_writing"):
            from onemin.resources.writing import WritingResource
            self._writing = WritingResource(self)
        return self._writing

    @property
    def conversation(self) -> "ConversationResource":
        """Conversation management resource."""
        if not hasattr(self, "_conversation"):
            from onemin.resources.conversations import ConversationResource
            self._conversation = ConversationResource(self)
        return self._conversation

    @property
    def asset(self) -> "AssetResource":
        """Asset management resource."""
        if not hasattr(self, "_asset"):
            from onemin.resources.assets import AssetResource
            self._asset = AssetResource(self)
        return self._asset

    async def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute an async HTTP request with retry logic and error mapping.

        Mirrors the sync BaseOneMinClient._request() but uses await for I/O
        and anyio.sleep() for retry backoff (works with both asyncio and trio).

        Args:
            method: HTTP method (e.g., 'POST', 'GET').
            path: API path (e.g., '/api/features'). Leading slash is normalized.
            timeout: Per-request timeout override in seconds. If None, uses self.timeout.
                     Domain resources use this to pass their domain-specific timeout.
            **kwargs: Additional arguments passed to httpx.AsyncClient.request().

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
                await anyio.sleep(delay)

            try:
                response = await self._http.request(
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
