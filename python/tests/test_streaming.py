"""Tests for SSE streaming helpers: stream_sse and astream_sse.

Uses unittest.mock to patch httpx_sse.connect_sse / aconnect_sse at the module level,
simulating the SSE event iteration without real HTTP connections.
"""

import json
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, patch, AsyncMock

import pytest


# ---------------------------------------------------------------------------
# Helpers: mock SSE event and event source
# ---------------------------------------------------------------------------

@dataclass
class FakeSSE:
    """Minimal stand-in for httpx_sse.ServerSentEvent."""
    data: str
    event: str = "message"
    id: str = ""
    retry: int | None = None


def make_sync_event_source(events: list[FakeSSE]):
    """Create a mock context manager that yields a sync event source."""
    class FakeEventSource:
        def iter_sse(self) -> Generator[FakeSSE, None, None]:
            yield from events

    class FakeContextManager:
        def __enter__(self):
            return FakeEventSource()
        def __exit__(self, *args):
            pass

    return FakeContextManager()


def make_async_event_source(events: list[FakeSSE]):
    """Create a mock async context manager that yields an async event source."""
    class FakeAsyncEventSource:
        async def aiter_sse(self) -> AsyncGenerator[FakeSSE, None]:
            for event in events:
                yield event

    class FakeAsyncContextManager:
        async def __aenter__(self):
            return FakeAsyncEventSource()
        async def __aexit__(self, *args):
            pass

    return FakeAsyncContextManager()


# ---------------------------------------------------------------------------
# Tests for _extract_token
# ---------------------------------------------------------------------------

def test_extract_token_content_field():
    """_extract_token returns obj['content'] for /api/chat-with-ai content events."""
    from onemin._streaming import _extract_token
    obj = {"content": "Hello"}
    assert _extract_token(obj) == "Hello"


def test_extract_token_openai_delta_content():
    """_extract_token returns choices[0].delta.content for OpenAI-style payloads."""
    from onemin._streaming import _extract_token
    obj = {"choices": [{"delta": {"content": "Hello"}}]}
    assert _extract_token(obj) == "Hello"


def test_extract_token_simple_data_field():
    """_extract_token returns obj['data'] for simple format payloads."""
    from onemin._streaming import _extract_token
    obj = {"data": "world"}
    assert _extract_token(obj) == "world"


def test_extract_token_fallback_to_str():
    """_extract_token falls back to str(obj) for unrecognized payloads."""
    from onemin._streaming import _extract_token
    obj = {"unknown": "value"}
    result = _extract_token(obj)
    # Should be a string representation of the dict
    assert isinstance(result, str)
    assert len(result) > 0


def test_extract_token_empty_delta_content_falls_to_data():
    """_extract_token returns data field when choices delta content is empty."""
    from onemin._streaming import _extract_token
    obj = {"choices": [{"delta": {"content": ""}}], "data": "fallback"}
    # Empty content — should return data field
    result = _extract_token(obj)
    assert result == "fallback"


# ---------------------------------------------------------------------------
# Tests for stream_sse (sync)
# ---------------------------------------------------------------------------

def test_stream_sse_yields_tokens_from_three_events():
    """stream_sse yields one token string per valid SSE data event."""
    from onemin._streaming import stream_sse

    events = [
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "tok1"}}]})),
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "tok2"}}]})),
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "tok3"}}]})),
    ]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        tokens = list(stream_sse(
            client,
            "https://api.1min.ai/api/features?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "CHAT_WITH_AI"},
            timeout=30.0,
        ))

    assert tokens == ["tok1", "tok2", "tok3"]


def test_stream_sse_stops_on_done_sentinel():
    """stream_sse stops iteration when it encounters data: [DONE]."""
    from onemin._streaming import stream_sse

    events = [
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "tok1"}}]})),
        FakeSSE(data="[DONE]"),
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "tok2"}}]})),
    ]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        tokens = list(stream_sse(
            client,
            "https://api.1min.ai/api/features?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "CHAT_WITH_AI"},
            timeout=30.0,
        ))

    assert tokens == ["tok1"]


def test_stream_sse_handles_partial_json_across_chunk_boundary():
    """stream_sse accumulates buffer across chunk boundaries without crashing."""
    from onemin._streaming import stream_sse

    # Split a valid JSON object across two SSE events to simulate chunk boundary
    full_json = json.dumps({"choices": [{"delta": {"content": "merged"}}]})
    half = len(full_json) // 2
    part1 = full_json[:half]
    part2 = full_json[half:]

    events = [
        FakeSSE(data=part1),   # incomplete JSON
        FakeSSE(data=part2),   # completes the JSON
        FakeSSE(data="[DONE]"),
    ]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        tokens = list(stream_sse(
            client,
            "https://api.1min.ai/api/features?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "CHAT_WITH_AI"},
            timeout=30.0,
        ))

    assert tokens == ["merged"]


