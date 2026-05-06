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
        num_of_site: int | None = None,
        max_word: int | None = None,
        **kwargs: Any,
    ) -> TextResult | Generator[str, None, None]:
        """Send a chat/completion request to a language model.

        Hits POST /api/chat-with-ai with type ``UNIFY_CHAT_WITH_AI`` -- the
        unified endpoint that replaces the legacy CHAT_WITH_IMAGE,
        CHAT_WITH_PDF, and CHAT_WITH_YOUTUBE_VIDEO feature types. Pass
        attachments via ``kwargs['attachments'] = {"images": [...], "files": [...]}``
        and history settings via ``kwargs['settings']`` to access the full
        promptObject schema documented at
        https://docs.1min.ai/docs/api/chat-with-ai-api.

        Args:
            prompt: The user message to send. Including a YouTube URL in the
                prompt triggers automatic transcript extraction (max 3 URLs).
            model: Model name (e.g. 'gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro').
            stream: If True, returns a generator yielding token strings via SSE.
            web_search: Enable web search augmentation.
            num_of_site: Optional override for the number of sites to query
                (only applied when web_search is True; default upstream is 3).
            max_word: Optional cap on words pulled from each site
                (only applied when web_search is True; default upstream is 1000).
            **kwargs: Extra fields merged into promptObject. Useful keys:
                ``conversationId``, ``attachments``, ``settings``,
                ``brandVoiceId``, ``metadata``.

        Returns:
            TextResult (non-streaming) or Generator[str] (streaming).

        Example:
            result = client.text.chat("What is 2+2?")
            print(result.content)
        """
        prompt_object: dict[str, Any] = {"prompt": prompt}
        if web_search:
            web_search_settings: dict[str, Any] = {"webSearch": True}
            if num_of_site is not None:
                web_search_settings["numOfSite"] = num_of_site
            if max_word is not None:
                web_search_settings["maxWord"] = max_word
            prompt_object["settings"] = {"webSearchSettings": web_search_settings}
        prompt_object.update(kwargs)

        payload: dict[str, Any] = {
            "type": "UNIFY_CHAT_WITH_AI",
            "model": model,
            "promptObject": prompt_object,
        }

        if stream:
            return self._stream_chat(payload)

        response = self._client._request(
            "POST", "/api/chat-with-ai", json=payload, timeout=self._timeout,
        )
        return self._parse_text_result(response, model)

    def _stream_chat(self, payload: dict[str, Any]) -> Generator[str, None, None]:
        """Internal: stream chat via SSE."""
        url = f"{self._client._base_url}/api/chat-with-ai?isStreaming=true"
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
        num_of_site: int | None = None,
        max_word: int | None = None,
        **kwargs: Any,
    ) -> TextResult | AsyncGenerator[str, None]:
        """Send a chat/completion request to a language model asynchronously.

        Args:
            prompt: The user message to send.
            model: Model name (e.g. 'gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro').
                See ``Models.Text`` for all supported model names.
            stream: If True, returns an async generator yielding token strings via SSE.
            web_search: Enable web search augmentation.
            num_of_site: Optional override for the number of sites to query
                (only applied when web_search is True).
            max_word: Optional cap on words pulled from each site
                (only applied when web_search is True).
            **kwargs: Extra fields merged into promptObject (e.g. ``conversationId``,
                ``attachments``, ``settings``, ``brandVoiceId``, ``metadata``).

        Returns:
            TextResult (non-streaming) or AsyncGenerator[str] (streaming).

        Example:
            result = await client.text.achat("What is 2+2?")
            print(result.content)
        """
        prompt_object: dict[str, Any] = {"prompt": prompt}
        if web_search:
            web_search_settings: dict[str, Any] = {"webSearch": True}
            if num_of_site is not None:
                web_search_settings["numOfSite"] = num_of_site
            if max_word is not None:
                web_search_settings["maxWord"] = max_word
            prompt_object["settings"] = {"webSearchSettings": web_search_settings}
        prompt_object.update(kwargs)

        payload: dict[str, Any] = {
            "type": "UNIFY_CHAT_WITH_AI",
            "model": model,
            "promptObject": prompt_object,
        }

        if stream:
            return self._astream_chat(payload)

        response = await self._client._request(
            "POST", "/api/chat-with-ai", json=payload, timeout=self._timeout,
        )
        return self._parse_text_result(response, model)

    async def _astream_chat(self, payload: dict[str, Any]) -> AsyncGenerator[str, None]:
        """Internal: stream chat via async SSE."""
        from onemin._streaming import astream_sse
        url = f"{self._client._base_url}/api/chat-with-ai?isStreaming=true"
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
        """Extract TextResult from API response.

        The /api/chat-with-ai endpoint nests the result at
        ``aiRecord.aiRecordDetail.resultObject`` (a list of strings). Older
        responses placed it at ``aiRecord.resultObject`` as a list or as a
        dict with ``message``/``content``/``text``. All shapes are handled.
        """
        ai_record = response.get("aiRecord", {})
        detail = ai_record.get("aiRecordDetail") or {}
        result_obj = detail.get("resultObject")
        if result_obj is None:
            result_obj = ai_record.get("resultObject")
        if isinstance(result_obj, list):
            content = "".join(str(c) for c in result_obj)
        elif isinstance(result_obj, dict):
            content = (
                result_obj.get("message")
                or result_obj.get("content")
                or result_obj.get("text")
                or str(result_obj)
            )
        else:
            content = "" if result_obj is None else str(result_obj)
        return TextResult(content=content, model=model)
