"""Text domain resource for the 1min.ai API."""
from __future__ import annotations
from typing import Any, AsyncGenerator, Generator, TYPE_CHECKING

from onemin.resources._base_resource import BaseResource
from onemin.models import TextResult
from onemin._streaming import stream_sse
from onemin._constants import API_KEY_HEADER

if TYPE_CHECKING:
    from onemin._base_client import BaseOneMinClient


class TextResource(BaseResource):
    """Text generation and LLM chat operations. Domain timeout: 30s."""

    _domain = "text"

    def chat(
        self,
        prompt: str,
        *,
        model: str = "gpt-4o",
        stream: bool = False,
        web_search: bool = False,
        chat_history: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> TextResult | Generator[str, None, None]:
        """Send a chat/completion request to a language model.

        Args:
            prompt: The user message to send.
            model: Model name (e.g. 'gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro').
            stream: If True, returns a generator yielding token strings via SSE.
            web_search: Enable web search augmentation.
            chat_history: Previous messages as [{"role": "user"|"assistant", "message": "..."}].
            **kwargs: Extra fields merged into promptObject.

        Returns:
            TextResult (non-streaming) or Generator[str] (streaming).

        Example:
            result = client.text.chat("What is 2+2?")
            print(result.content)
        """
        prompt_object: dict[str, Any] = {
            "prompt": prompt,
            "isMixed": False,
            "webSearch": web_search,
            "chatList": chat_history or [],
            **kwargs,
        }
        payload: dict[str, Any] = {
            "type": "CHAT_WITH_AI",
            "model": model,
            "promptObject": prompt_object,
        }

        if stream:
            return self._stream_chat(payload)

        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
        return self._parse_text_result(response, model)

    def _stream_chat(self, payload: dict[str, Any]) -> Generator[str, None, None]:
        """Internal: stream chat via SSE."""
        url = f"{self._client._base_url}/api/features?isStreaming=true"
        headers = {API_KEY_HEADER: self._client._api_key}
        yield from stream_sse(
            self._client._client,
            url,
            headers=headers,
            json=payload,
            timeout=self._timeout,
        )

    async def achat(
        self,
        prompt: str,
        *,
        model: str = "gpt-4o",
        stream: bool = False,
        web_search: bool = False,
        chat_history: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> TextResult | AsyncGenerator[str, None]:
        """Send a chat/completion request to a language model asynchronously.

        Args:
            prompt: The user message to send.
            model: Model name (e.g. 'gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro').
                See ``Models.Text`` for all supported model names.
            stream: If True, returns an async generator yielding token strings via SSE.
            web_search: Enable web search augmentation.
            chat_history: Previous messages as [{"role": "user"|"assistant", "message": "..."}].
            **kwargs: Extra fields merged into promptObject.

        Returns:
            TextResult (non-streaming) or AsyncGenerator[str] (streaming).

        Example:
            result = await client.text.achat("What is 2+2?")
            print(result.content)
        """
        prompt_object: dict[str, Any] = {
            "prompt": prompt,
            "isMixed": False,
            "webSearch": web_search,
            "chatList": chat_history or [],
            **kwargs,
        }
        payload: dict[str, Any] = {
            "type": "CHAT_WITH_AI",
            "model": model,
            "promptObject": prompt_object,
        }

        if stream:
            return self._astream_chat(payload)

        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
        return self._parse_text_result(response, model)

    async def _astream_chat(self, payload: dict[str, Any]) -> AsyncGenerator[str, None]:
        """Internal: stream chat via async SSE."""
        from onemin._streaming import astream_sse
        url = f"{self._client._base_url}/api/features?isStreaming=true"
        headers = {API_KEY_HEADER: self._client._api_key}
        async for token in astream_sse(
            self._client._http,
            url,
            headers=headers,
            json=payload,
            timeout=self._timeout,
        ):
            yield token

    @staticmethod
    def _parse_text_result(response: dict[str, Any], model: str) -> TextResult:
        """Extract TextResult from API response."""
        ai_record = response.get("aiRecord", {})
        result_obj = ai_record.get("resultObject", {})
        content = (
            result_obj.get("message")
            or result_obj.get("content")
            or result_obj.get("text")
            or str(result_obj)
        )
        usage = result_obj.get("usage")
        return TextResult(content=content, model=model, usage=usage)