def test_stream_sse_raises_on_buffer_overflow():
    """stream_sse raises ValueError when buffer exceeds 1MB."""
    from onemin._streaming import stream_sse, MAX_BUFFER_SIZE

    # Single event with data longer than 1MB
    oversized_data = "x" * (MAX_BUFFER_SIZE + 1)
    events = [FakeSSE(data=oversized_data)]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        with pytest.raises(ValueError, match="SSE buffer overflow"):
            list(stream_sse(
                client,
                "https://api.1min.ai/api/features?isStreaming=true",
                headers={"API-KEY": "test"},
                json={"type": "CHAT_WITH_AI"},
                timeout=30.0,
            ))


def test_stream_sse_skips_non_data_sse_lines():
    """stream_sse skips empty data lines (SSE keepalives)."""
    from onemin._streaming import stream_sse

    events = [
        FakeSSE(data=""),  # empty data line (keepalive) — should be skipped
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "tok"}}]})),
        FakeSSE(data="[DONE]"),
    ]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        tokens = list(stream_sse(
            client,
            "https://api.1min.ai/api/features?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "CHAT_WITH_AI"},
            timeout=30.0,
        ))

    assert tokens == ["tok"]


def test_stream_sse_yields_content_field_payloads():
    """stream_sse yields tokens for /api/chat-with-ai content event payloads."""
    from onemin._streaming import stream_sse

    events = [
        FakeSSE(data=json.dumps({"content": "Hel"}), event="content"),
        FakeSSE(data=json.dumps({"content": "lo"}), event="content"),
        FakeSSE(data="[DONE]"),
    ]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        tokens = list(stream_sse(
            client,
            "https://api.1min.ai/api/chat-with-ai?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "UNIFY_CHAT_WITH_AI"},
            timeout=30.0,
        ))

    assert tokens == ["Hel", "lo"]


def test_stream_sse_skips_result_event():
    """stream_sse does not yield tokens for the 'result' event (final aiRecord)."""
    from onemin._streaming import stream_sse

    events = [
        FakeSSE(data=json.dumps({"content": "tok"}), event="content"),
        FakeSSE(data=json.dumps({"aiRecord": {"resultObject": ["tok"]}}), event="result"),
        FakeSSE(data="", event="done"),
    ]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        tokens = list(stream_sse(
            client,
            "https://api.1min.ai/api/chat-with-ai?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "UNIFY_CHAT_WITH_AI"},
            timeout=30.0,
        ))

    assert tokens == ["tok"]


def test_stream_sse_raises_on_error_event():
    """stream_sse raises APIError when the server emits an 'error' SSE event."""
    from onemin._streaming import stream_sse
    from onemin._exceptions import APIError

    events = [
        FakeSSE(data="model unavailable", event="error"),
    ]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        with pytest.raises(APIError):
            list(stream_sse(
                client,
                "https://api.1min.ai/api/chat-with-ai?isStreaming=true",
                headers={"API-KEY": "test"},
                json={"type": "UNIFY_CHAT_WITH_AI"},
                timeout=30.0,
            ))


def test_stream_sse_skips_empty_token():
    """stream_sse does not yield empty token strings."""
    from onemin._streaming import stream_sse

    events = [
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": ""}}]})),
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "real"}}]})),
        FakeSSE(data="[DONE]"),
    ]
    ctx = make_sync_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.Client)
    with patch("onemin._streaming.connect_sse", return_value=ctx):
        tokens = list(stream_sse(
            client,
            "https://api.1min.ai/api/features?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "CHAT_WITH_AI"},
            timeout=30.0,
        ))

    assert tokens == ["real"]


# ---------------------------------------------------------------------------
# Tests for astream_sse (async)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_astream_sse_yields_tokens():
    """astream_sse async generator yields tokens identically to sync stream_sse."""
    from onemin._streaming import astream_sse

    events = [
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "a1"}}]})),
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "a2"}}]})),
        FakeSSE(data="[DONE]"),
    ]
    ctx = make_async_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.AsyncClient)
    with patch("onemin._streaming.aconnect_sse", return_value=ctx):
        tokens = []
        async for tok in astream_sse(
            client,
            "https://api.1min.ai/api/features?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "CHAT_WITH_AI"},
            timeout=30.0,
        ):
            tokens.append(tok)

    assert tokens == ["a1", "a2"]


@pytest.mark.asyncio
async def test_astream_sse_stops_on_done_sentinel():
    """astream_sse stops iteration when it encounters [DONE]."""
    from onemin._streaming import astream_sse

    events = [
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "first"}}]})),
        FakeSSE(data="[DONE]"),
        FakeSSE(data=json.dumps({"choices": [{"delta": {"content": "after"}}]})),
    ]
    ctx = make_async_event_source(events)

    import httpx
    client = MagicMock(spec=httpx.AsyncClient)
    with patch("onemin._streaming.aconnect_sse", return_value=ctx):
        tokens = []
        async for tok in astream_sse(
            client,
            "https://api.1min.ai/api/features?isStreaming=true",
            headers={"API-KEY": "test"},
            json={"type": "CHAT_WITH_AI"},
            timeout=30.0,
        ):
            tokens.append(tok)

    assert tokens == ["first"]
