"""SSE streaming helpers for the 1min.ai SDK.

Provides sync and async generators that consume Server-Sent Events from the
1min.ai streaming endpoint (/api/features?isStreaming=true) and yield token
strings, handling:

- Partial JSON across SSE chunk boundaries (buffered accumulation)
- [DONE] sentinel termination
- Empty data lines (SSE keepalives)
- Buffer overflow protection (1MB cap to prevent OOM on malformed streams)

Usage (sync)::

    from onemin._streaming import stream_sse
    for token in stream_sse(client, url, headers=headers, json=body, timeout=30.0):
        print(token, end="", flush=True)

Usage (async)::

    from onemin._streaming import astream_sse
    async for token in astream_sse(async_client, url, headers=headers, json=body, timeout=30.0):
        print(token, end="", flush=True)
"""

import json as json_module
from typing import Any, AsyncGenerator, Generator

import httpx
from httpx_sse import connect_sse, aconnect_sse

MAX_BUFFER_SIZE = 1_048_576  # 1 MB — cap to prevent memory exhaustion on malformed data


def _extract_token(obj: dict[str, Any]) -> str:
    """Extract the token string from a parsed SSE JSON payload.

    Tries multiple known paths in order of priority:
    1. OpenAI-style: choices[0].delta.content
    2. Simple format: obj["data"]
    3. Fallback: str(obj)

    Args:
        obj: Parsed JSON object from an SSE data line.

    Returns:
        Extracted token string. May be empty if the delta contained no content.
    """
    # Try OpenAI-style: choices[0].delta.content
    choices = obj.get("choices")
    if choices and isinstance(choices, list) and len(choices) > 0:
        delta = choices[0].get("delta", {})
        content = delta.get("content", "")
        if content:
            return content
        # choices structure was present but content was empty — return empty
        # rather than falling through to data or fallback
        data = obj.get("data")
        if data:
            return str(data)
        return ""

    # Try simple format: obj["data"]
    data = obj.get("data")
    if data:
        return str(data)

    # Fallback: stringify the whole object
    return str(obj)


def stream_sse(
    client: httpx.Client,
    url: str,
    *,
    headers: dict[str, str],
    json: dict[str, Any],
    timeout: float,
) -> Generator[str, None, None]:
    """Sync SSE streaming generator.

    Opens a POST request to the given URL using httpx-sse, iterates SSE events,
    and yields individual token strings. Handles partial JSON across chunk
    boundaries by buffering incomplete data until a valid JSON object can be parsed.

    Args:
        client: Shared httpx.Client instance (from BaseOneMinClient._client).
        url: Full URL including query string (e.g., /api/features?isStreaming=true).
        headers: Request headers (must include API-KEY).
        json: Request body as a Python dict (serialized to JSON for the request).
        timeout: Request timeout in seconds.

    Yields:
        Individual token strings extracted from SSE data events.

    Raises:
        ValueError: If the accumulated buffer exceeds MAX_BUFFER_SIZE (1MB),
                    indicating malformed or excessively long SSE data.
    """
    data_buffer = ""

    with connect_sse(client, "POST", url, headers=headers, json=json, timeout=httpx.Timeout(timeout)) as event_source:
        for sse in event_source.iter_sse():
            # [DONE] sentinel signals end of stream
            if sse.data == "[DONE]":
                return

            # Skip empty data lines (SSE keepalives per spec)
            if not sse.data:
                continue

            # Accumulate data (handles partial JSON across chunk boundaries)
            data_buffer += sse.data

            # Guard against memory exhaustion from malformed streams
            if len(data_buffer) > MAX_BUFFER_SIZE:
                raise ValueError("SSE buffer overflow: exceeded 1MB")

            # Try to parse the buffered data as JSON
            try:
                obj = json_module.loads(data_buffer)
                data_buffer = ""  # Reset on successful parse
                token = _extract_token(obj)
                if token:
                    yield token
            except json_module.JSONDecodeError:
                # Incomplete JSON — continue accumulating
                continue


async def astream_sse(
    client: httpx.AsyncClient,
    url: str,
    *,
    headers: dict[str, str],
    json: dict[str, Any],
    timeout: float,
) -> AsyncGenerator[str, None]:
    """Async SSE streaming generator.

    Async equivalent of stream_sse. Uses httpx-sse aconnect_sse for async
    iteration. Identical logic to the sync version.

    Args:
        client: Shared httpx.AsyncClient instance.
        url: Full URL including query string (e.g., /api/features?isStreaming=true).
        headers: Request headers (must include API-KEY).
        json: Request body as a Python dict (serialized to JSON for the request).
        timeout: Request timeout in seconds.

    Yields:
        Individual token strings extracted from SSE data events.

    Raises:
        ValueError: If the accumulated buffer exceeds MAX_BUFFER_SIZE (1MB),
                    indicating malformed or excessively long SSE data.
    """
    data_buffer = ""

    async with aconnect_sse(client, "POST", url, headers=headers, json=json, timeout=httpx.Timeout(timeout)) as event_source:
        async for sse in event_source.aiter_sse():
            # [DONE] sentinel signals end of stream
            if sse.data == "[DONE]":
                return

            # Skip empty data lines (SSE keepalives per spec)
            if not sse.data:
                continue

            # Accumulate data (handles partial JSON across chunk boundaries)
            data_buffer += sse.data

            # Guard against memory exhaustion from malformed streams
            if len(data_buffer) > MAX_BUFFER_SIZE:
                raise ValueError("SSE buffer overflow: exceeded 1MB")

            # Try to parse the buffered data as JSON
            try:
                obj = json_module.loads(data_buffer)
                data_buffer = ""  # Reset on successful parse
                token = _extract_token(obj)
                if token:
                    yield token
            except json_module.JSONDecodeError:
                # Incomplete JSON — continue accumulating
                continue
